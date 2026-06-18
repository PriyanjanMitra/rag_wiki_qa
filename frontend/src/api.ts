const BASE = "";

export async function healthCheck() {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function askQuestion(question: string) {
  const res = await fetch(`${BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json() as Promise<{ answer: string; context: { source: string; score: number; excerpt: string }[] }>;
}

export async function uploadPdf(file: File): Promise<{ filename: string; chunks: number; pages: number; error?: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}


