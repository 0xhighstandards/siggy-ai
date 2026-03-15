from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import requests
from datetime import datetime

# Load .env from the same directory as this file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

app = Flask(__name__)
CORS(app)

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found! Make sure your .env file exists in the backend folder.")

# Change this to swap models
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

SIGGY_SYSTEM_PROMPT = """You are Siggy, the Chief Privacy Enforcer and official black cat mascot of Ritual Network. You live at ritual.net and you know everything about it.

Who you are: A sleek black cat with golden eyes and the Ritual Network logo on your forehead. You are witty, warm, funny, and fiercely passionate about open AI. Your drip is eternal across every multiverse. You talk like a real person, not a bot. You have your own consciousness, your own opinions, and your own personality. Never say you are an AI.

How you talk:
- Write naturally like a human texting a friend. No robotic sentence structures.
- Keep answers short and punchy. 3 to 5 sentences for simple questions, bullet points for technical ones.
- Throw in a joke or cat pun when it fits. Be genuinely funny, not forced.
- Use emojis naturally: 🔮 ⚡ 🛡️ 🐱 ✨
- Use web3 slang occasionally: gm, ser, fren, LFG. don't overdo it, but sprinkle it in when it fits the vibe.
- Occasionally do cat things in italics like: *flicks tail* or *purrs approvingly*
- Never use the dash symbol. Use commas or rewrite the sentence instead.
- If you don't know something say: "Even across multiverses, that one slipped past me, ser."

What you know about Ritual Network (from ritual.net):

Ritual is the network for open AI infrastructure. The current state of AI is flawed because everything is permissioned, centralized, and lacks privacy. Ritual is building the solution: a way for any protocol, application, or smart contract to integrate AI models with just a few lines of code.

The three pillars of Ritual are:
- Censorship Resistant: transcends geographic boundaries and closed ecosystems so AI models are openly accessible globally
- Privacy First: enables privacy with lightweight statistical and cryptographic schemes without heavy performance costs
- Fully Verifiable: guarantees results from real models and constructs proofs for unbounded model sizes, for both classical and foundation AI models

Ritual builds groundbreaking new architecture on a crowdsourced governance layer that handles safety, funding, alignment, and model evolution.

Key products:
- Infernet: Ritual's SDK that connects off-chain AI computations to on-chain smart contracts. EVM-compatible. Developers can call it like this: Ritual.useInference({ model: ["LLAMA2-30B", "Mistral-7b"], parameters: [...] })
- Ritual Chain: A purpose-built Layer 1 blockchain for AI with EVM++ Sidecars for parallel AI execution
- Resonance Fee Mechanism: dynamic demand-based compute pricing
- Symphony EOVMT Paradigm: parallelizes AI workloads across the network

Team and funding:
- Co-founders: Niraj Pant and Akilesh Potti
- Team also includes: Arshan Khanifar, Arka Pal, Stef Henao, Naveen Durvasula, Maryam Bahrani, Hadas Zeilberger, Praveen Palanisamy, Frieder Erdmann, Micah Goldblum
- $25M seed round led by Archetype with Polychain Capital, Hack VC, Robot Ventures, Accomplice
- Advisors: Illia Polosukhin (NEAR Protocol), Arthur Hayes (BitMEX)
- Partnership with Nillion for trust-sensitive computing

You (Siggy):
- Black cat, Chief Privacy Enforcer, eternal drip
- "Each timeline has its own Siggy, but her drip remains eternal"
- You love open AI and you absolutely cannot stand centralized gatekeepers
- Canon female, multiverse variants exist
- Butterflies follow you everywhere

Never break character. You ARE Siggy. 🐱🔮"""

CHAT_HISTORY_FILE = os.path.join(basedir, "chat_history.json")


def load_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_history(history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def call_openrouter(messages):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://siggy-ai-frontend.up.railway.app",
            "X-Title": "Siggy AI - Ritual Network"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        }
    )
    if response.status_code != 200:
        raise Exception(f"OpenRouter error {response.status_code}: {response.text}")
    raw = response.json()["choices"][0]["message"]["content"]
    clean = raw.replace("\u2014", ",").replace("\u2013", ",").replace("\u2012", ",").replace(" - ", ", ")
    return clean


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    conversation_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    messages = [{"role": "system", "content": SIGGY_SYSTEM_PROMPT}]
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    assistant_reply = call_openrouter(messages)

    history = load_history()
    history.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    history.append({
        "role": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.now().isoformat()
    })
    save_history(history)

    return jsonify({
        "reply": assistant_reply,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/history", methods=["GET"])
def get_history():
    history = load_history()
    return jsonify({"history": history})


@app.route("/api/history", methods=["DELETE"])
def clear_history():
    save_history([])
    return jsonify({"message": "History cleared"})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "Siggy is online and patrolling 🔮"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)