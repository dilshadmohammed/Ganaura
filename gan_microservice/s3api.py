import os
import boto3
from botocore.exceptions import ClientError
import mimetypes
import uuid
from dotenv import load_dotenv

class DOSpacesManager:
    def __init__(self, access_key_id, secret_key, region='sgp1'):
        """
        Initialize DigitalOcean Spaces client
        
        :param access_key_id: Your DigitalOcean Spaces access key ID
        :param secret_key: Your DigitalOcean Spaces secret key
        :param region: The region of your Space (default: nyc3)
        """

        self.region = region
        # Create a session
        self.session = boto3.session.Session()
        
        # Initialize the S3 client with DigitalOcean Spaces configuration
        self.client = self.session.client(
            's3',
            region_name=region,
            endpoint_url=f'https://{region}.digitaloceanspaces.com',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key
        )

    def create_space(self, space_name):
        """
        Create a new Space (bucket)
        
        :param space_name: Name of the Space to create
        :return: True if successful, False otherwise
        """
        
        try:
            self.client.create_bucket(Bucket=space_name)
            
            # Configure public access
            self.client.put_bucket_acl(
                Bucket=space_name,
                ACL='private'
            )
            
            print(f"Space '{space_name}' created successfully!")
            return True
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"Space '{space_name}' already exists.")
            elif error_code == 'BucketAlreadyOwnedByYou':
                print(f"You already own the Space '{space_name}'.")
            else:
                print(f"Error creating Space: {e}")
            return False

    def upload_file(self, space_name, file_path):
        """
        Upload a file to a specific Space
        
        :param space_name: Name of the Space to upload to
        :param file_path: Path to the file to upload
        :param object_name: Name of the object in the Space (optional)
        :return: Public URL of the uploaded file
        """
        try:

            content_type, _ = mimetypes.guess_type(file_path)
            if not (content_type and (content_type.startswith('image/') or content_type.startswith('video/'))):
                raise ValueError("File must be an image or video")
            
            
            file_extension = os.path.splitext(file_path)[1]
            random_filename = str(uuid.uuid4()) + file_extension

            self.client.upload_file(
            file_path, 
            'ganaura', 
            random_filename, 
            ExtraArgs={
                'ACL': 'public-read', 
                'ContentType': content_type, 
                'ContentDisposition': 'inline'
                }
                )
            
            # Construct and return public URL
            public_url = f'https://{space_name}.{self.region}.cdn.digitaloceanspaces.com/{random_filename}'
            return public_url
        
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None


def upload_to_cloud(file_path):
    
    load_dotenv()
    ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SPACE_NAME = os.getenv('SPACE_NAME')
    # Create Spaces manager
    spaces_manager = DOSpacesManager(ACCESS_KEY_ID, SECRET_KEY)
    
    spaces_manager.create_space(SPACE_NAME)

    # Optional: Upload a file to a Space
    return spaces_manager.upload_file(
        space_name=SPACE_NAME, 
        file_path=file_path
    )