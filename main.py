import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# === Groq Client ===
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# === Scrape content from Narnetix AI website ===
@st.cache_data(show_spinner=False)
def scrape_narnetix_website(url="https://narnetix-ai.onrender.com"):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])
    return text

# === Ask LLaMA3 via Groq ===
def ask_groq(messages):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.7,
        max_tokens=1024
    )
    return response.choices[0].message.content

# === Main App ===
def main():
    st.set_page_config(page_title="Narnetix AI Chatbot", layout="centered")
    st.title("Narnetix AI Chatbot")

    context = scrape_narnetix_website()

    # === Session State for Chat ===
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": f"You are a helpful assistant for Narnetix AI. Use the following context to answer questions: {context}"}
        ]

    # === Tabs ===
    tab1, tab2 = st.tabs(["💬 Chat", "📌 Generate Project Questions"])

    # === Chat Interface ===
    with tab1:
        for msg in st.session_state.chat_history[1:]:  # Skip system prompt
            if msg["role"] == "user":
                st.markdown(
                    f"<div style='color: #1E90FF; font-weight: bold; margin-bottom: 4px;'>🧑 You</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div style='background-color: #1E90FF; color: white; padding: 12px 15px; 
                                border-radius: 12px; margin-bottom: 20px; max-width: 80%;'>
                        {msg['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif msg["role"] == "assistant":
                st.markdown(
                    f"<div style='color: #2E8B57; font-weight: bold; margin-bottom: 4px;'>🤖 Narnetix AI</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div style='background-color: #2E8B57; color: white; padding: 12px 15px; 
                                border-radius: 12px; margin-bottom: 20px; max-width: 80%;'>
                        {msg['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Input field
        user_input = st.chat_input("Type your message here...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                reply = ask_groq(st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    # === Question Generator ===
    with tab2:
        st.subheader("🧠 Generate Basic Project Questions")
        topic = st.text_input("Enter a project or automation topic:")
        if topic:
            with st.spinner("Generating questions..."):
                question_prompt = f"Generate 10 simple and essential questions someone should ask when starting a project or automation about: {topic}"
                questions = ask_groq([
                    {"role": "user", "content": question_prompt}
                ])
                st.markdown(
                    f"""
                    <div style='background-color: #444; color: white; padding: 12px 15px; 
                                border-radius: 12px; margin-top: 15px;'>
                        {questions}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()