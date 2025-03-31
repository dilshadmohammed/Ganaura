import onnxruntime as ort
import numpy as np
import cv2
import os
from glob import glob
import argparse

def preprocess_image(image, img_size=(256, 256)):
    """
    Preprocess image for model input
    
    Args:
        image: Input image (numpy array)
        img_size: Target size for resizing (default: 256x256)
        
    Returns:
        Preprocessed image normalized to [-1, 1]
    """
    # Resize if needed
    if img_size is not None:
        image = cv2.resize(image, img_size)
    
    # Convert BGR to RGB (if using OpenCV)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Normalize to [-1, 1]
    image = (image / 127.5) - 1.0
    
    return image.astype(np.float32)

def postprocess_image(image):
    """
    Convert model output back to displayable image
    
    Args:
        image: Model output tensor in range [-1, 1]
        
    Returns:
        Image in uint8 format suitable for saving/display
    """
    # Convert from [-1, 1] to [0, 255]
    image = ((image + 1) * 127.5).astype(np.uint8)
    
    # Convert RGB to BGR for OpenCV
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    return image


def filter(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  
    edges = cv2.adaptiveThreshold(cv2.medianBlur(gray, 5), 255, 
                                  cv2.ADAPTIVE_THRESH_MEAN_C, 
                                  cv2.THRESH_BINARY, 9, 10)  

    color = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    filter_image = cv2.bitwise_and(color, edges_colored)

    return filter_image



class GanauraInference:
    def __init__(self, model_path, use_gpu=True):
        """
        Initialize the Ganaura inference engine
        
        Args:
            model_path: Path to the ONNX model
            use_gpu: Whether to use GPU for inference (if available)
        """
        # Set up ONNX Runtime session
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if use_gpu else ['CPUExecutionProvider']
        try:
            self.session = ort.InferenceSession(model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            print(f"Model loaded successfully from {model_path}")
            print(f"Input name: {self.input_name}")
            print(f"Input shape: {self.session.get_inputs()[0].shape}")
            print(f"Using providers: {self.session.get_providers()}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def transform_image(self, image, img_size=None):
        """
        Transform a single image from real to anime style
        
        Args:
            image: Input image (numpy array in BGR format)
            img_size: Optional target size for resizing
            
        Returns:
            Anime-style image
        """
        # Preprocess the image
        processed_img = preprocess_image(image, img_size)
        
        # Add batch dimension
        input_tensor = np.expand_dims(processed_img, axis=0)
        
        # Run inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # Get output image and remove batch dimension
        anime_image = outputs[0][0]
        
        # Post-process the output
        result = postprocess_image(anime_image)
        result = filter(result)
        
        return result
    
    def transform_file(self, input_path, output_path, img_size=None):
        """
        Transform a single image file
        
        Args:
            input_path: Path to input image
            output_path: Path to save output image
            img_size: Optional target size for resizing
        """
        # Read the image
        image = cv2.imread(input_path)
        if image is None:
            print(f"Error reading image: {input_path}")
            return False
        
        # Transform the image
        result = self.transform_image(image, img_size)
        
        # Save the result
        output_dir = os.path.dirname(output_path)
        # Only try to create directory if there is one specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        cv2.imwrite(output_path, result)
        print(f"Transformed image saved to: {output_path}")
        
        return True
    
    def transform_directory(self, input_dir, output_dir, img_size=None, extensions=(".jpg", ".jpeg", ".png")):
        """
        Transform all images in a directory
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save output images
            img_size: Optional target size for resizing
            extensions: Tuple of valid file extensions to process
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all image files
        image_files = []
        for ext in extensions:
            image_files.extend(glob(os.path.join(input_dir, f"*{ext}")))
        
        if not image_files:
            print(f"No images found in {input_dir}")
            return
        
        # Process each image
        success_count = 0
        for input_path in image_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_dir, filename)
            
            try:
                if self.transform_file(input_path, output_path, img_size):
                    success_count += 1
            except Exception as e:
                print(f"Error processing {input_path}: {e}")
        
        print(f"Processed {success_count}/{len(image_files)} images successfully")

def main():
    """Main function to parse arguments and run inference"""
    parser = argparse.ArgumentParser(description="Ganaura GAN Image Transformation")
    parser.add_argument("--model", type=str, default='final_checkpoints/generator.onnx', help="Path to the ONNX model")
    parser.add_argument("--input", type=str, required=True, help="Path to input image or directory")
    parser.add_argument("--output", type=str, required=True, help="Path to output image or directory")
    parser.add_argument("--size", type=int, nargs=2, default=None, help="Resize image to WxH (e.g., --size 256 256)")
    parser.add_argument("--cpu", action="store_true", help="Force CPU inference")
    
    args = parser.parse_args()
    
    # Convert size argument to tuple if provided
    img_size = tuple(args.size) if args.size else None
    
    # Determine if input is a file or directory
    is_directory = os.path.isdir(args.input)
    
    # Create inference engine
    inference = GanauraInference(args.model, use_gpu=not args.cpu)
    
    if is_directory:
        # Process directory
        inference.transform_directory(args.input, args.output, img_size=img_size)
    else:
        # Process single file
        inference.transform_file(args.input, args.output, img_size=img_size)

if __name__ == "__main__":
    main()