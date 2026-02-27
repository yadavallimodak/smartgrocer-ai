import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { ShoppingCart, Home, Info, TrendingUp, X } from 'lucide-react';
import './index.css';
import InventoryCard from './components/InventoryCard';
import OutofStockMap from './components/OutofStockMap';
import StoreCard from './components/StoreCard';

const SUGGESTIONS = [
  { icon: '🥛', label: 'Do you have milk?' },
  { icon: '🍅', label: 'Where are tomatoes?' },
  { icon: '📍', label: 'Kroger locations near me' },
  { icon: '🍝', label: 'Ingredients for pasta' },
  { icon: '🥩', label: 'Where is the meat section?' },
];

const AVAILABLE_STORES = [
  { id: "01400943", name: "The Colony, TX · Store #01400943" },
  { id: "01401234", name: "Prosper, TX · Store #01401234" },
  { id: "01401567", name: "Dallas Pkwy, Frisco, TX · Store #01401567" },
  { id: "01401890", name: "Ohio Dr, Frisco, TX · Store #01401890" },
  { id: "01402100", name: "Lewisville, TX · Store #01402100" },
  { id: "01402350", name: "Carrollton, TX · Store #01402350" }
];

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi there! 👋 I\'m your Kroger in-store assistant.  \nAsk me where anything is, get recipe help, or find nearby locations!', type: 'chat' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [userLocation, setUserLocation] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [activeTab, setActiveTab] = useState('home');
  const [storeId, setStoreId] = useState('01400943');
  const [isWelcome, setIsWelcome] = useState(true);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const chatEndRef = useRef(null);

  const API_URL = 'https://smartgrocer-ai.onrender.com';

  const getLocation = () => new Promise((resolve) => {
    if (userLocation) return resolve(userLocation);
    if (!navigator.geolocation) return resolve(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        setUserLocation(loc);
        resolve(loc);
      },
      () => resolve(null),
      { timeout: 3000, maximumAge: 60000 }
    );
  });

  // Heartbeat to dashboard
  useEffect(() => {
    const heartbeat = setInterval(() => {
      fetch(`${API_URL}/api/devices/heartbeat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: 'tablet-001', status: 'online', battery_level: 95 })
      }).catch(() => { });
    }, 10000);
    return () => clearInterval(heartbeat);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    const userQuery = text || inputValue;
    if (!userQuery.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: userQuery, type: 'chat' }]);
    setInputValue('');
    setShowSuggestions(false);
    setIsTyping(true);

    try {
      const loc = await getLocation();
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuery,
          device_id: 'tablet-001',
          lat: loc?.lat ?? null,
          lon: loc?.lon ?? null,
          store_id: storeId,
        })
      });

      const data = await response.json();
      const responseText = typeof data.response === 'string'
        ? data.response
        : (data.response?.message || 'Here is what I found:');

      // Add a simulated delay if the bot is "checking inventory" and returns an item
      if (data.type === 'inventory_item') {
        // Show "Let me check..." message first
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: responseText,
          type: 'chat'
        }]);

        // Keep the typing bubble going for 1.5s
        setTimeout(() => {
          setIsTyping(false);
          // Replace the last message (the "checking..." chat) with the actual inventory result
          setMessages(prev => {
            const newMsgs = [...prev];
            // Overwrite the chat message with the actual inventory payload
            newMsgs[newMsgs.length - 1] = {
              sender: 'bot',
              text: responseText,
              type: data.type,
              data: data.response
            };
            return newMsgs;
          });
        }, 1500);
      } else {
        setIsTyping(false);
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: responseText,
          type: data.type,
          data: data.response
        }]);
      }

    } catch {
      setIsTyping(false);
      setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I\'m having trouble connecting to the store network right now. Please try again.', type: 'chat' }]);
    }
  };

  const handleSend = () => sendMessage();
  const handleChip = (label) => sendMessage(label);

  const renderBotResponse = (msg) => {
    // 1. Render the introductory text bubble (if any)
    const renderTextBubble = () => {
      if (!msg.text) return null;
      return (
        <div className="bot-row mb-3">
          <div className="bot-avatar">🛒</div>
          <div className="message bot w-fit">
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        </div>
      );
    };

    // 2. Render the interactive rich cards without a white background wrapper
    const renderRichContent = () => {
      if (msg.type === 'chat') return null;

      if (msg.type === 'inventory_item') {
        const item = msg.data?.data || msg.data;
        if (!item) return null;
        return (
          <div className="ml-12 mt-1 mb-2" style={{ maxWidth: '100%' }}>
            <InventoryCard item={item} />
          </div>
        );
      }
      if (msg.type === 'inventory_list') {
        const items = msg.data?.data || [];
        if (items.length === 0) {
          return <p className="ml-12 text-gray-500">No matching items found.</p>;
        }
        return (
          <div className="ml-12 mt-1 mb-2 flex flex-col gap-3" style={{ maxWidth: '100%' }}>
            {items.map((item, idx) => <InventoryCard key={idx} item={item} />)}
          </div>
        );
      }
      if (msg.type === 'competitor_redirect') {
        return (
          <div className="ml-12 mt-1 mb-2" style={{ maxWidth: '100%' }}>
            <OutofStockMap response={msg.data} />
          </div>
        );
      }
      if (msg.type === 'store_list') {
        const stores = msg.data?.stores || [];
        if (stores.length === 0) {
          return <p className="ml-12 text-gray-500">No Kroger locations found nearby.</p>;
        }
        const currentStoreId = msg.data?.current_store_id;
        return (
          <div className="ml-12 mt-1 mb-2 flex flex-col gap-3" style={{ maxWidth: '100%' }}>
            {stores.map((store, idx) => <StoreCard key={idx} store={store} currentStoreId={currentStoreId} />)}
          </div>
        );
      }
      return null;
    };

    return (
      <div className="flex flex-col gap-1 w-full">
        {renderTextBubble()}
        {renderRichContent()}
      </div>
    );
  };

  const handleStoreChange = (e) => {
    setStoreId(e.target.value);
  };

  const startTransition = () => {
    setIsTransitioning(true);
    setTimeout(() => {
      setIsWelcome(false);
      setIsTransitioning(false);
    }, 500);
  };

  return (
    <div className="kiosk-container">
      {/* Header */}
      {/* Header Island */}
      <div className="fixed top-5 left-0 right-0 w-full z-50 flex justify-center pointer-events-none px-4 md:px-8">
        <div className="w-[98%] max-w-[1500px] flex justify-between items-center gap-4 bg-transparent p-2 pr-3 pointer-events-auto overflow-hidden">
          {/* Left: Logo */}
          <div className="flex items-center gap-3 pl-2 flex-shrink-0">
            <div className="w-11 h-11 bg-gradient-to-br from-[#10b981] to-[#3b82f6] rounded-2xl flex items-center justify-center shadow-lg border border-white/20">
              <ShoppingCart className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-white font-['Outfit'] drop-shadow-sm pr-2">SmartGrocer</span>
          </div>

          {/* Center: Navigation */}
          <div className="flex items-center gap-4 md:gap-8 p-1.5 flex-shrink-0 hidden sm:flex">
            <button
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all font-medium text-sm ${activeTab === "home" ? "bg-white/10 text-white shadow-sm" : "text-white/80 hover:bg-white/5 hover:text-white"
                }`}
              onClick={() => setActiveTab('home')}
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </button>
            <button
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all font-medium text-sm ${activeTab === "about" ? "bg-white/10 text-white shadow-sm" : "text-white/80 hover:bg-white/5 hover:text-white"
                }`}
              onClick={() => setActiveTab('about')}
            >
              <Info className="w-4 h-4" />
              <span>About</span>
            </button>
            <a
              href="smartgrocer-ai-tool.vercel.app"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 rounded-xl flex items-center gap-2 text-white/80 hover:bg-white/5 hover:text-white transition-all font-medium text-sm"
            >
              <TrendingUp className="w-4 h-4" />
              <span>Analytics ↗</span>
            </a>
          </div>

          {/* Right: Store & Status */}
          <div className="flex items-center gap-3 flex-shrink-1 min-w-0">
            <select
              className="appearance-none bg-transparent text-white py-2 px-4 pr-9 rounded-xl text-sm font-medium focus:outline-none transition-all cursor-pointer truncate max-w-[250px] md:max-w-[400px]"
              value={storeId}
              onChange={handleStoreChange}
              style={{ backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.6rem top 50%', backgroundSize: '0.65rem auto' }}
            >
              {AVAILABLE_STORES.map((s) => (
                <option key={s.id} value={s.id} className="text-gray-900 bg-white">{s.name}</option>
              ))}
            </select>
            <div className="hidden md:flex items-center gap-1.5 px-3 py-2 bg-transparent text-white rounded-xl text-sm font-semibold flex-shrink-0">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
              Online
            </div>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="kiosk-content">
        {activeTab === 'home' && isWelcome && (
          <div className={`welcome-screen ${isTransitioning ? 'fade-out' : ''}`}>
            <div className="welcome-content fade-in-up">
              <h1>Hello, welcome to <br />SmartGrocerAI.</h1>
              <p>Find products, discover recipes, and navigate the store instantly.</p>
              <button
                className="welcome-btn"
                onClick={startTransition}
              >
                Okay, let's go
              </button>
            </div>
          </div>
        )}

        {activeTab === 'home' && !isWelcome && (
          <div className="chat-interface fade-in">
            {/* Chat */}
            <div className="chat-container">
              {messages.map((msg, index) =>
                msg.sender === 'user'
                  ? <div key={index} className="message user">{msg.text}</div>
                  : <React.Fragment key={index}>{renderBotResponse(msg)}</React.Fragment>
              )}

              {/* Typing indicator */}
              {isTyping && (
                <div className="bot-row">
                  <div className="bot-avatar">🛒</div>
                  <div className="typing-indicator">
                    <span /><span /><span />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Suggestion chips */}
            {showSuggestions && (
              <div className="suggestions fade-in-up">
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} className="chip" onClick={() => handleChip(s.label)}>
                    {s.icon} {s.label}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="input-area slide-up">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask me about any product, aisle, or recipe…"
              />
              <button className="send-btn" onClick={handleSend} aria-label="Send">
                ➤
              </button>
            </div>
          </div>
        )}

        {activeTab === 'about' && (
          <div className="fixed inset-0 w-full h-full z-[100] flex items-center justify-center p-4 md:p-8 bg-black/40 backdrop-blur-sm fade-in">
            <div className="relative w-full max-w-[1000px] min-h-[80vh] bg-white/10 backdrop-blur-xl border border-white/20 rounded-[2rem] p-10 md:p-16 shadow-2xl text-white transform transition-all duration-300 scale-100 max-h-[90vh] overflow-y-auto flex flex-col justify-between">
              <button
                onClick={() => setActiveTab('home')}
                className="absolute top-6 right-6 p-4 rounded-full bg-white/10 hover:bg-white/20 transition-colors text-white z-50 cursor-pointer flex items-center justify-center"
              >
                <X className="w-6 h-6 md:w-8 md:h-8" />
              </button>

              <div className="flex flex-col gap-10 md:gap-12">
                <div>
                  <h2 className="text-4xl md:text-5xl font-bold mb-6 drop-shadow-md pr-16 leading-tight">About the Kroger <br className="hidden md:block" />AI Assistant 🍓</h2>
                  <p className="text-xl md:text-2xl text-white/90 leading-relaxed font-medium">
                    Welcome to the future of grocery shopping! This interactive kiosk is powered by Gemini,
                    designed to help you instantly locate products, generate recipes on the fly, and find nearby stores if we're out of stock.
                  </p>
                </div>

                <div>
                  <h3 className="text-3xl font-bold mb-6">Key Features</h3>
                  <ul className="flex flex-col gap-8 w-full">
                    <li className="p-8 bg-black/20 rounded-2xl border-l-[6px] border-emerald-500 text-xl text-white/95 leading-relaxed shadow-inner">
                      <strong className="text-white block mb-3 text-2xl tracking-wide">Smart Product Location </strong>
                      Real-time inventory and precise aisle mapping.
                    </li>
                    <li className="p-8 bg-black/20 rounded-2xl border-l-[6px] border-emerald-500 text-xl text-white/95 leading-relaxed shadow-inner">
                      <strong className="text-white block mb-3 text-2xl tracking-wide">Recipe Engine </strong>
                      Ask for any dish and instantly get the aisle locations for every ingredient.
                    </li>
                    <li className="p-8 bg-black/20 rounded-2xl border-l-[6px] border-emerald-500 text-xl text-white/95 leading-relaxed shadow-inner">
                      <strong className="text-white block mb-3 text-2xl tracking-wide">Multi-Store Awareness </strong>
                      If we don't have it, we'll find the closest Kroger that does.
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>


    </div>
  );
}

export default App;
