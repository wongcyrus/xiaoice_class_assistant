# Student Web Client

A simple web application for students to follow the presentation in real-time.

## Features
- Real-time text updates synced with the presenter's slides.
- Text-to-Speech (TTS) audio playback.
- Language selection (English, Chinese, Spanish, etc.).

## Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Locally**:
   ```bash
   npm run dev
   ```
   Open the local URL (usually `http://localhost:5173`) in your browser.

3. **Build & Deploy**:
   ```bash
   # Build the Vite app
   npm run build
   
   # Deploy to Firebase Hosting
   firebase deploy
   ```

## Configuration

The Firebase configuration is in `src/firebase.js`. 

**Important**: The Firestore Rules (`firestore.rules`) are configured to allow public read access to the `presentation_broadcast` collection.

## Troubleshooting

- **Permission Denied**: Check your Firestore Security Rules in the Firebase Console or `firestore.rules`.
- **Autoplay Blocked**: Browsers often block audio autoplay. You may need to interact with the page (click somewhere) or manually press play for the first audio segment.
