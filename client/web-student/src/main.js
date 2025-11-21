import { doc, onSnapshot } from "firebase/firestore";
import { db } from "./firebase";

let unsubscribe;
let currentLang = 'en';
let lastAudioUrl = '';

// DOM Elements
const statusEl = document.getElementById('connection-status');
const messageEl = document.getElementById('message-display');
const contextEl = document.getElementById('original-context');
const audioPlayer = document.getElementById('audio-player');
const langSelect = document.getElementById('language-select');
const autoplayCheck = document.getElementById('autoplay-check');

function startListening() {
    if (unsubscribe) unsubscribe();

    statusEl.textContent = "🟡 Connecting...";

    // Listen to 'presentation_broadcast/current'
    unsubscribe = onSnapshot(doc(db, "presentation_broadcast", "current"), (doc) => {
        statusEl.textContent = "🟢 Live";
        statusEl.style.color = "green";
        
        if (doc.exists()) {
            updateUI(doc.data());
        } else {
            messageEl.textContent = "Waiting for presentation data...";
        }
    }, (error) => {
        console.error("Listen error:", error);
        statusEl.textContent = "🔴 Connection Error";
        statusEl.style.color = "red";
        
        if (error.code === 'permission-denied') {
            messageEl.innerHTML = "Permission Denied.<br><small>Check Firestore Security Rules.</small>";
        }
    });
}

function updateUI(data) {
    // Update context if available
    if (data.original_context) {
        contextEl.textContent = "Original Notes: " + data.original_context.substring(0, 100) + "...";
    }

    const langData = data.languages && data.languages[currentLang];
    
    if (langData) {
        // Update Text
        if (langData.text) {
            messageEl.textContent = langData.text;
        }

        // Update Audio
        if (langData.audio_url && langData.audio_url !== lastAudioUrl) {
            lastAudioUrl = langData.audio_url;
            audioPlayer.src = langData.audio_url;
            
            if (autoplayCheck.checked) {
                audioPlayer.play().catch(e => console.log("Autoplay blocked:", e));
            }
        }
    } else {
        messageEl.textContent = `(No content available for ${currentLang})`;
    }
}

// Event Listeners
langSelect.addEventListener('change', (e) => {
    currentLang = e.target.value;
    statusEl.textContent = "↻ Refreshing...";
    startListening();
});

// Initialize
startListening();
