import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications.vgg19 import VGG19
import os
import tf2onnx
from loss import *
from glob import glob

def preprocess_image(image_path, img_size=(256, 256)):
    """Load and preprocess a single image."""
    image = tf.io.read_file(image_path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, img_size)
    image = (image / 127.5) - 1.0  # Normalize to [-1, 1]
    return image

def create_dataset(real_image_dir, anime_image_dir, batch_size=16, img_size=(256, 256)):
    """Create a tf.data.Dataset from image folders."""
    # Get image file paths
    real_image_paths = glob(os.path.join(real_image_dir, "*.jpg"))
    anime_image_paths = glob(os.path.join(anime_image_dir, "*.jpg"))

    # Create TensorFlow datasets
    real_images = tf.data.Dataset.from_tensor_slices(real_image_paths)
    anime_images = tf.data.Dataset.from_tensor_slices(anime_image_paths)

    # Preprocess images
    real_images = real_images.map(lambda x: preprocess_image(x, img_size), num_parallel_calls=tf.data.AUTOTUNE)
    anime_images = anime_images.map(lambda x: preprocess_image(x, img_size), num_parallel_calls=tf.data.AUTOTUNE)

    # Zip datasets together
    dataset = tf.data.Dataset.zip((real_images, anime_images))

    # Shuffle, batch, and prefetch
    dataset = dataset.shuffle(buffer_size=1000).batch(batch_size).prefetch(buffer_size=tf.data.AUTOTUNE)

    return dataset

class Ganaura(tf.keras.Model):
    def __init__(self, learning_rate=0.0002):
        super(Ganaura, self).__init__() 
        self.learning_rate = learning_rate

        # Remove fixed img_size; it will be dynamic
        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()

        self.gen_optimizer = tf.keras.optimizers.Adam(self.learning_rate, beta_1=0.5)
        self.dis_optimizer = tf.keras.optimizers.Adam(self.learning_rate, beta_1=0.5)

        self.checkpoint = tf.train.Checkpoint(
            generator=self.generator,
            discriminator=self.discriminator,
            gen_optimizer=self.gen_optimizer,
            dis_optimizer=self.dis_optimizer
        )

        self.vgg19 = self.create_vgg19_feature_extractor()

    def create_vgg19_feature_extractor(self):
        """
        Create a VGG19 feature extractor for perceptual losses.
        
        Returns:
            A Keras Model that extracts features from specified layers
        """
        # Load base VGG19 model without top layers
        base_model = VGG19(weights='imagenet', include_top=False)
        
        # Select specific layers for feature extraction
        layer_names = [
            'block1_conv2',   # Early layer for low-level features
            'block2_conv2',   # Mid-level features
            'block3_conv2',   # Higher-level features
            'block4_conv2',   # Even higher-level features
            'block5_conv2'    # Most abstract features
        ]
        
        # Create a model that outputs features from specified layers
        outputs = [base_model.get_layer(name).output for name in layer_names]
        
        # Create and return the feature extraction model
        return tf.keras.Model(inputs=base_model.input, outputs=outputs)

    def build_generator(self):
        # Use None for height and width to support dynamic sizes
        inputs = layers.Input(shape=(None, None, 3))

        # Encoder: Downsampling
        x = layers.Conv2D(64, (7, 7), padding='same', activation='relu')(inputs)
        x = layers.Conv2D(128, (3, 3), strides=2, padding='same', activation='relu')(x)
        x = layers.Conv2D(256, (3, 3), strides=2, padding='same', activation='relu')(x)

        # Residual blocks
        for _ in range(6):
            x = self.residual_block(x)

        # Decoder: Upsampling
        x = layers.Conv2DTranspose(128, (3, 3), strides=2, padding='same', activation='relu')(x)
        x = layers.Conv2DTranspose(64, (3, 3), strides=2, padding='same', activation='relu')(x)
        outputs = layers.Conv2D(3, (7, 7), padding='same', activation='tanh')(x)

        return tf.keras.Model(inputs, outputs, name="Generator")

    def build_discriminator(self):
        # Use None for height and width to support dynamic sizes
        inputs = layers.Input(shape=(None, None, 3))

        x = layers.Conv2D(64, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(inputs)
        x = layers.Conv2D(128, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(x)
        x = layers.Conv2D(256, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(x)
        x = layers.Conv2D(512, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(x)

        # Output size will vary with input size; no global pooling to keep it dynamic
        outputs = layers.Conv2D(1, (4, 4), padding='same', activation='sigmoid')(x)

        return tf.keras.Model(inputs, outputs, name="Discriminator")

    def residual_block(self, x):
        res = x
        x = layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
        x = layers.Conv2D(256, (3, 3), padding='same')(x)
        return layers.add([x, res])

    # Update train_step to handle dynamic sizes (example, adjust as needed)
    @tf.function
    def train_step(self, real_images, anime_images, config=None):
        """
        Comprehensive training step with multiple loss options
        
        Args:
            real_images: Input real images
            anime_images: Target anime-style images
            config: Configuration dictionary for loss weights and types
        """
        # Default configuration if not provided
        if config is None:
            config = {
                'adversarial_weight': 1.0,
                'content_weight': 10.0,
                'style_weight': 5.0,
                'l1_weight': 0.1,
                'region_smooth_weight': 0.1,
                'loss_type': 'standard'  # Can be 'standard', 'lsgan', 'modified'
            }

        with tf.GradientTape(persistent=True) as tape:
            # Generate fake anime images
            fake_anime_images = self.generator(real_images, training=True)
            
            # Get discriminator outputs
            real_output = self.discriminator(anime_images, training=True)
            fake_output = self.discriminator(fake_anime_images, training=True)

            # Compute different loss variants based on config
            if config['loss_type'] == 'standard':
                # Standard GAN loss
                adversarial_gen_loss = generator_loss(fake_output)
                adversarial_disc_loss = discriminator_loss(real_output, fake_output)
            
            elif config['loss_type'] == 'lsgan':
                # Least Squares GAN loss
                adversarial_gen_loss = generator_loss_m(fake_output)
                adversarial_disc_loss = discriminator_loss_m(real_output, fake_output)
            
            elif config['loss_type'] == 'modified':
                # Alternative discriminator loss
                adversarial_gen_loss = generator_loss_m(fake_output)
                adversarial_disc_loss = discriminator_loss_346(fake_output)

            # Content and style losses
            content_loss = con_loss(
                real_images, 
                fake_anime_images, 
                vgg19=self.vgg19, 
                weight=config['content_weight']
            )

            # Multi-layer style loss
            style_losses = style_loss_decentralization_3(
                anime_images, 
                fake_anime_images, 
                vgg19=self.vgg19, 
                weight=[1.0, 1.0, 1.0]
            )
            style_transfer_loss = sum(style_losses)

            # L1 loss for pixel-level similarity
            l1_loss = config['l1_weight'] * L1_loss(real_images, fake_anime_images)

            # Region smoothing loss
            region_smooth_loss = region_smoothing_loss(
                anime_images, 
                fake_anime_images, 
                vgg19=self.vgg19, 
                weight=config['region_smooth_weight']
            )

            # Combine all losses
            gen_loss = (
                config['adversarial_weight'] * adversarial_gen_loss + 
                content_loss + 
                config['style_weight'] * style_transfer_loss + 
                l1_loss + 
                region_smooth_loss
            )
            
            disc_loss = adversarial_disc_loss

        # Compute gradients
        gen_gradients = tape.gradient(gen_loss, self.generator.trainable_variables)
        disc_gradients = tape.gradient(disc_loss, self.discriminator.trainable_variables)

        # Apply gradients
        self.gen_optimizer.apply_gradients(zip(gen_gradients, self.generator.trainable_variables))
        self.dis_optimizer.apply_gradients(zip(disc_gradients, self.discriminator.trainable_variables))

        # Return losses for logging
        return {
            'generator_loss': gen_loss,
            'discriminator_loss': disc_loss,
            'adversarial_gen_loss': adversarial_gen_loss,
            'adversarial_disc_loss': adversarial_disc_loss,
            'content_loss': content_loss,
            'style_loss': style_transfer_loss,
            'l1_loss': l1_loss,
            'region_smooth_loss': region_smooth_loss
        }


    def generator_loss(self, fake_output, real_images, fake_images):
        adversarial_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.ones_like(fake_output), fake_output)
        content_loss = tf.reduce_mean(tf.abs(real_images - fake_images))
        return adversarial_loss + 10.0 * content_loss

    def discriminator_loss(self, real_output, fake_output):
        real_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.ones_like(real_output), real_output)
        fake_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.zeros_like(fake_output), fake_output)
        return real_loss + fake_loss

    def save_as_savedmodel(self, checkpoint_dir, export_dir="generator_savedmodel"):
        """Save the generator as a SavedModel."""
        tf.saved_model.save(self.generator, os.path.join(checkpoint_dir, export_dir))
        print(f"Generator SavedModel saved at: {os.path.join(checkpoint_dir, export_dir)}")

    def train(self, dataset, epochs, checkpoint_dir):
        for epoch in range(epochs):
            for step, (real_images, anime_images) in enumerate(dataset):
                losses = self.train_step(real_images, anime_images)
                if step % 100 == 0:
                    print(f"Epoch {epoch + 1}, Step {step}, Gen Loss: {losses['generator_loss']:.4f}, Disc Loss: {losses['discriminator_loss']:.4f}")
            if epoch % 10 == 0:
                self.checkpoint.save(file_prefix=os.path.join(checkpoint_dir, "ckpt"))
    
    def load(self, checkpoint_dir):
        """Load the model checkpoint."""
        checkpoint_path = os.path.join(checkpoint_dir, "ckpt-8")
        status = self.checkpoint.restore(checkpoint_path).expect_partial()
        status.assert_existing_objects_matched()  # Verify weights are loaded correctly
        print(f"Checkpoint loaded from: {checkpoint_path}")
    
    def save_to_h5_and_onnx(self, checkpoint_dir):
        """Load checkpoint, save as HDF5, and convert to ONNX."""
        # Load the checkpoint
        self.load(checkpoint_dir)
        
        # Test the model
        # dummy_input = tf.random.normal([1, *self.img_size])
        # output = self.generator(dummy_input, training=False)
        # print(f"Generator output shape: {output.shape}")

        # Save as HDF5
        h5_path = os.path.join(checkpoint_dir, "generator.h5")
        self.generator.save(h5_path)
        print(f"HDF5 model saved at: {h5_path}")

        # Load HDF5 and convert to ONNX
        loaded_model = tf.keras.models.load_model(h5_path)
        onnx_model_path = os.path.join(checkpoint_dir, "generator.onnx")
        onnx_model, _ = tf2onnx.convert.from_keras(
            loaded_model,
            input_signature=[tf.TensorSpec([None, None, None, 3], tf.float32, name='input_1')],
            opset=13
        )
        
        # Save the ONNX model
        with open(onnx_model_path, 'wb') as f:
            f.write(onnx_model.SerializeToString())
        print(f"ONNX model saved at: {onnx_model_path}")


# Main execution
if __name__ == "__main__":
    # Define directories
    real_dir = '/home/dilshad/Desktop/Ganfeb/dataset/train_photo'  # Replace with your real images directory
    anime_dir = '/home/dilshad/Desktop/Ganfeb/dataset/Hayao/style'  # Replace with your anime images directory
    checkpoint_dir = '/home/dilshad/Desktop/Ganfeb/new_checkpoints'
    os.makedirs(checkpoint_dir, exist_ok=True)
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)

    # Create dataset (target_size=None for dynamic sizes, or (256, 256) for fixed)
    dataset = create_dataset(real_dir, anime_dir, batch_size=4)

    # Initialize and train model
    gan = Ganaura(learning_rate=0.0002)
    print(len(dataset))
    # gan.train(dataset,10,checkpoint_dir)
    gan.save_to_h5_and_onnx('/home/dilshad/Desktop/Ganfeb/final_checkpoints')
    # gan.train(dataset, epochs=50, checkpoint_dir=checkpoint_dir)