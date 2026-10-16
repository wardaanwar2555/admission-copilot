"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const num = (v: FormDataEntryValue | null) => (v === null || v === "" ? null : Number(v));

export default function Apply() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault(); setBusy(true); setError("");
    const f = new FormData(e.currentTarget);
    try {
      const { id } = await api("/applications", { method: "POST", body: JSON.stringify({
        name: f.get("name"), email: f.get("email"), program: f.get("program"), gender: f.get("gender") || null, region: f.get("region") || null,
        gpa: num(f.get("gpa")), gre: num(f.get("gre")), toefl: num(f.get("toefl")), sop: num(f.get("sop")), lor: num(f.get("lor")),
        research: num(f.get("research")), univ_rating: num(f.get("univ_rating")), essay: f.get("essay") }) });
      const file = f.get("doc") as File;
      if (file && file.size) {
        const fd = new FormData(); fd.append("file", file);
        await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/applications/${id}/documents`, { method: "POST", body: fd });
      }
      api(`/applications/${id}/process`, { method: "POST" });   // agents run in the background of this request
      router.push(`/status/${id}`);
    } catch (err: any) { setError(err.message); setBusy(false); }
  }

  return (
    <form onSubmit={submit}>
      <h1>Apply to a graduate program</h1>
      <p className="muted">Your application is reviewed by AI agents and then by a person. You can follow every step.</p>
      <div className="grid">
        <div><label htmlFor="name">Full name</label><input id="name" name="name" required /></div>
        <div><label htmlFor="email">Email</label><input id="email" name="email" type="email" required /></div>
        <div><label htmlFor="program">Program</label><select id="program" name="program"><option>MS_CS</option><option>MS_DS</option><option>MBA</option></select></div>
      </div>
      <div className="grid">
        <div><label htmlFor="gpa">GPA (0–4)</label><input id="gpa" name="gpa" type="number" step="0.01" min="0" max="4" /></div>
        <div><label htmlFor="gre">GRE (260–340)</label><input id="gre" name="gre" type="number" min="260" max="340" /></div>
        <div><label htmlFor="toefl">TOEFL (0–120)</label><input id="toefl" name="toefl" type="number" min="0" max="120" /></div>
        <div><label htmlFor="sop">Statement strength (1–5)</label><input id="sop" name="sop" type="number" step="0.5" min="1" max="5" /></div>
        <div><label htmlFor="lor">Recommendation strength (1–5)</label><input id="lor" name="lor" type="number" step="0.5" min="1" max="5" /></div>
        <div><label htmlFor="univ_rating">Undergrad university tier (1–5)</label><input id="univ_rating" name="univ_rating" type="number" min="1" max="5" /></div>
        <div><label htmlFor="research">Research experience</label><select id="research" name="research"><option value="0">No</option><option value="1">Yes</option></select></div>
      </div>
      <div className="grid">
        <div><label htmlFor="gender">Gender (optional, used only for fairness audits)</label><select id="gender" name="gender"><option value="">Prefer not to say</option><option>F</option><option>M</option><option>X</option></select></div>
        <div><label htmlFor="region">Region (optional, fairness audits only)</label><input id="region" name="region" /></div>
      </div>
      <label htmlFor="essay">Statement of purpose</label><textarea id="essay" name="essay" rows={8} />
      <label htmlFor="doc">Transcript or CV (PDF or TXT)</label><input id="doc" name="doc" type="file" accept=".pdf,.txt,.docx" />
      {error && <div className="flag" role="alert">{error}</div>}
      <button disabled={busy}>{busy ? "Submitting…" : "Submit application"}</button>
    </form>
  );
}
