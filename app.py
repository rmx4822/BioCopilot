import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Bio-Copilot", page_icon="🧬")
st.title("🧬 Bio-Copilot — AI Assistant for Biologists")
st.caption("If this page ever goes blank, the script crashed before rendering. This version surfaces errors below.")

# Read key from Streamlit Secrets (preferred) or env var as fallback
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
if not OPENAI_KEY:
    st.error("OpenAI API key not found. Add it in **Settings → Secrets** as `OPENAI_API_KEY`.")
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)

st.write("Describe a task in plain English. I’ll return Python code (Biopython/Pandas/Matplotlib) plus a short explanation.")

prompt_text = st.text_area("Your task:", placeholder="e.g., Read a FASTA file and plot a histogram of GC content")

if st.button("Generate Code"):
    if not prompt_text.strip():
        st.warning("Please enter a task.")
    else:
        sys = ("You are an expert bioinformatics coding assistant. "
               "Return concise, runnable Python code first in a fenced code block, "
               "using Biopython/Pandas/Matplotlib when appropriate, followed by a one-line explanation. "
               "Avoid extra prose.")
        try:
            with st.spinner("Thinking..."):
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": sys},
                        {"role": "user", "content": f"Task: {prompt_text}"}
                    ],
                )
            content = resp.choices[0].message.content or ""
        except Exception as e:
            st.error("OpenAI API call failed:")
            st.exception(e)
            st.stop()

        if "```" in content:
            parts = content.split("```")
            code_block = parts[1]
            if code_block.startswith("python"):
                code_block = code_block[len("python"):].lstrip("\n")
            st.subheader("Code")
            st.code(code_block, language="python")
            st.subheader("Explanation")
            st.write(parts[-1].strip())
        else:
            st.write(content)


