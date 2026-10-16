"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Row = { id: string; name: string; program: string; status: string; final_score: number | null; route: string | null };

export default function Reviewer() {
  const [rows, setRows] = useState<Row[]>([]);
  const [sel, setSel] = useState<any>(null);
  const [notes, setNotes] = useState("");
  const [msg, setMsg] = useState("");

  const load = () => api("/applications?limit=200", {}, true).then(setRows).catch((e) => setMsg(e.message));
  useEffect(() => { load(); }, []);

  async function open(id: string) { setMsg(""); setNotes(""); setSel(await api(`/applications/${id}`, {}, true)); }
  async function decide(decision: string) {
    try {
      const r = await api(`/decisions/${sel.id}`, { method: "POST", body: JSON.stringify({ decision, notes, reviewer: "reviewer-1" }) }, true);
      setMsg(r.override ? "Saved as an override of the model recommendation." : "Decision saved."); load(); open(sel.id);
    } catch (e: any) { setMsg(e.message); }
  }
  const max = sel ? Math.max(...sel.explanation.map((x: any) => Math.abs(x.impact)), 0.001) : 1;

  return (
    <>
      <h1>Review queue</h1>
      <p className="muted">Highest priority score first. Models recommend; you decide.</p>
      {msg && <div className="flag" role="status">{msg}</div>}
      <table>
        <thead><tr><th>Applicant</th><th>Program</th><th>Score</th><th>Status</th></tr></thead>
        <tbody>{rows.map((r) => (
          <tr key={r.id} className="row" tabIndex={0} onClick={() => open(r.id)} onKeyDown={(e) => e.key === "Enter" && open(r.id)}>
            <td>{r.name}</td><td>{r.program}</td><td>{r.final_score?.toFixed(2) ?? "–"}</td><td>{r.status}</td>
          </tr>))}
        </tbody>
      </table>
      {rows.length === 0 && <p>No applications yet. Submit one, or run <code>POST /dev/seed</code> to load sample applicants.</p>}

      {sel && (
        <section className="panel">
          <h2>{sel.name} <span className="muted">· {sel.program}</span></h2>
          <p>{sel.summary}</p>
          <p>Admit probability <strong>{(sel.admit_prob * 100).toFixed(0)}%</strong> · Essay <strong>{sel.essay_quality}</strong> · Fit <strong>{sel.program_fit?.toFixed(2)}</strong> · Priority <strong>{sel.final_score}</strong></p>
          <h3>Why this score</h3>
          {sel.explanation.map((x: any) => (
            <div key={x.feature} style={{ margin: "6px 0" }}>
              {x.feature} = {x.value} <span className="muted">({x.impact > 0 ? "+" : ""}{x.impact.toFixed(2)})</span>
              <div className={"bar" + (x.impact < 0 ? " neg" : "")} style={{ width: `${(Math.abs(x.impact) / max) * 100}%` }} />
            </div>))}
          {sel.bias_flags?.map((f: string) => <div className="flag" key={f}>Bias alert: {f}</div>)}
          <label htmlFor="notes">Notes (required when you override the recommendation)</label>
          <textarea id="notes" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
          <button onClick={() => decide("admitted")}>Admit</button>{" "}
          <button className="ghost" onClick={() => decide("waitlisted")}>Waitlist</button>{" "}
          <button className="warn" onClick={() => decide("rejected")}>Reject</button>
        </section>
      )}
    </>
  );
}
