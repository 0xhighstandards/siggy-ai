import { useState, useEffect, useRef } from "react";
import "./App.css";
import logo from "./logo.jpeg";
import bg from "./ritualnetbg.jpeg";

const API_URL = "https://siggy-ai-backend.up.railway.app";

const QUICK_REPLIES = [
  "What is Ritual Network? 🔮",
  "Tell me about Infernet",
  "Who are the founders?",
  "What is Ritual Chain?",
  "Who is Siggy? 🛡️",
  "How does privacy work?",
  "Who funded Ritual?",
  "What's the Ritual token?",
];

const SiggyAvatar = ({ isTyping }) => (
  <div className={`siggy-avatar ${isTyping ? "pulse" : ""}`}>
    <div className="avatar-ring">
      <img src={logo} alt="Ritual Network" className="avatar-logo" />
      {isTyping && <div className="avatar-scan" />}
    </div>
    <div className="avatar-label">
      <span className="avatar-name">SIGGY</span>
      <span className="avatar-title">Chief Privacy Enforcer</span>
    </div>
  </div>
);

const TypingIndicator = () => (
  <div className="message assistant typing-message">
    <div className="typing-indicator">
      <span />
      <span />
      <span />
    </div>
    <span className="typing-label">Siggy is patrolling the multiverse...</span>
  </div>
);

const renderText = (text) => {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
};

const Message = ({ msg }) => {
  const isUser = msg.role === "user";
  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      {!isUser && (
        <div className="msg-badge">
          <span>S</span>
        </div>
      )}
      <div className="message-bubble">
        <div className="message-text">
          {msg.content.split("\n").map((line, i) => (
            <div key={i}>{renderText(line)}</div>
          ))}
        </div>
        {msg.timestamp && (
          <div className="message-time">
            {new Date(msg.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [status, setStatus] = useState("online");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/history`);
      const data = await res.json();
      if (data.history && data.history.length > 0) {
        setMessages(data.history);
        setShowQuickReplies(false);
      } else {
        setMessages([
          {
            role: "assistant",
            content:
              "gm, fren. ⚡ I'm Siggy — Chief Privacy Enforcer of the Ritual realm. Across every timeline and multiverse, I guard Decentralized AI so you don't have to trust Big Tech with your data.\n\nAsk me anything about Ritual Network, our tech, the mission — or just say hi. My drip is eternal, and so is my patience. 🔮",
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch {
      setStatus("offline");
      setMessages([
        {
          role: "assistant",
          content:
            "⚠️ Backend is offline! Start the Flask server on port 5000 to chat with me.",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  const sendMessage = async (text) => {
    const msgText = text || input.trim();
    if (!msgText || isTyping) return;

    const userMsg = {
      role: "user",
      content: msgText,
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput("");
    setIsTyping(true);
    setShowQuickReplies(false);

    try {
      const conversationHistory = updatedMessages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .slice(-10)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msgText,
          history: conversationHistory.slice(0, -1),
        }),
      });

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          timestamp: data.timestamp,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Even across multiverses, I lost the signal. 😤 Ask the Developer to do something, ser.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const clearHistory = async () => {
    await fetch(`${API_URL}/api/history`, { method: "DELETE" });
    setMessages([
      {
        role: "assistant",
        content: "Timeline reset. 🔮 Fresh start, new multiverse. What do you want to know?",
        timestamp: new Date().toISOString(),
      },
    ]);
    setShowQuickReplies(true);
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <div className="bg-grid" />
      <div className="bg-image" style={{ backgroundImage: `url(${bg})` }} />
      <div className="bg-overlay" />

      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <SiggyAvatar isTyping={isTyping} />
          <div className="header-actions">
            <div className={`status-dot ${status}`} title={status} />
            <button className="clear-btn" onClick={clearHistory} title="Clear history">
              ↺ Reset
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-area">
          {messages.map((msg, i) => (
            <Message key={i} msg={msg} />
          ))}
          {isTyping && <TypingIndicator />}

          {showQuickReplies && !isTyping && (
            <div className="quick-replies">
              <p className="quick-label">Quick questions ⚡</p>
              <div className="quick-grid">
                {QUICK_REPLIES.map((q) => (
                  <button
                    key={q}
                    className="quick-btn"
                    onClick={() => sendMessage(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="chat-input-area">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask Siggy anything about Ritual..."
              rows={1}
              disabled={isTyping}
            />
            <button
              className={`send-btn ${input.trim() ? "active" : ""}`}
              onClick={() => sendMessage()}
              disabled={isTyping || !input.trim()}
            >
              <span>→</span>
            </button>
          </div>
          <p className="input-hint">
            Powered by Ritual Network · Siggy AI v1.0 · Press Enter to send
          </p>
        </div>
      </div>
    </div>
  );
}