import "./globals.css";
import Link from "next/link";
export const metadata = { title: "Admissions Copilot" };
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en"><body>
      <nav><strong>Admissions Copilot</strong><Link href="/">Apply</Link><Link href="/reviewer">Reviewer</Link><Link href="/admin">Analytics</Link></nav>
      <main>{children}</main>
    </body></html>
  );
}
