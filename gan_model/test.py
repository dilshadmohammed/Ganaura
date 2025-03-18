import tensorflow as tf
from Ganaura import Ganaura  # Import your class

# Initialize model
gan = Ganaura()
checkpoint_dir = "./checkpoints"
latest_ckpt = tf.train.latest_checkpoint(checkpoint_dir)

if latest_ckpt:
    print(f"Restoring from checkpoint: {latest_ckpt}")
    gan.load(latest_ckpt)  # Load the model checkpoint

# Save the generator model (not the entire GAN class)
saved_model_dir = "./saved_model"
tf.saved_model.save(gan.generator, saved_model_dir)  # Only the generator is saved
print(f"Model saved to {saved_model_dir}")
