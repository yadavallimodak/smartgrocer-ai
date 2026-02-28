import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { ShoppingCart, Home, Info, TrendingUp, X, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
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
  { id: "01400943", name: "The Colony, TX · Store #01400943", address: "5225 State Hwy 121, The Colony, TX 75056" },
  { id: "01401234", name: "Prosper, TX · Store #01401234", address: "4709 W University Dr, Prosper, TX 75078" },
  { id: "01401567", name: "Dallas Pkwy, Frisco, TX · Store #01401567", address: "2580 Dallas Pkwy, Frisco, TX 75034" },
  { id: "01401890", name: "Ohio Dr, Frisco, TX · Store #01401890", address: "5901 Ohio Dr, Frisco, TX 75035" },
  { id: "01402100", name: "Lewisville, TX · Store #01402100", address: "2350 Lake Vista Dr, Lewisville, TX 75067" },
  { id: "01402350", name: "Carrollton, TX · Store #01402350", address: "750 E Hebron Pkwy, Carrollton, TX 75010" }
];

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi there! 🤝 I\'m Grocer, your in-store assistant.  \nAsk me where anything is, get recipe help, or find nearby locations!', type: 'chat' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [userLocation, setUserLocation] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [activeTab, setActiveTab] = useState('home');
  const [storeId, setStoreId] = useState('01400943');
  const [storeName, setStoreName] = useState('The Colony, TX · Store #01400943');
  const [storeAddress, setStoreAddress] = useState('5225 State Hwy 121, The Colony, TX 75056');
  const [availableStores, setAvailableStores] = useState(AVAILABLE_STORES);
  const [showStorePicker, setShowStorePicker] = useState(false);
  const [nearbyStores, setNearbyStores] = useState([]);
  const [storeDetectionStatus, setStoreDetectionStatus] = useState('detecting'); // 'detecting' | 'found' | 'not_found' | 'expanded' | 'no_location'
  const [isListening, setIsListening] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true); // auto-read bot responses
  const recognitionRef = useRef(null);
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
      { timeout: 5000, maximumAge: 60000 }
    );
  });

  // Helper to set a store from API data
  const selectStore = (store) => {
    setStoreId(store.store_id);
    const addrParts = (store.address || '').split(',');
    const city = addrParts.length >= 2 ? addrParts[1].trim() : store.name;
    const displayName = `${city} · Store #${store.store_id}`;
    setStoreName(displayName);
    setStoreAddress(store.address);
    if (!AVAILABLE_STORES.find(s => s.id === store.store_id)) {
      setAvailableStores(prev => [{ id: store.store_id, name: displayName, address: store.address }, ...prev]);
    }
  };

  // Search for stores at a given radius
  const searchStores = async (loc, radius) => {
    const res = await fetch(`${API_URL}/api/nearest-store?lat=${loc.lat}&lon=${loc.lon}&radius=${radius}`);
    const data = await res.json();
    return data.stores || [];
  };

  // Expand search to 100 miles and show picker
  const expandSearch = async () => {
    setStoreDetectionStatus('detecting');
    const loc = await getLocation();
    if (!loc) return;
    try {
      const stores = await searchStores(loc, 100);
      if (stores.length > 0) {
        setNearbyStores(stores);
        setStoreDetectionStatus('expanded');
        setShowStorePicker(true);
      } else {
        setStoreDetectionStatus('not_found');
      }
    } catch (e) {
      console.warn('Expanded search failed:', e);
    }
  };

  // Pick a store from the modal
  const pickStore = (store) => {
    selectStore(store);
    setShowStorePicker(false);
    setStoreDetectionStatus('found');
  };

  // Auto-detect the nearest Kroger store on page load (25mi radius)
  useEffect(() => {
    const detectNearestStore = async () => {
      const loc = await getLocation();
      if (!loc) {
        setStoreDetectionStatus('no_location');
        return;
      }
      try {
        const stores = await searchStores(loc, 25);
        if (stores.length > 0) {
          selectStore(stores[0]);
          setStoreDetectionStatus('found');
          console.log(`Auto-detected nearest Kroger: ${stores[0].name} (${stores[0].distance_miles} mi) — ${stores[0].address}`);
        } else {
          setStoreDetectionStatus('not_found');
        }
      } catch (e) {
        console.warn('Could not auto-detect nearest store:', e);
        setStoreDetectionStatus('no_location');
      }
    };
    detectNearestStore();
  }, []);

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

  // ── Voice Input (Speech-to-Text) ───────────────────────────────────
  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;
    recognitionRef.current = recognition;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = (e) => {
      console.warn('Speech recognition error:', e.error);
      setIsListening(false);
    };

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      // Show interim results in the input
      if (interimTranscript) setInputValue(interimTranscript);
      // Auto-send on final
      if (finalTranscript.trim()) {
        setInputValue('');
        sendMessage(finalTranscript.trim());
      }
    };

    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // ── Voice Output (Text-to-Speech) ─────────────────────────────────
  const speakText = (text) => {
    if (!voiceEnabled || !text) return;
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    // Clean markdown/emoji from text for cleaner speech
    const cleanText = text
      .replace(/[#*_~`>\[\]()!]/g, '')
      .replace(/\n+/g, '. ')
      .replace(/📍|🛒|🔍|😕|🕐|🔎|➤|✅|❌|⚠️/g, '')
      .trim();
    if (!cleanText) return;
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    window.speechSynthesis.speak(utterance);
  };

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
          speakText(responseText);
        }, 1500);
      } else {
        setIsTyping(false);
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: responseText,
          type: data.type,
          data: data.response
        }]);
        speakText(responseText);
      }

    } catch {
      setIsTyping(false);
      setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I\'m having trouble connecting to the store network right now. Please try again.', type: 'chat' }]);
      if (voiceEnabled) speakText('Sorry, I\'m having trouble connecting to the store network right now. Please try again.');
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
        <div className="w-[98%] max-w-[1500px] flex justify-between items-center gap-4 bg-transparent p-2 pr-3 pointer-events-auto">
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
              href="https://smartgrocer-ai-tool.vercel.app/dashboard"
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
            <div className="relative group">
              <select
                className="appearance-none bg-transparent text-white py-2 px-4 pr-9 rounded-xl text-sm font-medium focus:outline-none transition-all cursor-pointer truncate max-w-[250px] md:max-w-[400px]"
                value={storeId}
                onChange={handleStoreChange}
                style={{ backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.6rem top 50%', backgroundSize: '0.65rem auto' }}
              >
                {availableStores.map((s) => (
                  <option key={s.id} value={s.id} className="text-gray-900 bg-white">{s.name}</option>
                ))}
              </select>
              {/* Custom tooltip with full address — appears on hover */}
              <div className="absolute top-full right-0 mt-2 px-4 py-2 bg-gray-900/95 text-white text-xs rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-[60] backdrop-blur-sm border border-white/10">
                📍 {availableStores.find(s => s.id === storeId)?.address || 'Address unavailable'}
              </div>
            </div>
            <div className="hidden md:flex items-center gap-1.5 px-3 py-2 bg-transparent text-white rounded-xl text-sm font-semibold flex-shrink-0">
              <span className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
              Online
            </div>
          </div>
        </div>
      </div>

      {/* Store Picker Modal */}
      {showStorePicker && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-[90%] max-w-[500px] max-h-[70vh] overflow-hidden">
            <div className="p-6 bg-gradient-to-r from-[#1e3a5f] to-[#2563eb] text-white">
              <h2 className="text-lg font-bold">Select Your Kroger Store</h2>
              <p className="text-sm text-white/80 mt-1">Found {nearbyStores.length} store{nearbyStores.length !== 1 ? 's' : ''} within 100 miles</p>
            </div>
            <div className="overflow-y-auto max-h-[45vh] p-2">
              {nearbyStores.map((s) => (
                <button
                  key={s.store_id}
                  onClick={() => pickStore(s)}
                  className="w-full text-left p-4 rounded-xl hover:bg-blue-50 transition-all border border-transparent hover:border-blue-200 mb-1 group"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-semibold text-gray-900">{s.name}</span>
                      <span className="text-xs text-gray-500 ml-2">#{s.store_id}</span>
                      <p className="text-sm text-gray-600 mt-0.5">📍 {s.address}</p>
                      {s.hours && <p className="text-xs text-gray-400 mt-0.5">🕐 {s.hours}</p>}
                    </div>
                    <span className="text-sm font-medium text-blue-600 whitespace-nowrap ml-3">{s.distance_miles} mi</span>
                  </div>
                </button>
              ))}
            </div>
            <div className="p-4 border-t border-gray-100">
              <button onClick={() => setShowStorePicker(false)} className="w-full py-2.5 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content Area */}
      <div className="kiosk-content">
        {activeTab === 'home' && isWelcome && (
          <div className={`welcome-screen ${isTransitioning ? 'fade-out' : ''}`}>
            <div className="welcome-content fade-in-up">
              <h1>Hello, welcome to <br />SmartGrocerAI.</h1>
              <p>Find products, discover recipes, and navigate the store instantly.</p>

              {/* Store connection status */}
              {storeDetectionStatus === 'detecting' && (
                <div className="mt-4 px-5 py-3 bg-white/10 backdrop-blur-sm rounded-xl text-white/90 text-sm animate-pulse">
                  🔍 Detecting your nearest Kroger store...
                </div>
              )}
              {storeDetectionStatus === 'found' && (
                <div className="mt-4 px-5 py-3 bg-white/15 backdrop-blur-sm rounded-xl text-white text-sm">
                  <p className="font-semibold">📍 Connected to: {storeName}</p>
                  <p className="text-white/75 text-xs mt-1">{storeAddress}</p>
                </div>
              )}
              {storeDetectionStatus === 'not_found' && (
                <div className="mt-4 px-5 py-3 bg-white/15 backdrop-blur-sm rounded-xl text-white text-sm">
                  <p>😕 No Kroger stores found within 25 miles.</p>
                  <button
                    onClick={expandSearch}
                    className="mt-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-all text-sm font-medium"
                  >
                    🔎 Search within 100 miles
                  </button>
                </div>
              )}
              {storeDetectionStatus === 'no_location' && (
                <div className="mt-4 px-5 py-3 bg-white/15 backdrop-blur-sm rounded-xl text-white text-sm">
                  <p>📍 Location access not available. Using default store.</p>
                  <p className="text-white/75 text-xs mt-1">{storeAddress}</p>
                </div>
              )}

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
              <button
                className={`mic-btn ${isListening ? 'listening' : ''}`}
                onClick={toggleListening}
                aria-label={isListening ? 'Stop listening' : 'Start voice input'}
                title={isListening ? 'Tap to stop' : 'Tap to speak'}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder={isListening ? 'Listening...' : 'Ask me about any product, aisle, or recipe…'}
              />
              <button
                className={`voice-toggle-btn ${voiceEnabled ? 'active' : ''}`}
                onClick={() => { setVoiceEnabled(v => !v); if (voiceEnabled) window.speechSynthesis.cancel(); }}
                aria-label={voiceEnabled ? 'Mute voice responses' : 'Enable voice responses'}
                title={voiceEnabled ? 'Voice responses ON — click to mute' : 'Voice responses OFF — click to enable'}
              >
                {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              </button>
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
