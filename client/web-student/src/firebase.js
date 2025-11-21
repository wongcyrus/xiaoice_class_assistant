import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyAJPv12AFv8L5KZpN3M0DUndDWVtt2wWYA",
  authDomain: "xiaoice-class-assistant.firebaseapp.com",
  projectId: "xiaoice-class-assistant",
  storageBucket: "xiaoice-class-assistant.firebasestorage.app",
  messagingSenderId: "621615798732",
  appId: "1:621615798732:web:fc7cf940b12334b1a0e569"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getFirestore(app, "xiaoice");
