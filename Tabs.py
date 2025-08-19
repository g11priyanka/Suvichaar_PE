from openai import AzureOpenAI
import os
import requests
from PIL import Image
import json
from dotenv import load_dotenv
import boto3
import streamlit as st
import json
from utils import (
    extract_article,
    get_sentiment,
    detect_category_and_subcategory,
    generate_story,
    pragnan_story,
    owl_response,
    spiritual,
    web_story,
    head,
    extract_subtopics,
    generate_podcast_script,
    hoot_explainer
)
from sample import (
    generate_image_prompts_one_by_one,
    generate_image_prompts,
    generate_and_save_images_azure,
    zip_images_in_memory,
    generate_scientific_image_prompts
)
from CS import (
    Nirvana_CS,
    Pragnan_CS,
    Polaris_CS,
    Chirai_CS,
    Owl_CS,
    Pengu_CS,
    Tika_CS,
    Rolo_CS,
    Sal_CS,
    Zuzu_CS,
    Luma_CS
)

from h import generate_s3_links,merge_image_links_into_slides

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

if os.getenv("STREAMLIT_RUNTIME") is None:
    load_dotenv()

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

st.set_page_config(page_title="Web Story Prompt Generator", layout="wide")

# Create Tabs
tabs = st.tabs(["⭐ Polaris", "✈️ Itinerary", "🌳 Pragnan Tells", "🖋 Nirvana Writes", "🦉 Hoot Answers", "🎙️ Podcast","Hoot explains"])

# ========== ⭐ Polaris ==========
with tabs[0]:
    st.title("Polaris News")
    st.image("Polaris.png",  width=300)
    with st.expander("About Polaris"):
        st.markdown(Polaris_CS)
    url = st.text_input("Enter a news article URL", key="url_input")
    persona_polaris = st.selectbox(
        "Choose audience persona:",
        ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
        key="persona_polaris"
    )

    if url and persona_polaris:
        with st.spinner("Analyzing the article and generating ..."):
            try:
                # Extract article details
                title, summary, full_text = extract_article(url)
                sentiment = get_sentiment(summary)
                result = detect_category_and_subcategory(full_text)
                category = result["category"]
                subcategory = result["subcategory"]
                emotion = result["emotion"]
                headline = head(url)
                titles = extract_subtopics(full_text, num_slides=5)

                # Generate structured web story
                output = web_story(
                    titles=titles,
                    headline=headline,
                    category=category,
                    subcategory=subcategory,
                    emotion=emotion,
                    article_text=full_text
                )

                final_output = {
                    "headline": headline,
                    "sentiment": sentiment,
                    "emotion": emotion,
                    "category": category,
                    "subcategory": subcategory,
                    "persona": persona_polaris,
                    "slides": output.get("slides", {})
                }
                st.success("✅ Prompt generation complete!")
                #st.json(final_output)

                # Prepare image prompt list excluding fixed slide10
                image_prompt_list = []
                for idx, (slide_key, slide_data) in enumerate(output.get("slides", {}).items(), start=1):
                    if idx == 10:  # Skip fixed slide10
                        continue
                    paragraph1 = slide_data.get(f"s{idx}paragraph1", "")
                    paragraph2 = slide_data.get(f"s{idx}paragraph2", "")
                    image_prompt_list.append({
                        "title": paragraph2,
                        "story": paragraph1
                    })

                # Persona context for image generation
                polaris_and_persona = f"{persona_polaris}\n\nCharacter Context:\nPolaris"

                # Generate image prompts
                prompts = generate_image_prompts_one_by_one(
                    image_prompt_list,
                    art_style="vector-style flat illustration"
                )
                st.success("🎨 Image prompts generated successfully!")
                st.json(prompts)

                # Image generation via Azure
                polaris_image_paths = generate_and_save_images_azure(prompts, client)
                 
               ##########################
                image_links = generate_s3_links(polaris_image_paths, BUCKET_NAME, s3_client)

                # FIX: only pass slides
                slides = final_output["slides"]
                slides = merge_image_links_into_slides(slides, image_links)
                final_output["slides"] = slides

                st.success("✅ Combined story + images")
                st.json(final_output)
                ##########################


                # Display images
                for idx, path in enumerate(polaris_image_paths, start=1):
                    st.image(path, caption=f"Slide {idx}", width=300)

                # ZIP download
                zip_buffer, zip_filename = zip_images_in_memory(polaris_image_paths)
                st.download_button(
                    label="📥 Download All Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


            

# ========== ✈️ Itinerary ==========
with tabs[1]:
    st.title("Chirai generates your itinerary")
    st.image("chirai.png",width=300)

    with st.expander("About Chirai"):
        st.markdown(Chirai_CS)

    place = st.text_input("Enter a place", key="place_input")
    persona_itinerary = st.selectbox(
        "Choose audience persona:",
        ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
        key="persona_itinerary"
    )

    if place and persona_itinerary:
        with st.spinner("Generating itinerary..."):
            try:
                full_slides = generate_story(place)
                st.success("✅ Prompt generation complete!")
                #st.json(full_slides)

                # Convert slides (except slide10) into list of dicts with 'title' and 'story'
                image_prompt_list = []
                for slide_key, slide_content in full_slides.items():
                    if slide_key == "slide10":
                        continue  # skip fixed slide10
                    n = slide_key.replace("slide", "")
                    title = slide_content.get(f"s{n}paragraph1", "")
                    story = slide_content.get(f"s{n}paragraph2", "").lstrip("- ").strip()
                    image_prompt_list.append({"title": title, "story": story})

                itinerary_prompts = generate_image_prompts(Chirai_CS, image_prompt_list)
                st.success("Image prompts generated")
                st.json(itinerary_prompts)

                image_paths = generate_and_save_images_azure(itinerary_prompts, client)
                
                ##########################
                image_links = generate_s3_links(image_paths,BUCKET_NAME,s3_client)

                full_slides = merge_image_links_into_slides(full_slides, image_links)

                st.success("✅ Combined story + images")
                st.json(full_slides)
                ############################

                for idx, path in enumerate(image_paths):
                    st.image(path, caption=f"Slide {idx+1}", width=300)

                zip_buffer, zip_filename = zip_images_in_memory(image_paths)
                st.download_button(
                    label="📥 Download All Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ========== 🌳 Pragnan Tells ==========
with tabs[2]:
    st.title("Pragnan Tells")
    st.image("pragnan.png",width=300)
    with st.expander("About Pragnan"):
        st.markdown(Pragnan_CS)
    topic = st.text_input("Enter a topic", key="topic_pragnan")
    persona_story = st.selectbox(
        "Choose audience persona:",
        ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
        key="persona_story"
    )
    language = "Hindi (use English letters only, no Devanagari script)"

    if topic and persona_story:
        with st.spinner("Generating story..."):
            try:
                full_story = pragnan_story(topic, 13, language)

                # Directly show the slide-based story JSON
                st.success("✅ Prompt generation complete!")
                #st.json(full_story)

                # Convert slides (except slide10) into list of dicts with 'title' and 'story' for image prompts
                image_prompt_list = []
                for slide_key, slide_content in full_story.items():
                    if slide_key == "slide10":
                        continue  # skip fixed slide10
                    n = slide_key.replace("slide", "")
                    title = slide_content.get(f"s{n}paragraph1", "")
                    story = slide_content.get(f"s{n}paragraph2", "").lstrip("- ").strip()
                    image_prompt_list.append({"title": title, "story": story})

                pragnan_prompts = generate_image_prompts(Pragnan_CS, image_prompt_list)
                st.success("Image prompts generated")
                st.json(pragnan_prompts)

                # Generate and save images
                p_image_paths = generate_and_save_images_azure(pragnan_prompts, client)

                ##########################
                image_links = generate_s3_links(p_image_paths,BUCKET_NAME,s3_client)

                full_story = merge_image_links_into_slides(full_story, image_links)

                st.success("✅ Combined story + images")
                st.json(full_story)
                ############################

                # Show images in Streamlit
                for idx, path in enumerate(p_image_paths):
                    st.image(path, caption=f"Slide {idx+1}", width=300)

                # Prepare ZIP for download
                zip_buffer, zip_filename = zip_images_in_memory(p_image_paths)

                st.download_button(
                    label="📥 Download All Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ========== 🖋 Nirvana Writes ==========
with tabs[3]:
    st.title("🖋 Nirvana Writes")
    st.image("nirvana.png",width=300)
    with st.expander("About Nirvana"):
        st.markdown(Nirvana_CS)
    topic_t = st.text_input("Enter your topic", key="nirvana_topic")
    persona_t = st.selectbox(
        "Choose audience persona:",
        ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
        key="nirvana_persona"
    )

    if topic_t and persona_t:
        with st.spinner("Generating story..."):
            try:
                # Generate structured slide dictionary with fixed slide10
                full_t = spiritual(topic_t, 2, language)

                # Show the slide-based story JSON
                st.success("✅ Prompt generation complete!")
                #st.json(full_t)

                # Prepare image prompt list (skip fixed slide10)
                image_prompt_list = []
                for slide_key, slide_content in full_t.items():
                    if slide_key == "slide10":
                        continue
                    n = slide_key.replace("slide", "")
                    title = slide_content.get(f"s{n}paragraph1", "")
                    story = slide_content.get(f"s{n}paragraph2", "").lstrip("- ").strip()
                    image_prompt_list.append({"title": title, "story": story})

                # Generate image prompts
                nirvana_prompts = generate_image_prompts(Nirvana_CS, image_prompt_list)
                st.success("Image prompts generated")
                st.json(nirvana_prompts)

                # Generate images
                image_paths = generate_and_save_images_azure(nirvana_prompts, client)

                ##########################
                image_links = generate_s3_links(image_paths,BUCKET_NAME,s3_client)

                full_t = merge_image_links_into_slides(full_t, image_links)

                st.success("✅ Combined story + images")
                st.json(full_t)
                ############################
                

                # Show images
                for idx, path in enumerate(image_paths):
                    st.image(path, caption=f"Slide {idx+1}", width=300)

                # ZIP download
                zip_buffer, zip_filename = zip_images_in_memory(image_paths)
                st.download_button(
                    label="📥 Download All Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")



# ========== 🦉 Hoot Answers ==========
with tabs[4]:
    st.title("🦉 Hoot Answers")
    st.image("owl.png",width=300)
    with st.expander("About Hoot"):
        st.markdown(Owl_CS)
    question = st.text_input("Enter your question/topic", key="hoot_input")
    persona_question = st.selectbox(
        "Choose audience persona:",
        ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
        key="hoot_persona"
    )

    if question and persona_question:
        with st.spinner("Generating answer..."):
            try:
                full_ans = owl_response(question, language)

                # Show the full structured story JSON
                st.success("✅ Prompt generation complete!")
                #st.json(full_ans)

                # Prepare prompt list for image generation (skip fixed slide10)
                image_prompt_list = []
                for slide_key, slide_content in full_ans.items():
                    if slide_key == "slide10":
                        continue  # don't make an image prompt for the fixed promo slide
                    n = slide_key.replace("slide", "")
                    title = slide_content.get(f"s{n}paragraph1", "")
                    story = slide_content.get(f"s{n}paragraph2", "").lstrip("- ").strip()
                    image_prompt_list.append({"title": title, "story": story})

                # Generate image prompts
                owl_prompts = generate_image_prompts(Owl_CS, image_prompt_list)
                st.success("Image prompts generated")
                st.json(owl_prompts)

                # Generate and save images
                image_paths = generate_and_save_images_azure(owl_prompts, client)

                 ##########################
                image_links = generate_s3_links(image_paths,BUCKET_NAME,s3_client)

                full_ans = merge_image_links_into_slides(full_ans, image_links)

                st.success("✅ Combined story + images")
                st.json(full_ans)
                ############################

                # Display generated images
                for idx, path in enumerate(image_paths):
                    st.image(path, caption=f"Slide {idx+1}", width=300)

                # Create downloadable ZIP
                zip_buffer, zip_filename = zip_images_in_memory(image_paths)

                st.download_button(
                    label="📥 Download All Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ========== 🎙️ Podcast ==========
with tabs[5]:
    st.title("🎙️ Podcast")
    st.image("pengu.png",width=300)
    with st.expander("About Tika"):
        st.markdown(Tika_CS)
    with st.expander("About Rolo"):
        st.markdown(Rolo_CS)
    with st.expander("About Sal"):
        st.markdown(Sal_CS)
    with st.expander("About Zuzu"):
        st.markdown(Zuzu_CS)
    with st.expander("About Luma"):
        st.markdown(Luma_CS)
    # Images for the 5 guests
    guest_images = [
        ("tika.png", "Tika"),
        ("rolo.png", "Rolo"),
        ("sal.png", "Sal"),
        ("zuzu.png", "Zuzu"),
        ("luma.png", "Luma"),
    ]

    # Display the 5 guest images below the penguin
    st.subheader("Meet your guests")
    cols = st.columns(5)  # 5 columns side by side

    for idx, (img, name) in enumerate(guest_images):
        with cols[idx]:
            st.image(img, width=150)
            st.caption(name)


    podcast_topic = st.text_input("Enter your topic for podcast", key="podcast_topic")
    guest = st.selectbox(
        "Choose your guest",
        ["Tika", "Rolo", "Sal", "Zuzu", "Luma"],
        key="podcast_guest"
    )

    if podcast_topic and guest:
        with st.spinner("Generating podcast script..."):
            try:
                # Guest character mapping
                guest_map = {
                    "Tika": Tika_CS,
                    "Rolo": Rolo_CS,
                    "Sal": Sal_CS,
                    "Zuzu": Zuzu_CS,
                    "Luma": Luma_CS
                }
                guest_character_sketch = guest_map[guest]

                # Generate structured podcast script (slides)
                podcast_script = generate_podcast_script(
                    podcast_topic,
                    guest,
                    guest_character_sketch,
                    language
                )

                # Show structured JSON output
                st.success("✅ Podcast script generation complete!")
                #st.json(podcast_script)

                # Prepare image prompts list (skip slide10 and keep same order)
                image_prompt_list = []
                total_slides = len(podcast_script)

                # Slides 1 to 9
                for n in range(1, 10):
                    key = f"slide{n}"
                    if key in podcast_script:
                        title = podcast_script[key].get(f"s{n}paragraph1", "")
                        story = podcast_script[key].get(f"s{n}paragraph2", "").lstrip("- ").strip()
                        image_prompt_list.append({"title": title, "story": story})

                # Slides 11 onwards
                for n in range(11, total_slides + 1):
                    key = f"slide{n}"
                    if key in podcast_script:
                        title = podcast_script[key].get(f"s{n}paragraph1", "")
                        story = podcast_script[key].get(f"s{n}paragraph2", "").lstrip("- ").strip()
                        image_prompt_list.append({"title": title, "story": story})

                # Persona context for image generation
                pengu_and_guest_CS = f"{Pengu_CS}\n\nGuest Character:\n{guest_character_sketch}"

                # Generate image prompts
                podcast_image_prompts = generate_image_prompts(
                    pengu_and_guest_CS,
                    image_prompt_list
                )
                st.success("🎨 Image prompts generated successfully!")
                st.json(podcast_image_prompts)

                # Generate images via Azure
                image_paths = generate_and_save_images_azure(podcast_image_prompts, client)
                ##########################
                image_links = generate_s3_links(image_paths,BUCKET_NAME,s3_client)

                podcast_script = merge_image_links_into_slides(podcast_script, image_links)

                st.success("✅ Combined story + images")
                st.json(podcast_script)
                ############################

                # Display images with captions
                for idx, path in enumerate(image_paths, start=1):
                    st.image(path, caption=f"Slide {idx}", width=300)

                # ZIP download button
                zip_buffer, zip_filename = zip_images_in_memory(image_paths)
                st.download_button(
                    label="📥 Download All Podcast Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tabs[6]:
    st.title("🦉 Hoot Explains")
    st.image("owl.png", width=300)

    with st.expander("About Hoot"):
        st.markdown(Owl_CS)  # or Hoot_CS if renamed

    # User inputs
    explain = st.text_input("Enter your question/topic", key="hoot")
    num_subtopics = st.text_input("Enter number of slides", key="numSlides")

    persona_explain = st.selectbox(
        "Choose audience persona:",
        ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
        key="explain_persona"
    )

    language = st.selectbox("Choose language", ["English"], key="hoot_language")

    # Trigger generation
    if explain and persona_explain and num_subtopics:
        with st.spinner("Hoot is thinking..."):
            try:
                # 1. Generate explanation from Hoot
                full_explain = hoot_explainer(explain, num_subtopics, language)

                st.success("✅ Explanation generated!")
                st.json(full_explain)

                # 2. Prepare prompt list for image generation

                image_prompt_list = []
                for slide_key, slide_content in full_explain.items():
                    # extract number part: slide1 -> 1, slide10 -> 10
                    n = ''.join(ch for ch in slide_key if ch.isdigit())
                    
                    explanation = slide_content.get(f"s{n}paragraph1", "")
                    title = slide_content.get(f"s{n}paragraph2", "").lstrip("- ").strip()
                    
                    image_prompt_list.append({"title": title, "content": explanation})

                # 3. Generate image prompts
                hoot_prompts = generate_scientific_image_prompts(
                    CharacterSketch=Owl_CS,
                    data_list=image_prompt_list,
                    art_style="scientific vector-style flat illustration"
                )
                st.success("🖼️ Image prompts generated!")
                st.json(hoot_prompts)

                # 4. Generate images using Azure OpenAI
                image_paths = generate_and_save_images_azure(hoot_prompts, client)
                ##########################
                image_links = generate_s3_links(image_paths,BUCKET_NAME,s3_client)

                full_explain = merge_image_links_into_slides(full_explain, image_links)

                st.success("✅ Combined story + images")
                st.json(full_explain)
                ############################

                # 5. Display images with captions
                for idx, path in enumerate(image_paths):
                    st.image(path, caption=f"Slide {idx + 1}", width=300)

                # 6. Zip and allow download
                zip_buffer, zip_filename = zip_images_in_memory(image_paths)

                st.download_button(
                    label="📥 Download All Images",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
