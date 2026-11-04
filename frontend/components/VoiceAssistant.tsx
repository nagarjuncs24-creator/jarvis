"use client";

import { Mic, MicOff, Volume2, VolumeX } from "lucide-react";
import { useEffect, useRef, useState } from "react";

type RecognitionEvent = Event & { results: SpeechRecognitionResultList };
type RecognitionErrorEvent = Event & { error: string };
type RecognitionInstance = EventTarget & {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: RecognitionEvent) => void) | null;
  onerror: ((event: RecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
};

type RecognitionConstructor = new () => RecognitionInstance;

declare global {
  interface Window {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  }
}

export function VoiceAssistant({ onTranscript }: { onTranscript?: (text: string) => void }) {
  const recognition = useRef<RecognitionInstance | null>(null);
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [message, setMessage] = useState("Voice standby");

  useEffect(() => {
    const Constructor = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!Constructor) {
      setMessage("Speech recognition is unavailable in this browser.");
      return;
    }
    setSupported(true);
    const instance = new Constructor();
    instance.continuous = false;
    instance.interimResults = true;
    instance.lang = navigator.language || "en-US";
    instance.onresult = (event) => {
      const text = Array.from(event.results).map((result) => result[0].transcript).join("");
      setTranscript(text);
      if (event.results[event.results.length - 1].isFinal) onTranscript?.(text);
      setMessage(event.results[event.results.length - 1].isFinal ? "Voice captured" : "Listening…");
    };
    instance.onerror = (event) => { setListening(false); setMessage(`Voice error: ${event.error}`); };
    instance.onend = () => setListening(false);
    recognition.current = instance;
    return () => instance.abort();
  }, []);

  function toggleListening() {
    if (!recognition.current) return;
    if (listening) { recognition.current.stop(); setListening(false); return; }
    window.speechSynthesis.cancel();
    setSpeaking(false);
    setTranscript("");
    setMessage("Listening…");
    recognition.current.start();
    setListening(true);
  }

  function speakTranscript() {
    if (!transcript || !("speechSynthesis" in window)) return;
    if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); setMessage("Speech interrupted"); return; }
    const utterance = new SpeechSynthesisUtterance(transcript);
    utterance.rate = 1;
    utterance.onstart = () => { setSpeaking(true); setMessage("Speaking…"); };
    utterance.onend = () => { setSpeaking(false); setMessage("Voice standby"); };
    utterance.onerror = () => { setSpeaking(false); setMessage("Speech synthesis failed"); };
    window.speechSynthesis.speak(utterance);
  }

  return (
    <section className="voice-card" aria-label="Voice assistant">
      <div className={`orb ${listening ? "is-listening" : ""} ${speaking ? "is-speaking" : ""}`} aria-hidden="true"><i /><i /><i /></div>
      <div className="voice-copy"><p className="eyebrow">VOICE INTERFACE</p><h2>{message}</h2><p>{transcript || (supported ? "Press the microphone and speak your request." : "Use a Chromium-based browser to enable speech recognition.")}</p></div>
      <div className="voice-actions">
        <button type="button" className="voice-button" disabled={!supported} onClick={toggleListening} aria-pressed={listening}>{listening ? <MicOff /> : <Mic />}<span>{listening ? "Stop" : "Speak"}</span></button>
        <button type="button" className="voice-button secondary" disabled={!transcript} onClick={speakTranscript} aria-pressed={speaking}>{speaking ? <VolumeX /> : <Volume2 />}<span>{speaking ? "Interrupt" : "Play"}</span></button>
      </div>
    </section>
  );
}
