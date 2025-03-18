import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import os

class Ganaura(tf.keras.Model):
    def __init__(self, img_size=(256, 256, 3), batch_size=16, learning_rate=0.0002):
        super(Ganaura, self).__init__() 

        self.img_size = img_size
        self.batch_size = batch_size
        self.learning_rate = learning_rate

        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()

        self.gen_optimizer = tf.keras.optimizers.Adam(self.learning_rate, beta_1=0.5)
        self.dis_optimizer = tf.keras.optimizers.Adam(self.learning_rate, beta_1=0.5)

        self._track_trackable(self.generator, name="generator")
        self._track_trackable(self.discriminator, name="discriminator")
        self._track_trackable(self.gen_optimizer, name="gen_optimizer")
        self._track_trackable(self.dis_optimizer, name="dis_optimizer")

        self.checkpoint = tf.train.Checkpoint(
            generator=self.generator,
            discriminator=self.discriminator,
            gen_optimizer=self.gen_optimizer,
            dis_optimizer=self.dis_optimizer
        )

    def build_generator(self):
        inputs = layers.Input(shape=self.img_size)

        x = layers.Conv2D(64, (7, 7), padding='same', activation='relu')(inputs)
        x = layers.Conv2D(128, (3, 3), strides=2, padding='same', activation='relu')(x)
        x = layers.Conv2D(256, (3, 3), strides=2, padding='same', activation='relu')(x)

        for _ in range(6):
            x = self.residual_block(x)

        x = layers.Conv2DTranspose(128, (3, 3), strides=2, padding='same', activation='relu')(x)
        x = layers.Conv2DTranspose(64, (3, 3), strides=2, padding='same', activation='relu')(x)
        outputs = layers.Conv2D(3, (7, 7), padding='same', activation='tanh')(x)

        return tf.keras.Model(inputs, outputs, name="Generator")

    def build_discriminator(self):
        inputs = layers.Input(shape=self.img_size)

        x = layers.Conv2D(64, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(inputs)
        x = layers.Conv2D(128, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(x)
        x = layers.Conv2D(256, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(x)
        x = layers.Conv2D(512, (4, 4), strides=2, padding='same', activation=tf.keras.layers.LeakyReLU())(x)

        outputs = layers.Conv2D(1, (4, 4), padding='same', activation='sigmoid')(x)

        return tf.keras.Model(inputs, outputs, name="Discriminator")

    def residual_block(self, x):
        res = x
        x = layers.Conv2D(256, (3, 3), padding='same', activation='relu')(x)
        x = layers.Conv2D(256, (3, 3), padding='same')(x)
        return layers.add([x, res])

    @tf.function
    def train_step(self, real_images, anime_images):
        with tf.GradientTape(persistent=True) as tape:
            fake_anime_images = self.generator(real_images, training=True)

            real_output = self.discriminator(anime_images, training=True)
            fake_output = self.discriminator(fake_anime_images, training=True)

            gen_loss = self.generator_loss(fake_output, real_images, fake_anime_images)
            disc_loss = self.discriminator_loss(real_output, fake_output)

        gen_gradients = tape.gradient(gen_loss, self.generator.trainable_variables)
        disc_gradients = tape.gradient(disc_loss, self.discriminator.trainable_variables)

        self.gen_optimizer.apply_gradients(zip(gen_gradients, self.generator.trainable_variables))
        self.dis_optimizer.apply_gradients(zip(disc_gradients, self.discriminator.trainable_variables))

        return gen_loss, disc_loss

    def generator_loss(self, fake_output, real_images, fake_images):
        adversarial_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.ones_like(fake_output), fake_output)
        content_loss = tf.reduce_mean(tf.abs(real_images - fake_images))
        return adversarial_loss + 10.0 * content_loss

    def discriminator_loss(self, real_output, fake_output):
        real_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.ones_like(real_output), real_output)
        fake_loss = tf.keras.losses.BinaryCrossentropy(from_logits=True)(tf.zeros_like(fake_output), fake_output)
        return real_loss + fake_loss

    def train(self, dataset, epochs):
        for epoch in range(epochs):
            for step, (real_images, anime_images) in enumerate(dataset):
                gen_loss, disc_loss = self.train_step(real_images, anime_images)

                if step % 100 == 0:
                    print(f"Epoch {epoch + 1}, Step {step}, Gen Loss: {gen_loss:.4f}, Disc Loss: {disc_loss:.4f}")
            if epoch % 10 == 0:
                self.save('./checkpoints')

    def save(self, checkpoint_dir):
        """Save the model checkpoint."""
        self.checkpoint.save(file_prefix=os.path.join(checkpoint_dir, "ckpt"))

    def load(self, checkpoint_dir):
        """Load the model checkpoint."""
        self.checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))

