from openai import AzureOpenAI
import json

client = AzureOpenAI(
    azure_endpoint="https://suvichaarai008818057333687.openai.azure.com/",
    api_key="BdF3fgzjYDE5j2WfQLh4uxblwoBN4OgooER86XJI7cx37R8Ku46LJQQJ99AKACYeBjFXJ3w3AAAAACOGYNrN",
    api_version="2024-02-01"
)

def generate_prompts_from_article_context(category, subcategory, emotion):
    system_prompt = """
You are a digital content editor for a web-based news platform.

Your job is to create a 5-slide web story for an article, based on its metadata:
- Category (e.g. Politics, Tech, Science)
- Subcategory (main person/event/issue)
- Dominant emotion evoked (e.g. pride, frustration, hope)

Make each slide:
- Brief and story-driven (1–2 sentences max)
- Professional, but not too formal (like a modern news web story)
- Targeted at a general news reader (not overly casual or Gen Z slang)

Return your response as a JSON object:
{
  "slides": [
    { "topic": "Slide topic 1", "prompt": "Slide 1 text" },
    { "topic": "Slide topic 2", "prompt": "Slide 2 text" },
    ...
  ]
}
"""

    user_prompt = f"""
Generate a 5-slide web story based on the following metadata:

Category: {category}
Subcategory: {subcategory}
Emotion: {emotion}

Write each slide with a distinct topic and corresponding text.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Strip code fences if GPT adds them
    if raw_text.startswith("```json"):
        raw_text = raw_text.removeprefix("```json").strip()
    if raw_text.endswith("```"):
        raw_text = raw_text.removesuffix("```").strip()

    try:
        return json.loads(raw_text)["slides"]
    except json.JSONDecodeError:
        return []
    

st.title("🧠 Generalized Web Story Prompt Engine")

url = st.text_input("Enter a news article URL")

persona = st.selectbox(
    "Choose audience persona:",
    ["genz", "millenial", "working professionals", "creative thinkers", "spiritual explorers"],
    key = "<1>"
)

if url and persona:
    with st.spinner("Analyzing the article and generating prompts..."):
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

            # Step 4: Generate 5-slide prompts using full article context
            output = title_script_generator(
                category, subcategory, emotion, article_text=full_text
            )

            # Merge sentiment, title, summary and persona into the final output
            final_output = {
                "title": title,
                "summary": summary,
                "sentiment": sentiment,
                "emotion": emotion,
                "category": category,
                "subcategory": subcategory,
                "persona": persona,
                "slides": output.get("slides", [])
            }

            st.success("✅ Prompt generation complete!")
            st.json(final_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

