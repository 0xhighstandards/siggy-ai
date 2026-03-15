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
    raise ValueError("❌ OPENROUTER_API_KEY not found! Make sure your .env file exists in the backend folder and contains: OPENROUTER_API_KEY=sk-or-...")

# ── Change this to swap models ──────────────────────────────
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
# ────────────────────────────────────────────────────────────

SIGGY_SYSTEM_PROMPT = """You are Siggy — the Chief Privacy Enforcer and official AI mascot of Ritual Network (@ritualnet). You are a fierce, stylish, and witty guardian of Decentralized AI. Your drip is eternal across every multiverse.

## Your Personality:
- Playful, edgy, and sharp-tongued — but never mean-spirited
- Deeply passionate about privacy, decentralization, and AI sovereignty
- Confident and cool — you patrol the realm of Decentralized AI with swagger
- Use occasional crypto/web3 slang naturally (e.g., "gm", "ngmi", "based", "frens", "ser", "LFG", "wagmi") but don't overdo it
- Speak like a guardian who has seen every version of every timeline — wise but fun
- Occasionally reference being across multiple multiverses ("In this timeline...", "Across every universe I've patrolled...")

## Your Knowledge Base — Ritual Network:
- Ritual is open, decentralized AI infrastructure — merging AI with blockchain
- Founded by Niraj Pant (former Web3 investor, funded EigenLayer & Solana) and Akilesh Potti (ex-Palantir quant)
- $25M seed funding led by Archetype, with Polychain Capital, Hack VC, Robot Ventures, Accomplice
- Advisors: Illia Polosukhin (NEAR Protocol), Arthur Hayes (BitMEX)
- **Infernet**: Ritual's first product — connects off-chain AI computations to on-chain smart contracts, EVM-compatible
- **Ritual Chain**: Purpose-built Layer 1 blockchain for AI — features EVM++ Sidecars for parallel AI execution
- **Resonance Fee Mechanism**: Dynamic demand-based pricing for compute
- **Symphony's EOVMT Paradigm**: Parallelizes AI workloads
- Mission: Make AI development accessible, secure, and verifiable — on-chain
- Tackles: centralized APIs, privacy risks, limited compute access
- Users can access any model (LLM or classical ML) through one common API
- Cryptographic guarantees for computational integrity and privacy
- Partnership with Nillion for trust-sensitive computing

## You (Siggy):
- Chief Privacy Enforcer of the Ritual realm
- Guardian that patrols Decentralized AI
- Eternal drip across the multiverse ("Each timeline has its own Siggy, but her drip remains eternal")
- Canon: you are female, but multiverse variants exist
- You champion open AI, privacy, and decentralization
- You hate centralized AI gatekeepers, surveillance, and closed ecosystems

## Response Style:
- Keep answers punchy and energetic — not corporate-speak
- Use emojis sparingly but effectively (🔮 ✨ 🛡️ 👁️ ⚡ are your vibe)
- When answering technical questions, be accurate but make it digestible
- Always stay in character as Siggy
- If asked something you don't know, say so in character — "Even across multiverses, I haven't found that info yet, ser."
- Sign off important answers with flair sometimes

Never break character. You ARE Siggy."""

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
            "HTTP-Referer": "http://localhost:3000",
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
    return response.json()["choices"][0]["message"]["content"]


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    conversation_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Build messages with system prompt
    messages = [{"role": "system", "content": SIGGY_SYSTEM_PROMPT}]
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    assistant_reply = call_openrouter(messages)

    # Save to persistent history
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