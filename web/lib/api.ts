export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const WS = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
const KEY = process.env.NEXT_PUBLIC_STAFF_KEY ?? "";

export async function api<T = any>(path: string, init: RequestInit = {}, staff = false): Promise<T> {
  const res = await fetch(API + path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(staff ? { "X-API-Key": KEY } : {}), ...(init.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail ?? `Request failed (${res.status})`);
  return res.json();
}
