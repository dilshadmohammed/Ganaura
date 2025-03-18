import tensorflow as tf
import os
from glob import glob
from Ganaura import Ganaura


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

def main():
# Paths to your image folders
    real_image_dir = "dataset/train_photo"
    anime_image_dir = "dataset/Hayao/style"

    # Create the dataset
    batch_size = 16
    dataset = create_dataset(real_image_dir, anime_image_dir, batch_size=batch_size)

    # gpus = tf.config.list_physical_devices('GPU')
    # if gpus:
    #     print("GPUs detected:", gpus)
    #     try:
    #         for gpu in gpus:
    #             tf.config.experimental.set_memory_growth(gpu, True)  # Allow dynamic memory allocation
    #     except RuntimeError as e:
    #         print(e)
    # Initialize the AnimeGANv3 model
    model = Ganaura(img_size=(256, 256, 3), batch_size=batch_size)

    # Train the model
    checkpoint_dir = "./final_checkpoints"
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    model.train(dataset, epochs=20)  # Set epochs as needed
    model.save(checkpoint_dir)

if __name__ == '__main__':
    main()
