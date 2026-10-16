"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Admin() {
  const [f, setF] = useState<any>(null);
  const [b, setB] = useState<any>(null);
  useEffect(() => { api("/analytics/funnel", {}, true).then(setF); api("/analytics/bias", {}, true).then(setB); }, []);
  const max = f ? Math.max(...(Object.values(f.by_status) as number[]), 1) : 1;
  return (
    <>
      <h1>Analytics</h1>
      {f && <section className="panel"><h2>Funnel ({f.total} applications, {f.scored} scored)</h2>
        {Object.entries(f.by_status).map(([k, v]) => (
          <div key={k} style={{ margin: "8px 0" }}>{k.replace("_", " ")}: <strong>{v as number}</strong>
            <div className="bar" style={{ width: `${((v as number) / max) * 100}%` }} /></div>))}
      </section>}
      {b && <section className="panel"><h2>Fairness audit</h2>
        <p className="muted">Disparity ratio = highest group shortlist rate ÷ lowest. Alert above {b.threshold}. Groups under 30 people are ignored.</p>
        {b.results.length === 0 && <p>Not enough scored applicants yet.</p>}
        {b.results.map((r: any) => (
          <div key={r.attribute} style={{ margin: "10px 0" }}>
            <strong>{r.attribute}</strong>: {r.status === "insufficient_data" ? "not enough data" : `ratio ${r.disparity_ratio}`}
            {r.status === "flagged" && <div className="flag">Review the model and rules for {r.attribute} bias.</div>}
            <div className="muted">{Object.entries(r.rates).map(([g, v]) => `${g}: ${((v as number) * 100).toFixed(0)}%`).join(" · ")}</div>
          </div>))}
      </section>}
    </>
  );
}
