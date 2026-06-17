import { useState, useRef, useCallback } from "react";
import { askQuestion, askStream, searchQuery } from "./api";
import "./App.css";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<{ source: string; score: number; excerpt: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(true);
  const [searchQueryText, setSearchQueryText] = useState("");
  const [searchResults, setSearchResults] = useState<{ score: number; chunk: string; metadata: Record<string, unknown> }[] | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const handleAsk = useCallback(async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setSources([]);

    if (streaming) {
      try {
        for await (const event of askStream(question)) {
          if (event.type === "context") setSources(event.sources);
          else if (event.type === "token") setAnswer((prev) => prev + event.content);
        }
      } catch (e) {
        setAnswer(`Error: ${e instanceof Error ? e.message : "Unknown error"}`);
      }
    } else {
      try {
        const result = await askQuestion(question);
        setAnswer(result.answer);
        setSources(result.context);
      } catch (e) {
        setAnswer(`Error: ${e instanceof Error ? e.message : "Unknown error"}`);
      }
    }

    setLoading(false);
  }, [question, streaming]);

  const handleSearch = useCallback(async () => {
    if (!searchQueryText.trim()) return;
    try {
      const result = await searchQuery(searchQueryText);
      setSearchResults(result.results);
    } catch (e) {
      console.error(e);
    }
  }, [searchQueryText]);

  return (
    <div className="container">
      <header>
        <h1>RAG Wiki QA</h1>
        <p>Ask questions about your PDF textbooks</p>
      </header>

      <section className="ask-section">
        <h2>Ask a Question</h2>
        <div className="input-row">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="e.g. What is a hash table?"
            disabled={loading}
          />
          <button onClick={handleAsk} disabled={loading || !question.trim()}>
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>
        <label className="toggle">
          <input type="checkbox" checked={streaming} onChange={() => setStreaming((s) => !s)} />
          Stream response
        </label>

        {answer && (
          <div className="answer">
            <h3>Answer</h3>
            <p>{answer}</p>
          </div>
        )}

        {sources.length > 0 && (
          <div className="sources">
            <h3>Sources</h3>
            {sources.map((s, i) => (
              <details key={i}>
                <summary>
                  {s.source} &mdash; score: {s.score.toFixed(3)}
                </summary>
                <blockquote>{s.excerpt}</blockquote>
              </details>
            ))}
          </div>
        )}
      </section>

      <section className="search-section">
        <h2>Search</h2>
        <div className="input-row">
          <input
            value={searchQueryText}
            onChange={(e) => setSearchQueryText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search the index..."
          />
          <button onClick={handleSearch} disabled={!searchQueryText.trim()}>
            Search
          </button>
        </div>

        {searchResults && (
          <div className="results">
            <h3>Results ({searchResults.length})</h3>
            {searchResults.map((r, i) => (
              <div key={i} className="result">
                <div className="score">Score: {r.score.toFixed(3)}</div>
                <pre>{r.chunk.slice(0, 400)}{r.chunk.length > 400 ? "..." : ""}</pre>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
