import { useState, useEffect, useRef } from "react";
import "./App.css";
import logo from "./logo.jpeg";
import bg from "./ritualnetbg.jpeg";
import siggy from "./siggy.jpeg";

const API_URL = "https://siggy-ai-backend.up.railway.app";

const QUICK_REPLIES = [
  "What is Ritual Network? 🔮",
  "Tell me about Infernet",
  "Who are the founders?",
  "What is Ritual Chain?",
  "Who is Siggy? 🐱",
  "How does privacy work?",
  "Who funded Ritual?",
  "What's the Ritual token?",
];

const SOCIALS = [
  {
    url: "https://twitter.com/ritualnet",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.91-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    ),
  },
  {
    url: "https://discord.gg/AZf5MW2xDm",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057c.002.022.015.043.032.056a19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
      </svg>
    ),
  },
  {
    url: "https://ritual.net",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm7.931 9h-2.764a14.67 14.67 0 0 0-1.227-5.112A8.017 8.017 0 0 1 19.931 11zM12.53 4.027c1.035 1.364 2.427 3.78 2.627 6.973H9.03c.139-2.596.994-5.028 2.451-6.974.172-.01.34-.026.519-.026.179 0 .347.016.53.027zm-3.842.7C7.704 6.618 7.136 8.845 7.03 11H4.069a8.013 8.013 0 0 1 4.619-6.273zM4.069 13h2.974c.136 2.379.665 4.478 1.556 6.23A8.01 8.01 0 0 1 4.069 13zm7.381 6.973C10.049 18.275 9.222 15.896 9.041 13h6.113c-.208 2.773-1.117 5.196-2.603 6.972-.182.012-.364.028-.551.028-.186 0-.367-.016-.55-.027zm4.011-.772c.955-1.794 1.538-3.901 1.691-6.201h2.778a8.005 8.005 0 0 1-4.469 6.201z"/>
      </svg>
    ),
  },
];

const SiggyAvatar = ({ isTyping }) => (
  <div className={`siggy-avatar ${isTyping ? "pulse" : ""}`}>
    <div className="avatar-ring">
      <img src={siggy} alt="Siggy" className="avatar-logo" />
      {isTyping && <div className="avatar-scan" />}
    </div>
    <div className="avatar-label">
      <span className="avatar-name">Siggy</span>
      <span className="avatar-title">Chief Privacy Enforcer</span>
    </div>
  </div>
);

const TypingIndicator = () => (
  <div className="message assistant typing-message">
    <div className="typing-indicator">
      <span /><span /><span />
    </div>
    <span className="typing-label">Siggy is patrolling the multiverse...</span>
  </div>
);

const renderInline = (text) => {
  // First split by URLs, then by markdown
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = text.split(urlRegex);

  return parts.map((part, i) => {
    // If it's a URL, make it clickable
    if (urlRegex.test(part)) {
      return (
        <a key={i} href={part} target="_blank" rel="noreferrer" className="msg-link">
          {part}
        </a>
      );
    }
    // Otherwise parse markdown
    const mdParts = part.split(/(\*\*.*?\*\*|\*.*?\*|`[^`]+`|~~.*?~~)/g);
    return mdParts.map((md, j) => {
      if (md.startsWith("**") && md.endsWith("**"))
        return <strong key={`${i}-${j}`}>{md.slice(2, -2)}</strong>;
      if (md.startsWith("*") && md.endsWith("*"))
        return <em key={`${i}-${j}`}>{md.slice(1, -1)}</em>;
      if (md.startsWith("`") && md.endsWith("`"))
        return <code key={`${i}-${j}`} className="inline-code">{md.slice(1, -1)}</code>;
      if (md.startsWith("~~") && md.endsWith("~~"))
        return <s key={`${i}-${j}`}>{md.slice(2, -2)}</s>;
      return <span key={`${i}-${j}`}>{md}</span>;
    });
  });
};

const renderContent = (content) => {
  const lines = content.split("\n");
  return lines.map((line, i) => {
    if (line.startsWith("### "))
      return <h3 key={i} className="msg-h3">{renderInline(line.slice(4))}</h3>;
    if (line.startsWith("## "))
      return <h2 key={i} className="msg-h2">{renderInline(line.slice(3))}</h2>;
    if (line.startsWith("# "))
      return <h1 key={i} className="msg-h1">{renderInline(line.slice(2))}</h1>;
    if (line.match(/^[-*] /))
      return (
        <div key={i} className="msg-bullet">
          <span className="bullet-dot">▸</span>
          <span>{renderInline(line.slice(2))}</span>
        </div>
      );
    if (line.match(/^\d+\. /)) {
      const num = line.match(/^(\d+)\. /)[1];
      return (
        <div key={i} className="msg-numbered">
          <span className="num-dot">{num}.</span>
          <span>{renderInline(line.slice(num.length + 2))}</span>
        </div>
      );
    }
    if (line.startsWith("> "))
      return <blockquote key={i} className="msg-blockquote">{renderInline(line.slice(2))}</blockquote>;
    if (line.match(/^---+$/))
      return <hr key={i} className="msg-hr" />;
    if (line.trim() === "")
      return <div key={i} className="msg-spacer" />;
    return <p key={i} className="msg-p">{renderInline(line)}</p>;
  });
};

const Message = ({ msg }) => {
  const isUser = msg.role === "user";
  return (
    <div className={`message ${isUser ? "user" : "assistant"}`}>
      {!isUser && (
        <div className="msg-badge-img">
          <img src={siggy} alt="Siggy" />
        </div>
      )}
      <div className="message-bubble">
        <div className="message-text">
          {isUser ? msg.content : renderContent(msg.content)}
        </div>
        {msg.timestamp && (
          <div className="message-time">
            {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </div>
        )}
      </div>
    </div>
  );
};

const ChatModal = ({ onClose, visible }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [status, setStatus] = useState("online");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { fetchHistory(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isTyping]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/history`);
      const data = await res.json();
      if (data.history && data.history.length > 0) {
        setMessages(data.history);
        setShowQuickReplies(false);
      } else {
        setMessages([{
          role: "assistant",
          content: "Gm, I'm Siggy, Chief Privacy Enforcer of the Ritual realm. Across every timeline and multiverse, I help lost souls like you so you don't lose your way on your journey. Ask me anything about Ritual Network, our tech, the mission, or just say hi. My power is eternal, and so is my patience. 😎",
          timestamp: new Date().toISOString(),
        }]);
      }
    } catch {
      setStatus("offline");
      setMessages([{ role: "assistant", content: "⚠️ Backend is offline! Ask the Developer to do something, ser.\n\n*Can Devs do something?* 😭", timestamp: new Date().toISOString() }]);
    }
  };

  const sendMessage = async (text) => {
    const msgText = text || input.trim();
    if (!msgText || isTyping) return;
    const userMsg = { role: "user", content: msgText, timestamp: new Date().toISOString() };
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
        body: JSON.stringify({ message: msgText, history: conversationHistory.slice(0, -1) }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply, timestamp: data.timestamp }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Even across multiverses, I lost the signal. 😤 Ask the Developer to do something, ser.\n\n*Can Devs do something?* 😭", timestamp: new Date().toISOString() }]);
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const clearHistory = async () => {
    await fetch(`${API_URL}/api/history`, { method: "DELETE" });
    setMessages([{ role: "assistant", content: "Timeline reset. 🔮 Fresh start, new multiverse. What do you want to know?", timestamp: new Date().toISOString() }]);
    setShowQuickReplies(true);
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div className={`modal-overlay ${visible ? "modal-visible" : ""}`} onClick={onClose}>
      <div className={`chat-container modal-chat ${visible ? "modal-chat-visible" : ""}`} onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <SiggyAvatar isTyping={isTyping} />
          <div className="header-actions">
            <div className={`status-dot ${status}`} title={status} />
            <button className="clear-btn" onClick={clearHistory}>↺ Reset</button>
            <button className="close-btn" onClick={onClose}>✕</button>
          </div>
        </div>
        <div className="messages-area">
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {isTyping && <TypingIndicator />}
          {showQuickReplies && !isTyping && (
            <div className="quick-replies">
              <p className="quick-label">Quick questions ⚡</p>
              <div className="quick-grid">
                {QUICK_REPLIES.map((q) => (
                  <button key={q} className="quick-btn" onClick={() => sendMessage(q)}>{q}</button>
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
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
            <button className={`send-btn ${input.trim() ? "active" : ""}`} onClick={() => sendMessage()} disabled={isTyping || !input.trim()}>
              <span>→</span>
            </button>
          </div>
          <p className="input-hint">Powered by Ritual Network · Siggy AI v1.0 · Press Enter to send</p>
        </div>
      </div>
    </div>
  );
};

export default function App() {
  const [chatOpen, setChatOpen] = useState(false);
  const [chatVisible, setChatVisible] = useState(false);

  const openChat = () => {
    setChatOpen(true);
    setTimeout(() => setChatVisible(true), 10);
  };

  const closeChat = () => {
    setChatVisible(false);
    setTimeout(() => setChatOpen(false), 300);
  };

  return (
    <div className="app">
      <div className="bg-image" style={{ backgroundImage: `url(${bg})` }} />

      <nav className="landing-nav">
        <div className="nav-logo">
          <img src={logo} alt="Ritual" className="nav-logo-img" />
          <span className="nav-logo-text">RITUAL</span>
        </div>
        <div className="nav-links">
          {SOCIALS.map((s, i) => (
            <a key={i} href={s.url} target="_blank" rel="noreferrer" className="nav-icon-link">
              {s.icon}
            </a>
          ))}
        </div>
      </nav>

      <main className="landing-main">
        <div className="hero-box">
          <div className="hero-top">
            <h1 className="hero-title">
              Siggy <span className="hero-accent">Sovereign AI</span>
            </h1>
            <p className="hero-subtitle">
              Your guide and friendly companion in the Ritual realm. Ask Siggy anything, she helps lost souls navigate the world of decentralized AI.
            </p>
            <p className="hero-lowersubtitle">Ritual Network Key Features</p>
          </div>

          <div className="hero-divider" />

          <div className="hero-pills">
            <div className="hero-pill">Privacy First</div>
            <div className="hero-pill">Censorship Resistant</div>
            <div className="hero-pill">Fully Verifiable</div>
            <div className="hero-pill">EVM Compatible</div>
          </div>

          <div className="hero-grid">
            <div className="hero-grid-item">
              <div>
                <p className="hero-grid-title">Infernet SDK</p>
                <p className="hero-grid-desc">Easily connect off-chain AI to on-chain smart contracts using just a few lines of code.</p>
              </div>
            </div>
            <div className="hero-grid-item">
              <div>
                <p className="hero-grid-title">Ritual Chain</p>
                <p className="hero-grid-desc">A Layer-1 blockchain built for AI with EVM compatibility that can run multiple tasks at the same time.</p>
              </div>
            </div>
            <div className="hero-grid-item">
              <div>
                <p className="hero-grid-title">$25M Seed Round</p>
                <p className="hero-grid-desc">Backed by Archetype, Polychain Capital, Hack VC, and Robot Ventures.</p>
              </div>
            </div>
            <div className="hero-grid-item">
              <div>
                <p className="hero-grid-title">Meet Siggy</p>
                <p className="hero-grid-desc">Our Chief Privacy Enforcer and the official mascot of Ritual Network.</p>
              </div>
            </div>
          </div>

          <div className="hero-divider" />

          <div className="hero-actions">
            <button className="hero-cta" onClick={openChat}>
              <img src={siggy} alt="Siggy" className="cta-avatar" />
              Chat with Siggy
            </button>
            <a href="https://ritual.net/about" target="_blank" rel="noreferrer" className="hero-secondary">
              What is Ritual?
            </a>
          </div>

          <div className="hero-links">
            <a href="https://docs.ritual.net" target="_blank" rel="noreferrer" className="hero-link">Documentation ↗</a>
            <a href="https://ritual.net/careers" target="_blank" rel="noreferrer" className="hero-link">Careers ↗</a>
          </div>
        </div>
      </main>

      <footer className="landing-footer">
        <span>© 2026</span>
        <span className="footer-credit">
          Built by <a href="https://x.com/intent/follow?screen_name=0xhghstndrds" target="_blank" rel="noreferrer" className="footer-name">0xhighstandards</a>
        </span>
        <a href="mailto:hello@ritual.net" className="footer-email">hello@ritual.net</a>
      </footer>

      {chatOpen && <ChatModal onClose={closeChat} visible={chatVisible} />}
    </div>
  );
}