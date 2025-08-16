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
    generate_podcast_script
)
from sample import (
    generate_image_prompts_one_by_one,
    generate_image_prompts
)
from CS import (
    Nirvana_CS,
    Pragnan_CS,
    Polaris_CS,
    Chirai_CS,
    Owl_CS,
    Tika_CS,
    Rolo_CS,
    Sal_CS,
    Zuzu_CS,
    Luma_CS
)

st.set_page_config(page_title="Web Story Prompt Generator", layout="wide")

#ROHAN_SECOND_DRAFT
st.title("⭐ Polaris")

url = st.text_input("Enter a news article URL")

persona_polaris = st.selectbox(
    "Choose audience persona:",
    ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
    key = "<1>"
)

if url and persona_polaris:
    with st.spinner("Analyzing the article and generating ..."):
        try:
            # Step 1: Extract article content
            title, summary, full_text = extract_article(url)

            # Step 2: Sentiment analysis
            sentiment = get_sentiment(summary)

            # Step 3: Category, Subcategory, Emotion detection via GPT
            result = detect_category_and_subcategory(full_text)
            category = result["category"]
            subcategory = result["subcategory"]
            emotion = result["emotion"]

            # Step 4: Extract the headline from the URL
            headline = head(url)

            # Step 5: Generate slide titles (subtopics)
            titles = extract_subtopics(full_text, num_slides=5)
            

            # Step 6: Generate Polaris-style slide content
            output = web_story(
                titles=titles,
                headline=headline,
                category=category,
                subcategory=subcategory,
                emotion=emotion,
                article_text=full_text
            )

            # Step 7: Final assembled output
            final_output = {
                "headline": headline,
                "sentiment": sentiment,
                "emotion": emotion,
                "category": category,
                "subcategory": subcategory,
                "persona": persona_polaris,
                "slides": output.get("slides", [])
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if url and persona_polaris:
    prompts = generate_image_prompts_one_by_one(titles,full_text)

    st.success("Image prompts generated")
    st.json(prompts)

    

#TRAVEL
st.title("✈️ Itinerary generator")
place=st.text_input("Enter a place")
persona_itinerary= st.selectbox(
    "Choose audience persona:",
    ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
    key = "<2>"
)

if place and persona_itinerary:
    with st.spinner("Generating itinerary....."):
        try:
            full_itinerary = generate_story(place)

            # Merge sentiment, title, summary and persona into the final output
            final_output = {
                "Place": place,
                "Itinerary" : full_itinerary
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if place and persona_itinerary:
    itinerary_prompts = generate_image_prompts(Chirai_CS,full_itinerary)

    st.success("Image prompts generated")
    st.json(itinerary_prompts)



#STORY
st.title("🌳 Pragnan Tells")
topic = st.text_input("Enter a topic")
persona_story= st.selectbox(
    "Choose audience persona:",
    ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
    key = "<3>"
)
language = "Hindi with english script" 

if topic and persona_story:
    with st.spinner("Generating story....."):
        try:
            full_story = pragnan_story(topic,5,language)
            final_output = {
                "Topic": topic,
                "Story" : full_story
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if topic and persona_story:
    pragnan_prompts = generate_image_prompts(Pragnan_CS,full_story)

    st.success("Image prompts generated")
    st.json(pragnan_prompts)


#Story 2
st.title("🖋 Nirvana Writes")
topic_t = st.text_input("Enter your topic")
persona_t= st.selectbox(
    "Choose audience persona:",
    ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
    key = "<4>"
) 

if topic_t and persona_t:
    with st.spinner("Generating answer....."):
        try:
            full_t = spiritual(topic_t,5,language)
            final_output = {
                "Topic": topic_t,
                "Story" : full_t
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if topic_t and persona_t:
    nirvana_prompts = generate_image_prompts(Nirvana_CS,full_t)

    st.success("Image prompts generated")
    st.json(nirvana_prompts)

#ANSWER
st.title("🦉 Hoot Answers")
question = st.text_input("Enter your question/topic")
persona_question= st.selectbox(
    "Choose audience persona:",
    ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
    key = "<5>"
) 

if question and persona_question:
    with st.spinner("Generating answer....."):
        try:
            full_ans = owl_response(question,language)
            final_output = {
                "Input": question,
                "Story" : full_ans
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if question and persona_question:
    owl_prompts = generate_image_prompts(Owl_CS,full_ans)

    st.success("Image prompts generated")
    st.json(owl_prompts)

st.title("Podcast")
podcast_topic = st.text_input("Enter your topic for podcast")
guest= st.selectbox(
    "Choose your guest",
    ["Tika", "Rolo", "Sal", "Zuzu", "Luma"],
    key = "<6>"
)

if podcast_topic and guest:
    with st.spinner("Generating answer....."):
        try:
            if guest == "Tika":
                guest_character_sketch = Tika_CS
            elif guest == "Rolo":
                guest_character_sketch = Rolo_CS
            elif guest == "Sal":
                guest_character_sketch = Sal_CS
            elif guest == "Zuzu":
                guest_character_sketch = Zuzu_CS
            elif guest == "Luma":
                guest_character_sketch = Luma_CS

            podcast_script = generate_podcast_script(podcast_topic,guest,guest_character_sketch,language)
            final_output = {
                "Script" : podcast_script
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")