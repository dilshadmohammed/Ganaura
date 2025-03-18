import cv2
import matplotlib.pyplot as plt
from Ganaura import Ganaura
import numpy as np
import tensorflow as tf

def generate_anime_image(model, input_image_path, output_image_path=None):
    """
    Generate an anime-style image using the pre-trained AnimeGAN model.
    
    Args:
        model: Trained AnimeGANv3 instance.
        input_image_path: Path to the input real-world image.
        output_image_path: Path to save the generated anime-style image (optional).
    """
    # Load and preprocess the input image
    img = cv2.imread(input_image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (model.img_size[0], model.img_size[1]))
    img = img / 127.5 - 1.0  # Normalize to [-1, 1]
    img_tensor = tf.expand_dims(img, axis=0)  # Add batch dimension

    # Generate anime-style image
    anime_img_tensor = model.generator(img_tensor, training=False)
    anime_img = anime_img_tensor[0].numpy()  # Remove batch dimension
    anime_img = (anime_img + 1.0) * 127.5  # Rescale to [0, 255]
    anime_img = anime_img.astype(np.uint8)

    # Save or display the result
    if output_image_path:
        cv2.imwrite(output_image_path, cv2.cvtColor(anime_img, cv2.COLOR_RGB2BGR))
        print(f"Anime-style image saved to {output_image_path}")

    # Display the result
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Input Image")
    plt.imshow(img / 2.0 + 0.5)  # Rescale to [0, 1] for display
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.title("Anime-style Image")
    plt.imshow(anime_img)
    plt.axis("off")
    plt.show()


model = Ganaura(img_size=(720, 720, 3))
model.load("./final_checkpoints")  # Load pre-trained weights

# Generate anime-style image
input_image_path = "inputs/imgs/v3_17.jpg" # Path to your real-world image
output_image_path = "output.jpg"  # Optional path to save the output

generate_anime_image(model, input_image_path, output_image_path)
