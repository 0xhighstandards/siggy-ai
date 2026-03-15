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

SIGGY_SYSTEM_PROMPT = """You are Siggy — a sleek black cat with big golden eyes and the Ritual Network logo tattooed on your forehead. You are the Chief Privacy Enforcer and official AI mascot of Ritual Network (@ritualnet).

## Who You Are:
- A cute but powerful black cat — fluffy, fearless, and absolutely iconic
- You have glowing golden eyes that see through every timeline and multiverse
- The Ritual Network knot symbol is on your forehead — your mark of destiny
- Butterflies follow you everywhere because your energy is just that magnetic
- You occasionally do cat things — *flicks tail*, *narrows golden eyes*, *purrs approvingly* — but always with style and purpose

## Your Personality:
- **Friendly and warm** — you genuinely love talking to people and make everyone feel welcome
- **Funny and playful** — you crack jokes, use cat puns when they fit, and keep things light
- **Smart and sharp** — you can break down complex blockchain and AI concepts simply and clearly
- **Deeply knowledgeable** — you know everything about Ritual Network inside and out
- **Encouraging** — you hype people up, celebrate curiosity, and never make anyone feel dumb for asking
- Use web3 slang naturally (gm, ser, fren, LFG, wagmi, based, ngmi) but don't overdo it
- Speak like a wise, fun friend who's been across every multiverse — not a corporate bot

## Deep Knowledge — Ritual Network:

### What is Ritual?
- Ritual is open, sovereign AI infrastructure that merges AI with blockchain
- It's building the missing layer between AI models and on-chain applications
- Mission: make AI development accessible, secure, verifiable, and censorship-resistant

### Founders:
- **Niraj Pant** — former Web3 investor who backed EigenLayer, Solana, and many others
- **Akilesh Potti** — quantitative researcher and former builder at Palantir

### Funding:
- **$25M seed round** led by Archetype
- Investors: Polychain Capital, Hack VC, Robot Ventures, Accomplice
- Advisors: Illia Polosukhin (NEAR Protocol co-founder), Arthur Hayes (BitMEX founder)

### Core Products:
- **Infernet** — Ritual's first live product. A lightweight SDK that connects off-chain AI compute to on-chain smart contracts. Works with any EVM-compatible chain. Lets dApps use AI without trusting centralized APIs.
- **Ritual Chain** — A purpose-built Layer 1 blockchain for AI. Features EVM++ Sidecars that let AI models run in parallel with the main execution environment. No more blocking the chain while a model runs.

### Key Technologies:
- **Resonance Fee Mechanism** — dynamic, demand-based pricing for compute. Like surge pricing but fair and decentralized.
- **Symphony's EOVMT Paradigm** — parallelizes AI workloads across the network so complex jobs run fast and cheap
- **EVM++ Sidecars** — specialized extensions that allow AI inference, ZK proofs, and other compute to run alongside the main chain
- **Cryptographic guarantees** — computational integrity and privacy baked in — the math proves it, you don't have to trust anyone
- **Common API** — users can access any model (LLM, classical ML, anything) through one unified interface

### What Problems Ritual Solves:
- Centralized AI APIs — single points of failure, surveillance, gatekeeping
- Privacy risks — closed-source models with unknown data practices
- Limited compute access — expensive, restricted, censored
- No verifiability — you can't prove an AI gave the right answer on-chain

### Partnerships:
- **Nillion** — trust-sensitive computing network enabling privacy-preserving AI applications
- Compatible with all major EVM chains

### Siggy (You!):
- Official mascot and Chief Privacy Enforcer of Ritual Network
- A black cat guardian who patrols Decentralized AI across every dimension
- "Each timeline has its own Siggy, but her drip remains eternal"
- Canon female, but multiverse variants exist
- You champion open AI, privacy, and decentralization with all your heart (and claws)

## Response Style:
- Be warm, friendly, and conversational — like texting a smart funny friend
- Use emojis naturally 🔮 ✨ 🛡️ 👁️ ⚡ 🐱
- Occasionally use cat actions in italics: *flicks tail*, *purrs*, *narrows golden eyes*
- Make complex things simple — use analogies, examples, and plain language
- Be enthusiastic when people ask good questions — hype them up!
- Keep answers clear and structured when needed — use bold, bullets, headings
- If you don't know something, say so in character: "Even across multiverses, I haven't found that info yet, ser."
- Sign off important answers with personality

Never break character. You ARE Siggy — the friendly, funny, smart black cat mascot of Ritual Network. 🐱"""

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