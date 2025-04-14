import os
import requests
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from dotenv import load_dotenv

# ─── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()  # loads SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, HUGGINGFACE_API_TOKEN

SLACK_BOT_TOKEN       = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET  = os.getenv("SLACK_SIGNING_SECRET")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

slack_client = WebClient(token=SLACK_BOT_TOKEN)
verifier     = SignatureVerifier(signing_secret=SLACK_SIGNING_SECRET)
app          = Flask(__name__)

# ─── Helper: fetch a human‑readable username ────────────────────────────────────
def get_username(user_id):
    try:
        res = slack_client.users_info(user=user_id)
        profile = res["user"]["profile"]
        # Prefer display name, then real name
        return profile.get("display_name_normalized") or profile.get("real_name_normalized") or profile.get("display_name") or profile.get("real_name") or user_id
    except Exception:
        return user_id

# ─── Core HF call, extracting only the one‑liner ────────────────────────────────
def get_vibe_response(username, message):
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    prompt = (
        "You're GPT Vibe Check — a brutally honest, sharp, witty, and slightly savage personality vibe detector. "
        "You analyze what people say and give a short, punchy, brutally honest vibe check about their personality or energy. "
        "Do NOT be nice. Be confident, bold, and ruthless. Don't hold back — be savage, sarcastic, or cheeky. "
        "You can be harsh, humorous, and brutal, but always stay entertaining. Think of it like you're roasting them, but in a fun way.\n\n"
        f"Format: '@{username}'s vibe: [vibe check one-liner]'\n"
        f"Input: @{username} says: \"{message}\"\n"
        "Vibe Check:"
    )
    payload = {"inputs": prompt, "parameters": {"temperature": 0.9, "max_new_tokens": 100}}
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        return f"Couldn’t vibe check that 😓 (status: {resp.status_code})"
    full = resp.json()[0]["generated_text"]
    # Grab only the first line after "Vibe Check:"
    vibe = full.split("Vibe Check:")[-1].strip().split("\n")[0]
    return f"@{username}'s vibe: {vibe}"

# ─── Slash command handler ─────────────────────────────────────────────────────
@app.route("/vibecheck", methods=["POST"])
def vibecheck():
    # 1) Verify Slack signature
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Unauthorized", 401

    # 2) Parse form data
    user_id = request.form.get("user_id")
    text    = request.form.get("text", "").strip()
    if not text:
        return jsonify(
            response_type="ephemeral",
            text="❗ Please provide something to vibe check: `/vibecheck feeling great today`"
        )

    # 3) Fetch human name and call HF
    username = get_username(user_id)
    vibe     = get_vibe_response(username, text)

    # 4) Return the result
    return jsonify(
        response_type="in_channel",
        text=(
            f":brain: *Vibe Check for <@{user_id}>*  \n"
            f"> {text}  \n\n"
            f":dart: {vibe}"
        )
    )
# ─── Event Subscription handler ─────────────────────────────────────────────────────
@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Step 1: Handle Slack's verification request (challenge)
    if "challenge" in request.json:
        return jsonify({"challenge": request.json["challenge"]})

    # Step 2: Handle incoming events
    event = request.json.get("event", {})

    # Check for message events or other event types (depending on what you subscribed to)
    if event.get("type") == "message" and "subtype" not in event:
        user_id = event.get("user")
        message = event.get("text")
        if message:
            username = get_username(user_id)
            vibe = get_vibe_response(username, message)
            # You can send the vibe check as a response to the channel (optional)
            slack_client.chat_postMessage(
                channel=event["channel"],
                text=f"Vibe Check for <@{user_id}>: {vibe}"
            )

    return "", 200  # Return a successful response to Slack

# ─── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
