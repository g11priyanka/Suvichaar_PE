import boto3
import os
import streamlit as st
from sample import generate_and_save_images_azure
# ========== Define S3 client globally ==========
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def get_secret(key: str):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

api_key = get_secret("AZURE_API_KEY")
endpoint = get_secret("AZURE_ENDPOINT")

from openai import AzureOpenAI
client = AzureOpenAI(
    api_version="2024-02-01",
    api_key=api_key,
    azure_endpoint=endpoint
)

# ========== Function to generate S3 links ==========
def generate_s3_links(image_paths, bucket_name, s3_client):
    """
    Uploads images to S3 and returns their public URLs.

    Args:
        image_paths (list[str]): Local paths of images to upload.
        bucket_name (str): Name of your S3 bucket.
        s3_client: boto3 S3 client object.

    Returns:
        list[str]: Public URLs of uploaded images.
    """
    urls = []
    for image_path in image_paths:
        filename = os.path.basename(image_path)
        try:
            s3_client.upload_file(
                Filename=image_path,
                Bucket=bucket_name,
                Key=filename,
                #ExtraArgs={'ACL': 'public-read'}  # Make file public
            )
            url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{filename}"
            urls.append(url)
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            urls.append("")  # Add empty string if failed

    return urls

image_prompts = [
    "A vector-style flat illustration representing a serene evening view from Victoria Peak. The skyline of Hong Kong bathed in the warm, fading light of sunset with shades of pink and orange gradually transitioning into a darker blue. Tiny, luminous dots imitate city lights below, resembling stars scattered across the earth, while a gentle breeze symbolized by delicate swirls subtly animates the scene. This illustration is calm, respectful, and captures the magical transformation of the city as day turns to night.",
    
    "A serene, vector-style flat illustration capturing the vibrant Temple Street Night Market at night in Hong Kong. The scene includes diverse, unidentifiable people of various ethnicities browsing colorful stalls filled with antiques and street food. At the center, a vendor elegantly serves stir-fry seafood, surrounded by glowing lanterns that softly illuminate the environment. The atmosphere should convey a sense of communal joy and tranquility, with the characters shown smiling, engaged in light conversations, and enjoying their time, reflecting a cultural melting pot in a calm and respectful editorial mood.",
    
    "A serene vector-style flat illustration showing a peaceful landscape of Lantau Island. The foreground features a figure sitting cross-legged and meditatively looking at the Giant Buddha statue, portrayed in a simplified, non-detailed style. Surrounding the Buddha is lush greenery and rolling hills that encapsulate the island's natural beauty. The sky is rendered in soft pastel colors, reflecting a calm and harmonious mood. Gently stylized clouds float above, enhancing the tranquil setting.",
    
    "A serene, vector-style flat illustration of Victoria Harbour during the Symphony of Lights show. The image features a calm, twilight backdrop with stylized geometric shapes representing water. Over the water dance numerous, softly glowing orbs in a spectrum of colors - blues, purples, oranges, and yellows - arranged to suggest movement and harmony, like notes on a musical scale. These lights gently reflect on the surface of the water, creating a mirroring effect that enhances the sense of tranquility. The skyline in the background is depicted in soothing pastel shades, subtly suggesting the presence of the city without overwhelming the serene spectacle of the lights and their reflection.",
    
    "A serene, vector-style flat illustration depicting the scenic coastal town of Sai Kung. The image features a calm beach with crystal clear waters in the forefront, a few people enjoying the tranquil setting. In the background, a bustling seafood market line the shore with colorful, quaint stalls offering an array of fresh seafood, capturing the essence of local culinary delights. Overlooking the market, the majestic Sai Kung Geopark is seen with lush greenery and uniquely shaped rock formations, representative of its natural beauty, all under a clear, calming sky."
]


#image_paths = generate_and_save_images_azure(image_prompts, client)
#image_urls = generate_s3_links(image_paths, BUCKET_NAME, s3_client)
#print(image_urls)

# merge_utils.py
from typing import Dict, List

def merge_image_links_into_slides(slides: Dict[str, dict], image_links: List[str]) -> Dict[str, dict]:
    """
    Mutates + returns `slides` by inserting each image link into s{n}image1
    following the same order you used to build prompts (skips slide10).
    Safe if links < slides (fills "" when missing).
    """
    i = 0
    for slide_key, slide in slides.items():
        if slide_key == "slide10":
            continue
        try:
            n = int(slide_key.replace("slide", ""))  # e.g. "slide3" -> 3
        except ValueError:
            continue
        link = image_links[i] if i < len(image_links) else ""
        slide[f"s{n}image1"] = link
        i += 1
    return slides
