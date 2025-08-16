from openai import AzureOpenAI
import os
import requests
from PIL import Image
import json

client = AzureOpenAI(
    api_version="2024-02-01",  
    api_key=os.environ["AZURE_API_KEY"],  
    azure_endpoint=os.environ['AZURE_ENDPOINT']
)

def generate_image_prompts(data_list, art_style="vector-style flat illustration"):
    f"""
    Generate symbolic image prompts from a list of title-content pairs.

    Args:
        data_list: List of dictionaries, each with 'title' and 'content' keys.
        art_style: {art_style}

    Returns:
        List of DALL·E-style image prompts.
    """
    prompts = []

    for item in data_list:
        title = item["title"]
        content = item["content"]

        prompt_text = f"""
You are an expert DALL·E 3 image prompt engineer.

Use the following title and context to write a symbolic, creative image prompt that visually represents the essence of the content.

Art Style: {art_style}
Mood: Calm, editorial, respectful.
Avoid: Graphic realism, distress, famous figures,non sexual.

Title: "{title}"

Context:
\"\"\"
{content}
\"\"\"

Output ONLY the image prompt. No labels or titles.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_text.strip()}]
        )

        result = response.choices[0].message.content.strip()
        if result.startswith("```"):
            result = result.split("```")[1].strip()

        prompts.append(result)

    return prompts


def generate_and_save_images_azure(prompts, client, model_name="dall-e-3", output_dir="images"):
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    for idx, prompt in enumerate(prompts, start=1):
        try:
            print(f"Generating image {idx}...")

            result = client.images.generate(
                model=model_name,
                prompt=prompt,
                n=1
            )

            json_response = json.loads(result.model_dump_json())
            image_url = json_response["data"][0]["url"]

            image_path = os.path.join(output_dir, f"slide{idx}_image_nirvana.png")
            image_data = requests.get(image_url).content

            with open(image_path, "wb") as f:
                f.write(image_data)

            print(f"Saved: {image_path}")

        except Exception as e:
            print(f"Error generating image {idx}: {e}")


