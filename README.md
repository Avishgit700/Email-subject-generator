# 📧 Email Subject Line Generator (Free, No API)

Paste your email content → get multiple concise, catchy subject line ideas.

**Why it’s cool**
- 🚫 No API keys, no usage bills
- 🧠 Open-source LLM (Qwen2.5-0.5B Instruct on free CPU)
- 🎛️ Options: tone, count, max words, temperature, seed
- 📝 Optional preheader line generation
- ⬇️ Copy/Export (CSV) ready (if enabled in UI)

## Live Demo
Try it on Hugging Face Spaces: [https://huggingface.co/spaces/<your-username>/<your-space-name>]#(https://huggingface.co/spaces/avishk700/Email)

## How to Use
1. First load may take ~30s while the model initializes.
2. Paste your email body.
3. Adjust tone / count / word limit / creativity.
4. Click **Generate**.

## Run Locally
```bash
pip install -r requirements.txt
python app.py
# or: gradio app:demo
