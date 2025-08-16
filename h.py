# Step 1: Install boto3 (only once in terminal, not inside the script)
# pip install boto3

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Step 2: File path (local image on your computer)
filename = "C:/Users/LENOVO/Desktop/prompt_engine/luma.png"  # 👈 change this to your file path
file_key = os.path.basename(filename)  # Just the filename for S3

# Step 3: AWS credentials
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_KEY"]
AWS_REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["AWS_BUCKET"]

# Step 4: Create S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Step 5: Upload the file (make it public)
try:
    s3_client.upload_file(
        Filename=filename,
        Bucket=BUCKET_NAME,
        Key=file_key,
        #ExtraArgs={'ACL': 'public-read'}  # 👈 Make file public
    )
    print(f"✅ {file_key} uploaded successfully to {BUCKET_NAME}")
except Exception as e:
    print(f"❌ Error uploading file: {e}")

# Step 6: Public URL
s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"
print("🌐 Public S3 URL:", s3_url)
