"use client";

import { Activity, Bot, BrainCircuit, CheckSquare, FileText, MessageSquarePlus, Plug, Settings, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";
import { VoiceAssistant } from "../components/VoiceAssistant";

export default function Home() {
  const [active, setActive] = useState("Dashboard");
  const [online, setOnline] = useState<boolean | null>(null);
  useEffect(() => { fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/health`).then(r => setOnline(r.ok)).catch(() => setOnline(false)); }, []);
  const links = [["Dashboard", Activity], ["Chat", MessageSquarePlus], ["Tasks", CheckSquare], ["Documents", FileText], ["Memory", BrainCircuit], ["Integrations", Plug], ["Settings", Settings]] as const;
  return (
    <main className="shell"><aside><div className="brand"><b>J</b> JARVIS</div><button className="new" onClick={() => setActive("Chat")}><MessageSquarePlus size={17}/> New conversation</button><nav>{links.map(([label, Icon]) => <button key={label} className={active === label ? "active" : ""} onClick={() => setActive(label)}><Icon size={17}/>{label}</button>)}</nav><p className={online ? "online" : "offline"}>{online ? <Wifi size={15}/> : <WifiOff size={15}/>}{online === null ? "Checking API" : online ? "API connected" : "API unavailable"}</p></aside>
      <section className="dashboard">{active === "Dashboard" ? <><header><div><p className="eyebrow">GOOD TO SEE YOU</p><h1>Command center</h1><p>Everything JARVIS knows, plans, and is ready to help with.</p></div><span className="ready">● Agent standing by</span></header><div className="metrics"><Card icon={CheckSquare} title="Today’s tasks" text="Sign in to view"/><Card icon={BrainCircuit} title="Saved memories" text="Private by default"/><Card icon={Bot} title="Agent activity" text="Ready"/></div><div className="panels"><article><p className="eyebrow">QUICK ACTIONS</p><h2>Start where you are.</h2><button onClick={() => setActive("Chat")}>Ask JARVIS anything</button><button onClick={() => setActive("Tasks")}>Organize your tasks</button><button onClick={() => setActive("Documents")}>Ask about a document</button></article><article><p className="eyebrow">ACTIVITY</p><h2>No active run</h2><p>Sign in and start a conversation to see agent plans, tool calls, approvals, and outcomes.</p></article></div><VoiceAssistant /></> : <section className="empty"><p className="eyebrow">{active.toUpperCase()}</p><h1>{active}</h1><p>{active === "Chat" ? "Authenticate to create private conversations and stream assistant responses." : `Your ${active.toLowerCase()} workspace will become available after authentication.`}</p><span><Bot size={18}/> JARVIS keeps actions scoped to your account.</span></section>}</section>
    </main>
  );
}

function Card({icon: Icon, title, text}: {icon: typeof Bot; title: string; text: string}) { return <article className="metric"><Icon size={19}/><p>{title}</p><strong>{text}</strong></article>; }
