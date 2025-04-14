# GPT Vibe Check Slack Bot 🎭

This is a Slack bot that listens to messages in your workspace and replies empathetically using OpenAI's GPT model. It's meant for fun, support, and general vibes.

---

## 🚀 Features

- Listens to Slack messages using the Events API
- Uses Hugging Face's `OpenAssistant` model for empathetic responses
- Replies only when mentioned or directly messaged

---

## 🧠 Powered By

- **Slack Bolt SDK (Python)**
- **HuggingFace Inference API**
- **Flask** (for webhook routing)

---

## 📦 Installation

### 1. Clone the repo:

```bash
git clone https://github.com/plug999/slack-vibe-bot.git
cd slack-vibe-bot

-------------------------------------------------------------------------------

Create a .env file using the provided .env.example:

cp .env.example .env

SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
HUGGINGFACE_API_TOKEN=your-huggingface-token

-------------------------------------------------------------------------------

 Install dependencies


pip install -r requirements.txt

--------------------------------------------------------------------------------

Run the bot locally


python app.py

--------------------------------------------------------------------------------

Use ngrok to expose your local Flask app:

ngrok http 3000

----------------------------------------------------------------------------------

🌍 Deployment (Render)
Fork or clone this repo

On Render, create a new Web Service

Use Python 3.10 or higher

Add the following Environment Variables in Render Dashboard:

SLACK_BOT_TOKEN

SLACK_SIGNING_SECRET

HUGGINGFACE_API_TOKEN

Set the Start Command as:

gunicorn app:app

----------------------------------------------------------------------------------

🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change.