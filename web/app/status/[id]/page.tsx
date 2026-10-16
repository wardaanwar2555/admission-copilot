"use client";
import { useEffect, useState } from "react";
import { WS } from "@/lib/api";

const STEPS = ["submitted", "under_review", "shortlisted", "admitted"];

export default function Status({ params }: { params: { id: string } }) {
  const [s, setS] = useState<{ status: string; interview_slot?: string } | null>(null);
  useEffect(() => {
    const ws = new WebSocket(`${WS}/ws/status/${params.id}`);
    ws.onmessage = (m) => setS(JSON.parse(m.data));
    return () => ws.close();
  }, [params.id]);
  const idx = s ? STEPS.indexOf(s.status) : -1;
  return (
    <>
      <h1>Application {params.id}</h1>
      <p className="muted">This page updates by itself.</p>
      <div className="steps" aria-label="Progress">
        {STEPS.map((st, i) => <span key={st} className={"step" + (i <= idx ? " on" : "")}>{st.replace("_", " ")}</span>)}
      </div>
      {s && idx < 0 && <p>Current status: <strong>{s.status}</strong></p>}
      {s?.interview_slot && <div className="panel">Interview proposed for <strong>{new Date(s.interview_slot).toUTCString()}</strong>. Check your email for the link.</div>}
      {!s && <p>Connecting…</p>}
    </>
  );
}
