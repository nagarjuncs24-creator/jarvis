"use client";
import { useState } from "react";
import { signIn, type Session } from "../lib/api";
export function LoginForm({ onSession }: { onSession: (s: Session) => void }) { const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [error,setError]=useState(""); return <form onSubmit={async e=>{e.preventDefault();try{onSession(await signIn(email,password));}catch(e){setError(e instanceof Error?e.message:"Sign in failed");}}}><input aria-label="Email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" type="email" required/><input aria-label="Password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password" required/><button>Sign in</button>{error&&<p role="alert">{error}</p>}</form>; }
