import re, csv, io
from dotenv import load_dotenv
load_dotenv()  # must be before importing models

import streamlit as st
from models import get_generator
def autocorrect_text(txt: str) -> str:
    # light, rule-based helper for common marketing typos
    fixed = txt
    fixed = re.sub(r"\bproduct lunch\b", "product launch", fixed, flags=re.I)
    return fixed

def enforce_n_lines(candidates: list[str], n: int) -> list[str]:
    # pad or trim to exactly n
    out = [s.strip().rstrip(" ,.;:!-") for s in candidates if s.strip()]
    # remove leading/trailing quotes
    out = [s.strip('"\''"”’") for s in out]
    # de-dup case-insensitively
    seen, uniq = set(), []
    for s in out:
        k = s.lower()
        if k not in seen:
            seen.add(k); uniq.append(s)
    # pad with simple fallbacks if needed
    while len(uniq) < n:
        uniq.append(f"Your update is here {len(uniq)+1}")
    return uniq[:n]

 # <-- loads .env into environment
# ---- Page/UI setup ----
st.set_page_config(page_title="Email Subject Generator", page_icon="📧")
st.title("📧 Email Subject Line Generator — Free & Shareable")
st.write("Paste your email content below. I’ll generate concise, catchy subject lines.")

with st.sidebar:
    st.header("⚙️ Options")
    tone = st.selectbox("Tone", ["Default","Friendly","Professional","Urgent","Playful","Curious","Luxury","Minimal"])
    count = st.slider("How many subject lines?", 3, 12, 6)
    word_limit = st.slider("Max words per subject", 4, 14, 8)
    temperature = st.slider("Creativity (temperature)", 0.1, 1.2, 0.8, 0.1)
    seed = st.number_input("Seed (optional)", min_value=0, value=0)

email_content = st.text_area(
    "Email Content", height=240,
    placeholder="Example: We're launching a new productivity app with a 30% discount..."
)

col1, col2 = st.columns(2)
with col1:
    go = st.button("Generate ✨", use_container_width=True)
with col2:
    if st.button("Clear", use_container_width=True):
        st.experimental_rerun()

# ---- CSV helper ----
@st.cache_data(show_spinner=False)
def _csv_download(rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Subject Line"])
    writer.writerows([[r] for r in rows])
    return buf.getvalue()

# ---- Prompt builder ----
def build_prompt(content: str, tone: str, count: int, word_limit: int, include_kw: str = "", allow_emojis: bool = True) -> str:
    tone_txt = "" if tone == "Default" else f" Tone: {tone}."
    emoji_rule = "" if allow_emojis else " Do not use emojis."
    kw_rule = f" Include these terms if natural: {include_kw}." if include_kw.strip() else ""
    return (
        "You are a world-class email copywriter. Return ONLY a numbered list with no explanations. "
        f"Write {count} distinct subject lines; each must be under {word_limit} words.{tone_txt}{emoji_rule}{kw_rule}\n\n"
        "Avoid spammy words and ALL CAPS. Vary structure and hooks.\n\n"
        f"EMAIL BODY:\n{content}\n\nSUBJECT LINES:\n"
    )


# ---- Cleaner ----
def clean_subjects(text: str, word_limit: int) -> list:
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        s = re.sub(r"^[\-\•\*\s]*", "", s)        # leading bullets
        s = re.sub(r"^[0-9]+[\).:\-\s]+", "", s)  # leading numbering
        s = s.strip(" \t-•·—")
        if not s:
            continue
        words = s.split()
        if len(words) > word_limit:
            s = " ".join(words[:word_limit])
        if len(s) > 120:
            continue
        lines.append(s)

    seen, out = set(), []
    for s in lines:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out

# ---- Generate on click ----
# ...inside: if go:  (replace that block)
if go:
    if not email_content.strip():
        st.warning("Please paste your email content first.")
    else:
        with st.spinner("Thinking… (using local Ollama)"):
            generator = get_generator(temperature=temperature, seed=int(seed) if seed else None)

            # NEW: autocorrect obvious typos
            clean_input = autocorrect_text(email_content)

            # (optional) keep your existing build_prompt; this uses the same signature
            prompt = build_prompt(clean_input, tone, count, word_limit)

            # Give a bit more headroom so lists don't get cut
            max_out = min(240, count * (word_limit + 8))
            raw = generator(prompt, max_new_tokens=max_out)

        if raw.startswith("[Error]"):
            st.error(raw)
        else:
            # parse + NEW: enforce exactly N lines
            subjects = clean_subjects(raw, word_limit)
            subjects = enforce_n_lines(subjects, count)

            if not subjects:
                st.error("No subjects were produced. Try increasing words or temperature.")
            else:
                st.subheader("✨ Suggested Subject Lines")
                for i, s in enumerate(subjects, 1):
                    st.write(f"{i}. {s}")

                csv_data = _csv_download(subjects)
                st.download_button("Download CSV", data=csv_data, file_name="subject_lines.csv", mime="text/csv")


st.caption("Runs on a small open-source chat model (CPU). First run may take ~30–60s to download weights.")
