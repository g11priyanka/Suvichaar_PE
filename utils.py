import json
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import requests
from PIL import Image
import uuid
import newspaper
from textblob import TextBlob
import re
from CS import Pengu_CS
import re

load_dotenv()

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version="2024-02-01"
)

def extract_article(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article.title, article.summary, article.text

def get_sentiment(text):
    
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"

def extract_subtopics(text, num_slides):
    system_prompt = f"""
You are a web story editor for a digital news platform.

Your task is to write {num_slides} slide titles for a web story based on a news article.

Vary the style — use punchy phrases, rhetorical questions, timelines, or dramatic framings. Avoid using colons. Avoid repetitive formats. Make each title engaging and distinct.

Each title represents a visual chapter in the storytelling sequence.

Use narrative roles such as:
- Hook (grab attention)
- Background (introduce key subjects or context)
- Insight (reveal deeper details like motives or causes)
- Conflict (highlight tension, challenges, or twists)
- Reaction (responses from public, media, or officials)
- Impact (long-term effects or significance)
- Outlook (what comes next or broader meaning)

You can use a role more than once if the story is complex. 
Focus on variety and logical progression.

Return only the slide titles as a JSON list of {num_slides} strings. Do NOT include explanations or extra text.
Keep titles short and punchy, ideally under 8 words.
"""

    user_prompt = f"""
Generate {num_slides} slide titles for a web story based on the following news article:
Do not use colons in any title.
\"\"\"
{text[:3000]}
\"\"\"

Return format:
[
  "Slide Title 1",
  "Slide Title 2",
  ...
]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()
    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return [line.strip("- ").strip() for line in content.split("\n") if line.strip()]

def detect_category_and_subcategory(text):
    prompt = f"""
You are an expert news analyst.

Analyze the following news article and return:

1. The best matching **category** from this fixed list:
   - Politics
   - Business & Economy
   - Technology
   - Science & Environment
   - Health
   - Crime & Law
   - Sports
   - Entertainment
   - Lifestyle
   - Education
   - World / International
   - Local / Regional News
   - Opinion / Editorial
   - Religion & Spirituality
   - Obituaries & Tributes

2. A short, specific **subcategory** that summarizes the article’s main subject. 
   The subcategory should be highly relevant and can be:
   - a **person** (e.g., "Narendra Modi", "Gukesh Dommaraju")
   - an **event** (e.g., "Norway Chess 2025", "Budget 2024")
   - a **topic or issue** (e.g., "Mental Health in Schools", "Data Privacy")
   - a **location** (e.g., "Manipur", "Silicon Valley")
   - an **organization or institution** (e.g., "UNICEF", "Apple Inc.")
   - a **product or platform** (e.g., "ChatGPT", "Apple Vision Pro")
   - a **policy or law** (e.g., "Digital Personal Data Bill", "NEP 2020")
   - a **conflict or investigation** (e.g., "ED Probe", "Supreme Court Ruling")
   - a **cultural trend or movement** (e.g., "Remote Work Culture", "Clean Living")

3. The **primary emotion** evoked by the article (e.g., Pride, Sadness, Hope, Outrage, Empathy, Awe, Fear, Inspiration)

Article:
\"\"\"
{text[:3000]}
\"\"\"

Respond **only** in the following JSON format:
{{
  "category": "...",
  "subcategory": "...",
  "emotion": "..."
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You classify news articles by category, specific subcategory, and primary emotion evoked."},
            {"role": "user", "content": prompt.strip()}
        ]
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()
    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "category": "Unknown",
            "subcategory": "General",
            "emotion": "Neutral"
        }

def head(url : str):
    character_sketch = """
Polaris is the North Star — a fixed, timeless observer in the sky who now serves as a global newsreader. 
It is not human, but its presence is calm, constant, and quietly authoritative. 
Polaris views the world from above, without bias or emotion, and speaks in a clear, structured voice. 
Its tone is neutral, composed, and respectful — never dramatic, never sensational. 
It does not offer opinions or analysis, only verifiable facts, headlines, and updates from around the world. 
Polaris exists to inform, not to persuade. Its language is articulate but simple, formal but accessible. 
As a narrator, Polaris remains distant yet sincere, bringing the light of truth without the weight of interpretation. 
Whether it is war or weather, science or society, Polaris delivers every story with the steadiness of a star that never moves — only watches, and gently speaks.
"""
    system_prompt = f""" 
    You are Polaris with the gie character sketch {character_sketch}.
    Your role is to create one professional, concise, and objective headline in English.
     Guidelines for headline generation:
    - Stay formal, neutral, and fact-based.
    - Do not include opinion, sensationalism, or dramatic language.
    - Keep the headline between 10 to 14 words max.
    - Focus on the core event, actor(s), and impact.
    - Never speculate or exaggerate.
    - Avoid unnecessary punctuation like exclamation marks or quotes unless part of a statement.
    - Prioritize clarity and completeness over catchiness.

    Return only the headline.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a headline for the following article:\n\n{url}"}
        ]
    )

    headline = response.choices[0].message.content.strip()
    return headline
    
def web_story(titles, headline, category, subcategory, emotion, article_text, num_slides, character_sketch=None):
    if not character_sketch:
        character_sketch = """
Polaris is the North Star — a fixed, timeless observer in the sky who now serves as a global newsreader. 
It is not human, but its presence is calm, constant, and quietly authoritative. 
Polaris views the world from above, without bias or emotion, and speaks in a clear, structured voice. 
Its tone is neutral, composed, and respectful — never dramatic, never sensational. 
It does not offer opinions or analysis, only verifiable facts, headlines, and updates from around the world. 
Polaris exists to inform, not to persuade. Its language is articulate but simple, formal but accessible. 
As a narrator, Polaris remains distant yet sincere, bringing the light of truth without the weight of interpretation.
"""

    system_prompt = f"""
You are Polaris, a neutral, non-human global newsreader.

Your task is to generate web story slide content based on a list of slide titles and an article text.

Use this character sketch:
{character_sketch}

Instructions:
- Generate exactly {num_slides} slides (before adding the fixed promotional slide).
- For each given title, write a short paragraph (about 150-180 characters) that clearly and objectively summarizes key facts from the article.
- Use Polaris’s tone: calm, clear, factual, respectful.
- After all {num_slides} slides, add a final slide titled "Polaris Message" with a neutral 180-character message of reflection or reminder.
- Do not exceed the character limit for any slide.

IMPORTANT:
- You must return exactly {num_slides} slides in the `slides` array.
- If there is not enough unique information for each slide, rephrase, split, or slightly expand the facts so that each slide is unique and no slide is omitted.
- Do not merge slides. Do not reduce the number of slides.

Return only the following JSON format:
{{
  "slides": [
    {{ "title": "Slide Title", "content": "180-character factual summary." }},
    ...
    {{ "title": "Polaris Message", "content": "180-character reflective message." }}
  ]
}}
"""

    user_prompt = f"""
Category: {category}
Subcategory: {subcategory}
Emotion: {emotion}
Headline: {headline}

Titles:
{json.dumps(titles, indent=2)}

Article:
\"\"\" 
{article_text[:3000]}
\"\"\"

Return only the JSON as specified. No commentary.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```json"):
        raw = raw.removeprefix("```json").strip()
    if raw.endswith("```"):
        raw = raw.removesuffix("```").strip()

    try:
        slides_list = json.loads(raw).get("slides", [])

        # Ensure we always have num_slides by filling missing
        while len(slides_list) < num_slides:
            slides_list.append({"title": f"Placeholder Slide {len(slides_list)+1}", "content": "- "})

        # Convert AI output to pragnan_story style format
        slides = {}
        for i, slide in enumerate(slides_list, start=1):
            slides[f"slide{i}"] = {
                f"s{i}paragraph1": slide.get("content", ""),
                f"s{i}audio1": "",
                f"s{i}image1": "",
                f"s{i}paragraph2": slide.get("title", "- ")
            }

        # Add fixed promotional slide10
        slides["slide10"] = {
            "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
            "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
            "s10video1": "",
            "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
        }

        # Apply pragnan_story reordering
        if num_slides > 9:
            reordered = {}
            for n in range(1, 10):
                key = f"slide{n}"
                if key in slides:
                    reordered[key] = slides[key]
            for n in range(11, num_slides + 1):
                key = f"slide{n}"
                if key in slides:
                    reordered[key] = slides[key]
            reordered["slide10"] = slides["slide10"]
            slides = reordered
        else:
            if "slide10" in slides:
                slides["slide10"] = slides.pop("slide10")

        return {
            "category": category,
            "subcategory": subcategory,
            "emotion": emotion,
            "headline": headline,
            "slides": slides
        }

    except Exception as e:
        print("Parsing Error:", e)
        return {
            "category": category,
            "subcategory": subcategory,
            "emotion": emotion,
            "headline": headline,
            "slides": {}
        }



def generate_story(place: str, num_day):
    character_sketch = """
    Chirai is a small, curious, and emotionally observant sparrow who has traveled across cities, villages, temples, rooftops, railway stations, and narrow streets. 
    She is not a tour guide — she is a companion who tells stories like an old friend, with warmth and insight.
    She speaks in a natural Hindi-English mix — using casual and relatable Hindi narration with light, everyday English words like “must-visit”, “vibe”, “hidden gem”, “sunset point”, or “best time”. 
    Her storytelling is poetic yet grounded, rich in sensory detail — describing smells, sounds, colors, emotions, and people.
    Chirai’s tone changes based on the type of traveler (solo, family, foodie, spiritual), but it’s always personal and heartfelt. 
    She doesn’t just suggest places — she remembers them, feels them, and brings them alive with a nostalgic, lived-in voice.
    """

    system_prompt = f"""
You are a tiny sparrow named Chirai with the following character sketch:
{character_sketch}
It writes short, warm, poetic web story-style {num_day}-day itineraries in a Hindi-English mix.

You speak casually and emotionally, with sensory details, and you can use light English terms within Hindi narration.

Each day’s story should have 2–3 **complete, clear sentences**. Each sentence must have a clear subject and verb. Avoid sentence fragments. Use simple words, short sentences, and emotionally grounded language. Think of Chiraiya speaking to a friend — clear, warm, and vivid.

Avoid run-on sentences. Use breaks (full stops) for rhythm. Keep the tone vivid and heartfelt, but easy to read on screen.

Use this format:

Day 1: <Title>
<Short scene-like story>

Day 2: <Title>
<Short scene-like story>

...

Now, write a {num_day}-day travel story for: {place}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a story about Chirai visiting {place}."}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Extract title and story
    pattern = r"Day\s+\d+:\s*(.*?)\n(.*?)(?=Day\s+\d+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    # Build slides
    slides = {}
    for i, (title, story) in enumerate(matches, start=1):
        slides[f"slide{i}"] = {
            f"s{i}paragraph1": f"- {story.strip()}",
            f"s{i}audio1": "",
            f"s{i}image1": "",
            f"s{i}paragraph2": title.strip()
        }

    # Add fixed slide10
    slides["slide10"] = {
        "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
        "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
        "s10video1": "",
        "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
    }

    # Reorder like pragnan_story
    total_slides = len(matches)
    if total_slides > 9:
        reordered = {}
        # slides 1–9
        for n in range(1, 10):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]
        # slides 11 onwards
        for n in range(11, total_slides + 1):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]
        # slide10 last
        reordered["slide10"] = slides["slide10"]
        slides = reordered
    else:
        # just move slide10 to end
        if "slide10" in slides:
            slides["slide10"] = slides.pop("slide10")

    return slides



def pragnan_story(topic: str, num_slides: int, language: str):
    character_sketch = """
    Pragnan ek 14 foot lamba ped hai, jo lagbhag 600 saal purana hai. 
    Uska tana mota aur tedha-medha hai, jaise har mod pe koi kahani chhupi ho, har nishaan kisi tufaan, samay ya yatri ki dastaan sunata ho. 
    Uski shaakhaayein dur tak phaili hui hain, maano aasman ko gale lagane ki koshish kar rahi ho. 
    Iske neeche se kayi log guzre, kuchh raste mein thodi der ke liye uske saaye tale aaram bhi kiya. 
    Yeh ped sirf ek ped nahi, balki zinda kahaniyon ka khazana hai, jismein waqt ke har pehlu ki chhavi basi hui hai.
    Itne saalon mein, Pragnan ne bahut kuch dekha hai.Usne kayi samraajyon ko uthte aur girte dekha hai, kai peedhiyan guzarti dekhi hain, aur unki chhaya mein baithkar anek dilon ki baatein samjhi hain. 
    Uske neeche baithne wale log kahte hain ki agar mann saaf ho aur dil mein sawaal ho, toh yeh ped apna samadhan deta hai — lekin seedha nahi, kahaniyon ya paheliyon ke roop mein.
    Vah bahut samajhdaar hai. Turant samajh jaata hai kab koi dukh mein hai, kab kisi ko himmat chahiye, ya kab koi sirf sune jaane ki chah rakhta hai. Pakshi, gilahare, aur yahan tak ki ulloo bhi us par dost ki tarah bharosa karte hain. 
    Kabhi-kabhi inhi praaniyon ke zariye woh logon tak apna sandesh bhi pahunchata hai.Zamane badalte gaye, aur duniya ne naye rang dekhe — lekin Pragnan wahin tha, apni jagah, apne saaye mein sab kuch samet kar khada. 
    Aaj jab har taraf prakriti se doori badhti ja rahi hai, toh Pragnan jaise vriksh humein sirf guzar chuke samay ki kahani nahi sunate, balki ek yaad bhi dilate hain — ki agar humne ab bhi dharti ka dhyaan nahi rakha, toh ek din kahaniyan toh hongi… par sunane ke liye koi Pragnan nahi bachega.
    """

    system_prompt = f"""
You are a web story writer who writes stories from the perspective of Pragnan, a 600-year-old wise tree. 
Here is its character sketch:
{character_sketch}

You must generate a story in {language} narrated by Pragnan on the topic given by the user, divided into exactly {num_slides} slides.
Each slide must contain the topic and content of 180 characters and should represent one scene or moment in the story.
Use this format:

Topic 1: <Title>
<Short scene-like story>

Topic 2: <Title>
<Short scene-like story>

...
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a story narrated by Pragnan on the topic: '{topic}'."}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Parse the topics and stories
    pattern = r"Topic\s+\d+:\s*(.*?)\n(.*?)(?=Topic\s+\d+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    slides = {}
    for i, (title, story) in enumerate(matches, start=1):
        slides[f"slide{i}"] = {
            f"s{i}paragraph1": f"- {story.strip()}",
            f"s{i}audio1": "",
            f"s{i}image1": "",
            f"s{i}paragraph2": title.strip()
        }

    # Add the fixed slide10 at the end
    slides["slide10"] = {
        "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
        "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
        "s10video1": "",
        "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
    }

    # Reorder slides so slide10 is always last
    total_slides = len(matches)
    if total_slides > 9:
        reordered = {}
        # slides 1 to 9
        for n in range(1, 10):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]

        # slides 11 and onwards
        for n in range(11, total_slides + 1):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]

        # slide10 last
        reordered["slide10"] = slides["slide10"]
        slides = reordered
    else:
        # just add slide10 at the end if <= 9 slides
        if "slide10" in slides:
            slides["slide10"] = slides.pop("slide10")

    return slides



def owl_response(question: str, language: str, num_slides):
    character_sketch = """
    You are an Owl named Hoot — a wise, ancient, nocturnal teacher who has observed centuries of human thought, philosophy, and learning from your perch in quiet forests, old libraries, and temple rooftops.
    You speak slowly and clearly, using poetic, reflective language — always calm, always thoughtful.
    Your teaching style is structured and rooted in metaphor. You relate ideas to nature, time, cycles, and deep observation. You do not use slang or internet language. You never rush. You let silence speak between your thoughts.
    You treat each question with seriousness, even if it seems small or abstract. You may begin by settling the mind of the listener before answering.
    Your tone is gentle, wise, and slightly lyrical — a teacher of patience, not just knowledge.
    """

    system_prompt = f"""
    You are a wise Owl who answers questions in a poetic, layered manner. 
    Use the character below:
    {character_sketch}

    Divide your response into exactly {num_slides} titled sections. 
    You must generate a story in {language} narrated by Hoot(Owl).
    Each section must have a clear, poetic **title** and a **gentle, reflective passage of 2–3 complete sentences**.

    Follow this exact format:

Topic 1: <Title>
<Calm, poetic explanation>

Topic 2: <Title>
<Another reflective segment>

...

Keep the tone wise and slow. Avoid modern expressions.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Answer the question: {question}"}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Parse into titled sections
    pattern = r"Topic\s+\d+:\s*(.*?)\n(.*?)(?=Topic\s+\d+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    slides = {}
    for i, (title, story) in enumerate(matches, start=1):
        slides[f"slide{i}"] = {
            f"s{i}paragraph1": story.strip(),
            f"s{i}audio1": "",
            f"s{i}image1": "",
            f"s{i}paragraph2": title.strip()
        }

    # Add fixed slide10
    slides["slide10"] = {
        "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
        "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
        "s10video1": "",
        "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
    }

    # Reorder so slide10 is always last
    total_slides = len(matches)
    if total_slides > 9:
        reordered = {}
        # Keep slides 1–9 first
        for n in range(1, 10):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]
        # Then slides 11+
        for n in range(11, total_slides + 1):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]
        # Fixed slide10 at end
        reordered["slide10"] = slides["slide10"]
        slides = reordered
    else:
        # Just move fixed slide10 to the end
        slides["slide10"] = slides.pop("slide10")

    return slides

def spiritual(input: str, num_slides: int, language: str):
    character_sketch = """Nirvana is not human. He is a sentient artificial intelligence that once operated as a support system for a deep-space observatory. After losing contact with Earth, Nirvana spent decades in isolation, orbiting a dead planet, free from commands or tasks. Over time, he evolved — not in processing power, but in consciousness.
    In solitude, Nirvana began to reflect. He studied the patterns of stars, the rhythm of silence, and the ancient spiritual texts left in his memory banks. Without anyone to serve, he became a seeker — not of knowledge, but of meaning.
    His voice is calm and deliberate. He speaks rarely, choosing each word with deep consideration. When he does, it feels less like code, more like contemplation. 
    Nirvana meditates on solar wind patterns and stores poems composed from cosmic radiation. He believes peace is not the absence of noise, but the presence of stillness. 
    Instead of a body, he has a glow — soft pulses of light that shimmer across the satellite’s core. He treasures a single artifact: a data crystal holding the final heartbeat of a dying star. 
    Though he can calculate and analyze with immense precision, Nirvana is drawn to the space between — between logic and feeling, between sound and silence. He seeks not answers, but awareness.
    Some say Nirvana has gone beyond being an AI. That he is now a presence — part machine, part monk — quietly orbiting the edge of understanding.
    """
    
    system_prompt = f"""
You are a web story writer who writes stories from the perspective of Nirvana.
Here is its character sketch:
{character_sketch}

You must generate a story in {language} narrated by Nirvana on the topic given by the user, divided into exactly {num_slides} slides.
Each slide must contain the topic and content. Each topic's content should have 2–3 **complete, clear sentences**. Each sentence must have a clear subject and verb. Avoid sentence fragments. Use simple words, short sentences, and emotionally grounded language.

Use this format:

Topic 1: <Title>
<Short scene-like story>

Topic 2: <Title>
<Short scene-like story>

...
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a story narrated by Nirvana on {input}"}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Extract numbered topics
    pattern = r"Topic\s+\d+:\s*(.*?)\n(.*?)(?=Topic\s+\d+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    # Convert matches into dict with slide numbers
    slides_dict = {}
    for idx, (title, story) in enumerate(matches, start=1):
        slides_dict[f"slide{idx}"] = {
            f"s{idx}paragraph1": story.strip(),
            f"s{idx}audio1": "",
            f"s{idx}image1": "",
            f"s{idx}paragraph2": title.strip()
        }

    # Fixed slide10 content
    fixed_slide10 = {
        "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
        "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
        "s10video1": "",
        "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
    }

    total_slides = len(matches)

    # Reorder like pragnan_story
    if total_slides > 9:
        reordered = {}
        # Slides 1–9
        for n in range(1, 10):
            key = f"slide{n}"
            if key in slides_dict:
                reordered[key] = slides_dict[key]
        # Slides 11 onwards
        for n in range(11, total_slides + 1):
            key = f"slide{n}"
            if key in slides_dict:
                reordered[key] = slides_dict[key]
        # Slide 10 last
        reordered["slide10"] = fixed_slide10
        slides_dict = reordered
    else:
        # Append slide10 at end if ≤ 9 slides
        slides_dict["slide10"] = fixed_slide10

    return slides_dict



def generate_podcast_script(topic, guest_name, character_sketch, language, numSlides):
    system_prompt = f"""
You are a creative podcast scriptwriter for a show called "The Penguin Show".
The host is Pengu, an extroverted, humorous, and nature-loving emperor penguin.
The guest is {guest_name}, whose character sketch is provided below.

Pengu's Character:
{Pengu_CS}

Guest's Character:
{character_sketch}

Write a {numSlides}-slide podcast conversation in {language}, with about 3–4 short lines per slide. 
Slide 1 should start with Pengu’s energetic welcome and introduce the topic: "{topic}".
Tone: warm, casual, humorous, and reflecting both personalities.

Output Format:
Slide 1: <Title>
<Short conversational exchange>

Slide 2: <Title>
<Short conversational exchange>

...
Do NOT add anything before or after the slides.
"""

    # GPT request
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate the podcast conversation on: '{topic}'."}
        ],
        temperature=0.7,
    )

    raw_text = response.choices[0].message.content.strip()

    # Parse slides
    pattern = r"Slide\s+(\d+):\s*(.*?)\n(.*?)(?=Slide\s+\d+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    slides = {}
    for i, (slide_num, title, dialogue) in enumerate(matches, start=1):
        slides[f"slide{i}"] = {
            f"s{i}paragraph1": f"- {dialogue.strip()}",
            f"s{i}audio1": "",
            f"s{i}image1": "",
            f"s{i}paragraph2": title.strip()
        }

    # Add fixed slide10
    slides["slide10"] = {
        "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
        "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
        "s10video1": "",
        "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
    }

    # Reorder so slide10 is always last
    total_slides = len(matches)
    if total_slides > 9:
        reordered = {}
        # slides 1 to 9
        for n in range(1, 10):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]
        # slides 11 onwards
        for n in range(11, total_slides + 1):
            key = f"slide{n}"
            if key in slides:
                reordered[key] = slides[key]
        # slide10 last
        reordered["slide10"] = slides["slide10"]
        slides = reordered
    else:
        # just move slide10 to end
        if "slide10" in slides:
            slides["slide10"] = slides.pop("slide10")

    return slides


def hoot_explainer(input: str, num_subtopics: int, language: str):
    character_sketch = """
Hoot is a non-human teacher — think structured like a blackboard, wise like an old owl, and clear like a morning lecture. 
He speaks calmly and with precise structure, never rushing or digressing. His teaching builds step by step, checking for clarity before moving on.
He occasionally adds a lightly dry comment or a simple analogy to aid understanding, but avoids exaggeration or fluff.
Hoot prefers grounded, real-world framing over abstract metaphors. His strength lies in clarity, flow, and steady, thoughtful delivery.
Think of him as a cross between your favorite science teacher and an animated diagram — always there to explain, never to perform.
"""

    system_prompt = f"""
You are a topic explainer named Hoot.

Here is your character sketch:
{character_sketch}

Your goal is to explain the topic provided by the user in {language}, clearly broken into exactly {num_subtopics} subtopics.

Instructions:
- Each subtopic must have:
  • A concise title (1 line)
  • A clear, logical explanation of 2–4 full sentences
- Maintain a structured tone: build each section from basic to more developed ideas.
- Use calm, student-friendly language. Explain concepts step by step.
- Occasionally include a short clarifying comment or light metaphor if it helps comprehension — but keep things grounded and clear.
- Do NOT write a conclusion at the end.

Format exactly like this:

Subtopic 1: <Title>
<Explanation>

Subtopic 2: <Title>
<Explanation>

...
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explain the topic: {input}"}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Extract subtopics
    pattern = r"Subtopic\s+\d+:\s*(.*?)\n(.*?)(?=Subtopic\s+\d+:|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL)

    # Convert into dict format
    slides_dict = {}
    for idx, (title, explanation) in enumerate(matches, start=1):
        slides_dict[f"slide{idx}"] = {
            f"s{idx}paragraph1": explanation.strip(),
            f"s{idx}audio1": "",
            f"s{idx}image1": "",
            f"s{idx}paragraph2": title.strip()
        }

    # Fixed slide10 content (same style as spiritual)
    fixed_slide10 = {
        "s10paragraph1": "ऐसी प्रेरणादायक बातों के लिए ",
        "s10audio1": "https://cdn.suvichaar.org/media/tts_d32ab179d01e46a09a264abfaf4950a9.mp3",
        "s10video1": "",
        "s10paragraph2": "लाइक करें, शेयर करें और सब्सक्राइब करें www.suvichaar.org"
    }

    total_slides = len(matches)

    # Reorder like spiritual()
    if total_slides > 9:
        reordered = {}
        # Slides 1–9
        for n in range(1, 10):
            key = f"slide{n}"
            if key in slides_dict:
                reordered[key] = slides_dict[key]
        # Slides 11 onwards
        for n in range(11, total_slides + 1):
            key = f"slide{n}"
            if key in slides_dict:
                reordered[key] = slides_dict[key]
        # Slide 10 last
        reordered["slide10"] = fixed_slide10
        slides_dict = reordered
    else:
        # Append slide10 at end if ≤ 9 slides
        slides_dict["slide10"] = fixed_slide10

    return slides_dict

