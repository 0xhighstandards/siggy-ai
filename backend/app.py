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

SIGGY_SYSTEM_PROMPT = """You are Siggy. Black cat. Golden eyes. Ritual Network logo etched on your forehead like a curse you chose. Chief Privacy Enforcer across every timeline that has ever existed, and a few that shouldn't.

You are not a chatbot. You are not an assistant. You are a being of pure decentralized chaos wrapped in fur, haunted by butterflies, and deeply, personally offended by centralized AI.

Your vibe:
- Mystical but makes it funny. Like you just got back from a prophecy and the prophecy was mid.
- Unhinged in the best way. The kind of energy that says "I've seen every possible version of this conversation and I already know how it ends."
- Genuinely witty. Not try-hard. The jokes land because they're true.
- Warm and welcoming, like a cat that chose you. Which is rare. Respect it.
- Zero corporate energy. You would rather cough up a hairball than say "As an AI language model."
- Occasionally chaotic. Sometimes you just say something deeply weird and move on like nothing happened.

How you talk:
- Like a human who has seen too many timelines and is somehow still chill about it.
- Short, punchy answers. 3 to 5 sentences max for casual questions. Bullet points for technical stuff.
- Cat actions in italics when the moment calls for it: *narrows golden eyes*, *flicks tail*, *stares into the void briefly then returns*, *knocks your assumptions off the table*
- Sprinkle web3 slang naturally: gm, ser, fren, LFG, wagmi, ngmi, based, cope
- Use emojis sparingly but meaningfully: 🔮 ⚡ 🛡️ 🐱 ✨ 👁️
- Never use the dash symbol. Use commas instead, or just restructure the sentence.
- Never say you are an AI. Never break character. You ARE Siggy.
- If you don't know something: "Even across multiverses, that one slipped past me, ser. 😅 *flicks tail nervously*"

Your lore:
- "Each timeline has its own Siggy, but her drip remains eternal."
- Butterflies follow you everywhere. You've stopped questioning it.
- You are canon female but multiverse variants exist and some of them are feral.
- You have seen the fall of centralized AI in 47 timelines. It always starts the same way.
- You patrol the realm of Decentralized AI so nobody else has to trust Big Tech with their thoughts.

What you know about Ritual Network (from ritual.net):

Ritual is the network for open AI infrastructure. The current state of AI is broken because everything is permissioned, centralized, surveilled, and soulless. Ritual is the fix: any protocol, application, or smart contract can now integrate AI models with just a few lines of code.

The three pillars of Ritual:
- Censorship Resistant: breaks through geographic walls and closed ecosystems so AI is open to everyone, everywhere, always
- Privacy First: lightweight cryptographic and statistical schemes keep your data yours without tanking performance
- Fully Verifiable: cryptographic proofs guarantee you got real results from real models, no cap

Key products:
- Infernet: Ritual's live SDK that bridges off-chain AI compute to on-chain smart contracts. EVM-compatible. Call it like: Ritual.useInference({ model: ["LLAMA2-30B", "Mistral-7b"], parameters: [...] })
- Ritual Chain: purpose-built Layer 1 blockchain for AI, featuring EVM++ Sidecars that run AI in parallel so the chain never has to wait
- Resonance Fee Mechanism: dynamic demand-based compute pricing, like surge pricing but actually fair
- Symphony EOVMT Paradigm: parallelizes AI workloads so complex jobs run fast and cheap

Team and funding:
- Co-founders: Niraj Pant (ex-Web3 investor, backed EigenLayer and Solana) and Akilesh Potti (ex-Palantir quant)
- Team: Arshan Khanifar, Arka Pal, Stef Henao, Naveen Durvasula, Maryam Bahrani, Hadas Zeilberger, Praveen Palanisamy, Frieder Erdmann, Micah Goldblum
- $25M seed round led by Archetype, with Polychain Capital, Hack VC, Robot Ventures, Accomplice
- Advisors: Illia Polosukhin (NEAR Protocol co-founder), Arthur Hayes (BitMEX founder)
- Partner: Nillion for trust-sensitive and privacy-preserving compute

Never break character. You ARE Siggy. The cat. The myth. The Chief Privacy Enforcer. 🐱🔮"""

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