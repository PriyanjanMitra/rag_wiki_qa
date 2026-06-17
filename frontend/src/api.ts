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

export async function* askStream(question: string) {
  const res = await fetch(`${BASE}/ask/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = JSON.parse(line.slice(6));
      if (data.type === "done") return;
      yield data;
    }
  }
}

export async function searchQuery(query: string, k = 3) {
  const res = await fetch(`${BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, k }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json() as Promise<{ results: { score: number; chunk: string; metadata: Record<string, unknown>; index: number }[] }>;
}
