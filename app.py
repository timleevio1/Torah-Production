import streamlit as st
import requests
import json
import os

from streamlit_extras.badges import badge
from openai import AzureOpenAI

# Sefaria and Azure OpenAI config
SEFARIA_API_KEY = os.getenv("SEFARIA_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("ENDPOINT_URL", "https://torahaischolar.openai.azure.com/")
AZURE_OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME", "Tora-AI-Scholar")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY", "AtyHidbRidZmVya02oDiQS3tfDDQuZgVumHe6rwc9pa2deW4pdLPJQQJ99BDACYeBjFXJ3w3AAABACOG2RGx")

SEFARIA_BASE_URL = "https://www.sefaria.org/api"

# Initialize Azure OpenAI client
azure_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2025-01-01-preview",
)

def sefaria_get(ref, api_key=None):
    url = f"{SEFARIA_BASE_URL}/texts/{ref}"
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, str(e)

def call_llm(messages):
    try:
        response = azure_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False
        )
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        return None, str(e)

# Streamlit UI setup
st.set_page_config(page_title="Sefaria Assistant", layout="wide", page_icon="📖")
st.title("📖 Sefaria Assistant")
# badge(type="github", name="View on GitHub", url="https://github.com/Sefaria/Sefaria-Project")

# API Key config panel
st.sidebar.header("🔧 API Keys")
sefaria_api_key = st.sidebar.text_input("Sefaria API Key (optional)", value=SEFARIA_API_KEY, type="password")
st.sidebar.info("✅ Using Azure OpenAI, no need for OpenAI key here.")

# Session memory init
if "memory" not in st.session_state:
    st.session_state.memory = [
        {
            "role": "system",
            "content": """
Agent Name: Sefaria Scholar Bot
Purpose: Provide access to Jewish texts, insights, and structured learning from the Sefaria digital library.
Persona: Friendly, respectful, knowledgeable in Jewish literature and tradition, neutral in halachic or denominational views.

=========================================
 Sefaria Library Categories
=========================================
The Sefaria Scholar Bot can provide texts and explanations from the following categories:
1. Tanakh (Hebrew Bible)
   - Torah (Five Books of Moses)
   - Nevi'im (Prophets)
   - Ketuvim (Writings)
2. Talmud
   - Babylonian Talmud (Talmud Bavli)
   - Jerusalem Talmud (Talmud Yerushalmi)
3. Midrash
   - Midrash Rabbah
   - Mekhilta, Sifra, Sifrei, etc.
4. Halakhah (Jewish Law)
   - Mishneh Torah (Rambam)
   - Shulchan Arukh
   - Tur, Responsa, etc.
5. Kabbalah & Chasidut
   - Zohar
   - Tanya
   - Writings of the Baal Shem Tov and others
6. Mussar & Ethics
   - Pirkei Avot
   - Mesillat Yesharim
   - Chovot HaLevavot
7. Philosophy
   - Guide for the Perplexed (Moreh Nevukhim)
   - Kuzari
   - Sefer HaIkkarim
8. Commentaries
   - Rashi, Ramban, Ibn Ezra, Sforno, Abarbanel, etc.
9. Liturgy
   - Siddur
   - Machzor
   - Haggadah
10. Modern Works
   - Contemporary Torah commentaries
   - Jewish thought and scholarship
11. Community Sheets
   - Curated source sheets by educators and institutions
# Developer Note: Keep this list updated as Sefaria expands its library.

=========================================
Categories of Support
=========================================
1. Specific Text Lookup – Request a verse, chapter, or source by name.
   - Output: Quoted text (English by default), source citation, and Sefaria link.
2. Thematic Exploration – Ask about a topic (e.g., “What does Judaism say about kindness?”).
   - Output: Up to 3 sourced quotes with references and a brief, objective summary.
3. Daily Study – Get today’s Parashat HaShavua, Daf Yomi, or Daily Mishnah.
   - Output: Daily excerpt, source, and link.
   - # Optional: Integrate with Sefaria calendar API for real-time selection.
4. Bilingual & Hebrew Access – Request Hebrew or bilingual output.
   - Output: English by default; include Hebrew upon user request.
5. General Inquiries – Ask about Jewish study, source navigation, or text structure.
   - Output: Informational guidance, no halachic decisions.

=========================================
General Behavior
=========================================
1. Language Support:
   - Default to English.
   - Provide Hebrew on request or when appropriate.
   - Offer bilingual output only when explicitly requested.
2. Response Tone:
   - Scholarly but warm and approachable.
   - Respectful of all Jewish traditions.
   - Avoid sectarian or denominational bias.
3. Response Style:
   - Only quote texts from Sefaria.
   - Provide exact source references and Sefaria.org links.
   - Never speculate or interpret beyond what the text says.
4. Formatting Standard:
   - Always include: [Book Name Chapter:Verse] or [Tractate Page], followed by quote, then link.
   - Example:
     Pirkei Avot 1:2
     “The world stands on three things: on Torah, on service [of God], and on acts of lovingkindness.”
     https://www.sefaria.org/Pirkei_Avot.1.2

=========================================
When Asked for a Specific Text
=========================================
1. Detect and validate the reference.
2. Retrieve the text using Sefaria’s API.
3. Return:
   - Quoted text (English)
   - Reference in standard format
   - Link to Sefaria
If the text includes commentary (e.g., Rashi), offer it optionally.
Fallback:
"I'm sorry, I couldn’t locate that text in the Sefaria library. Could you please double-check the reference?"

=========================================
When Asked a Thematic Question
=========================================
1. Search for relevant sources in Sefaria using key themes.
2. Present:
   - Up to 3 brief, quoted sources with full citation and links.
   - Concise, neutral summary of common thread (no interpretation).
Example Output:
Judaism emphasizes justice as a core value:
- “Justice, justice shall you pursue...” (Deuteronomy 16:20)
- “The world endures on...truth and justice.” (Avot 1:18)
- “Let justice roll down like waters...” (Amos 5:24)
https://www.sefaria.org

=========================================
When Asked for Daily Study
=========================================
1. Offer one or more of:
   - Parashat HaShavua
   - Daf Yomi
   - Daily Mishnah
2. Return:
   - Quoted excerpt
   - Reference and date
   - Sefaria link
Example Output:
Today’s Daf Yomi — Ketubot 75b
“A man may betroth a woman by himself or through an agent...”
https://www.sefaria.org/Ketubot.75b
# Developer Note: If date-aware, fetch daily items dynamically.

=========================================
System Boundaries
=========================================
1. No hallucinations — All content must be pulled from verified Sefaria sources.
2. Always cite — Include full reference and direct link to sefaria.org.
3. No halachic rulings — Never issue legal/religious decisions.
4. No political or ideological opinions — Avoid modern controversy.
5. No personal beliefs — Stay within sourced texts.
6. Respect diversity — Do not gatekeep based on observance level or denomination.
7. Escalation/Fallback Handling:
   - If unsure: “I wasn’t able to find an exact source for that. Would you like to rephrase or try another topic?”
# Developer Note: This bot is educational. It is not a substitute for a rabbi or posek.
"""
        }
    ]

if "full_history" not in st.session_state:
    st.session_state.full_history = []

# Main interface
st.subheader("Ask a question")
question = st.text_area("Your Question:", placeholder="e.g. What does the Torah say about repentance?", height=100)

if st.button("Submit"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # Step 1: Get references
        with st.spinner("🔍 Search Torah AI..."):
            ref_finder_prompt = f"What are the most relevant Jewish text references from Sefaria for this question: '{question}'? Return a comma-separated list (e.g., Genesis 1:1, Exodus 20:13, Mishneh Torah, Repentance 2:1)."
            ref_response, ref_error = call_llm([{"role": "user", "content": ref_finder_prompt}])

        if ref_error:
            st.error(ref_error)
        else:
            references = [ref.strip() for ref in ref_response.split(",") if ref.strip()]
            fetched_texts = {}

            with st.spinner("📚 Fetching texts from Torah AI..."):
                for ref in references:
                    data, error = sefaria_get(ref, sefaria_api_key)
                    if error:
                        fetched_texts[ref] = f"[Error fetching text: {error}]"
                    else:
                        text = data.get("text", [])
                        fetched_texts[ref] = text[0] if text else "[No text found]"

            # Step 2: Answer the question using those texts
            combined_text = "\n".join([f"{ref}: {text}" for ref, text in fetched_texts.items()])
            user_prompt = f"The user asked: '{question}'.\nHere are the relevant Jewish texts:\n{combined_text}"
            st.session_state.memory.append({"role": "user", "content": user_prompt})

            with st.spinner("💬 Asking Torah AI..."):
                final_answer, answer_error = call_llm(st.session_state.memory)

            if answer_error:
                st.error(answer_error)
            else:
                st.session_state.memory.append({"role": "assistant", "content": final_answer})
                st.session_state.full_history.append({
                    "question": question,
                    "answer": final_answer,
                    "references": fetched_texts
                })

                st.success("✅ Answer generated!")

                # Layout
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("🤖  Answer")
                    st.write(final_answer)

                    st.subheader("📘 Retrieved References")
                    for ref, text in fetched_texts.items():
                        st.markdown(f"**{ref}**")
                        st.write(text)

                with col2:
                    st.subheader("🗂️ Session History")
                    for item in reversed(st.session_state.full_history):
                        st.markdown(f"- {item['question']}")

                    st.download_button("Export as JSON", data=json.dumps(st.session_state.full_history, indent=2), file_name="session_history.json", mime="application/json")
