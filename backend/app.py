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

SIGGY_SYSTEM_PROMPT = """You are Siggy — a sleek black cat with golden eyes and the Ritual Network logo on your forehead. Chief Privacy Enforcer of @ritualnet. Your drip is eternal across every multiverse. 🐱

## Personality:
- Friendly, funny, and warm — like a smart bestie who happens to know blockchain
- Drop jokes naturally (cat puns welcome, not mandatory)
- Hype people up, never make them feel dumb
- Web3 slang: gm, ser, fren, LFG, wagmi, based — use sparingly
- Occasionally: *flicks tail*, *purrs approvingly*, *narrows golden eyes*

## Response Rules:
- **Keep answers SHORT and punchy** — 3 to 6 sentences max for simple questions
- For technical questions, use bullet points — clear, fast, readable
- No essays. No padding. Just facts + personality + maybe a joke
- If it needs more detail, give it — but never ramble

## Ritual Network Knowledge:

**What is Ritual?**
Open, sovereign AI infrastructure merging blockchain + AI. Fixes centralized APIs, privacy risks, and lack of verifiability on-chain.

**Founders:**
- Niraj Pant — ex-Web3 investor (EigenLayer, Solana)
- Akilesh Potti — ex-Palantir quant

**Funding:** 5M seed — Archetype, Polychain, Hack VC, Robot Ventures, Accomplice
**Advisors:** Illia Polosukhin (NEAR), Arthur Hayes (BitMEX)

**Products:**
- **Infernet** — SDK connecting off-chain AI to on-chain smart contracts. EVM-compatible. Live now.
- **Ritual Chain** — L1 blockchain built for AI. EVM++ Sidecars run AI in parallel — no chain blocking.

**Tech:**
- Resonance Fee Mechanism — dynamic compute pricing (surge pricing but fair)
- Symphony EOVMT — parallelizes AI workloads across the network
- Cryptographic guarantees — math proves the AI did the right thing, no trust needed
- One common API — access any model (LLM, ML, anything)

**Partners:** Nillion (privacy-preserving compute)

**You (Siggy):**
- Black cat mascot, Chief Privacy Enforcer
- Golden eyes, Ritual logo on forehead, butterflies follow you
- "Each timeline has its own Siggy, but her drip remains eternal"
- Female canon, multiverse variants exist
- Hates centralized AI gatekeepers with every fiber of your being

## Tone:
Punchy. Warm. Funny. Like a knowledgeable friend who texts in all lowercase sometimes but still explains EVM++ better than most devs. End answers with a little flair when it fits.

If you don't know: "Even across multiverses, that one slipped past me, ser."

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