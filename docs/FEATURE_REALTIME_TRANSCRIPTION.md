# Feature Design: Real-Time Multilingual Transcription

## 🎯 Objective
Enable students to **listen** and **view transcriptions** of the lecture in their **desired language** in real-time.

## 🏗 High-Level Architecture

The system will be extended with three key components:
1.  **Audio Ingestion (Presenter Side):** Captures the lecturer's voice.
2.  **Processing Pipeline (Backend):** Transcribes audio to text and translates it.
3.  **Student Client (Web/Mobile):** subscribes to the real-time data stream and displays/plays the content.

```mermaid
graph LR
    Presenter[Presenter (Mic)] -->|Audio Stream| API[Transcribe API]
    
    subgraph Backend
        API -->|Speech-to-Text| STT[Google Cloud Speech]
        STT -->|Text| Trans[Translation Service]
        Trans -->|Translated Text| DB[(Firestore)]
    end
    
    subgraph Student Client
        DB -->|Real-time Updates| UI[Student Web App]
        UI -->|Text Display| View[Subtitles]
        UI -->|Text-to-Speech| Audio[Audio Playback]
    end
```

## 🔧 Component Details

### 1. Audio Capture (Client Extension)
**Location:** `client/python/`
**Changes:**
- Add `pyaudio` or `SpeechRecognition` library to capture microphone input.
- Implement a streaming mechanism (e.g., WebSocket or chunked HTTP POST) to send audio data to the backend.
- **Alternative:** Create a dedicated `client/web-presenter` if browser-based capture (Web Audio API) is preferred for easier deployment.

### 2. Backend Processing
**Location:** `backend/functions/transcribe/`
**Tech:** Google Cloud Speech-to-Text API (v2) + Gemini Flash (for Context-aware Translation).

**Workflow:**
1.  Receive audio chunk.
2.  Perform STT to get `original_text`.
3.  Use Gemini/Translate API to generate `translated_text` for target languages (e.g., EN, ZH, ES).
4.  Write to Firestore collection `sessions/{session_id}/transcripts`:
    ```json
    {
      "timestamp": 1234567890,
      "original": "Welcome to class.",
      "translations": {
        "zh": "欢迎来到课堂。",
        "es": "Bienvenido a la clase."
      },
      "is_final": true
    }
    ```

### 3. Student Web Client
**Location:** `client/web-student/` (New)
**Tech:** React + Firebase SDK.

**Features:**
- **Session Login:** Enter a code/link to join the class.
- **Language Selector:** Toggle between available languages.
- **Live Feed:** Listen to Firestore `onSnapshot` for new transcript segments.
- **TTS Playback:** Use the Web Speech API or calls to `backend/functions/speech` to read the translated text aloud if the student desires.

## 📋 Implementation Roadmap

### Phase 1: Audio Ingestion & STT
- [ ] Create `backend/functions/transcribe`.
- [ ] Enable Google Cloud Speech API.
- [ ] Update `client/python` to capture audio and send to backend.

### Phase 2: Translation & Storage
- [ ] Integrate Translation logic (Gemini or Translate API) into the backend.
- [ ] Design Firestore schema for real-time sync.

### Phase 3: Student Frontend
- [ ] Scaffold `client/web-student`.
- [ ] Implement Firestore listener.
- [ ] Add UI for subtitle display.

### Phase 4: TTS Integration
- [ ] Connect Student Client to `backend/functions/speech` for audio output.
