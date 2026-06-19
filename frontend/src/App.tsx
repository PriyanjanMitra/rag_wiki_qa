import { useState, useCallback, useEffect, useRef } from "react";
import { askQuestion, uploadPdf, getUploads, deleteUpload } from "./api";
import "./App.css";

function getInitialDark(): boolean {
  const stored = localStorage.getItem("dark-mode");
  if (stored !== null) return stored === "true";
  return true;
}

function SendIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 2L11 13" /><path d="M22 2L15 22L11 13L2 9L22 2Z" />
    </svg>
  );
}

function ChevronIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function SparkleIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3L14.5 9.5L21 12L14.5 14.5L12 21L9.5 14.5L3 12L9.5 9.5Z" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function LoadingDots() {
  return (
    <span className="inline-flex gap-0.5 items-center">
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-[bounce_0.6s_ease-in-out_infinite]" />
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-[bounce_0.6s_ease-in-out_0.15s_infinite]" />
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-[bounce_0.6s_ease-in-out_0.3s_infinite]" />
    </span>
  );
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<{ source: string; score: number; excerpt: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(getInitialDark);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploads, setUploads] = useState<{ filename: string; pages: number; chunks: number }[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchUploads = useCallback(async () => {
    try {
      setUploads(await getUploads());
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("dark-mode", String(dark));
  }, [dark]);

  useEffect(() => { fetchUploads(); }, [fetchUploads]);

  const handleAsk = useCallback(async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const result = await askQuestion(question);
      setAnswer(result.answer);
      setSources(result.context);
    } catch (e) {
      setAnswer(`Error: ${e instanceof Error ? e.message : "Unknown error"}`);
    }

    setLoading(false);
  }, [question]);

  const handleUpload = useCallback(async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus("");
    try {
      const result = await uploadPdf(file);
      if (result.error) {
        setUploadStatus(`Error: ${result.error}`);
      } else {
        setUploadStatus(`Indexed "${result.filename}" — ${result.chunks} chunk(s), ${result.pages} page(s)`);
        await fetchUploads();
      }
    } catch (e) {
      setUploadStatus(`Upload failed: ${e instanceof Error ? e.message : "Unknown error"}`);
    }
    setUploading(false);
    if (fileRef.current) fileRef.current.value = "";
  }, [fetchUploads]);

  return (
    <div className="font-segoe">
      {/* Light background: warm tones — Dark background: deep blue */}
      <div className="fixed inset-0 -z-10
        bg-[linear-gradient(135deg,#e8f0fe,#d4e4f7_30%,#f0e8f8_70%,#fce8e8)]
        dark:bg-[linear-gradient(135deg,#2b5797,#1e3c72_30%,#0a1628_70%,#1a1a2e)]"
      />
      <div className="fixed inset-0 -z-10
        bg-[radial-gradient(ellipse_120%_50%_at_20%_80%,rgba(255,150,50,0.06),transparent_60%),radial-gradient(ellipse_80%_40%_at_80%_20%,rgba(255,200,100,0.08),transparent_50%)]
        dark:bg-[radial-gradient(ellipse_120%_50%_at_20%_80%,rgba(255,255,255,0.05),transparent_60%),radial-gradient(ellipse_80%_40%_at_80%_20%,rgba(100,180,255,0.08),transparent_50%)]"
      />

      <div className="max-w-2xl mx-auto py-3 px-4">

        {/* Glass card base styles: warm light / blue dark */}
        <div className="mb-2 overflow-hidden rounded-lg
          bg-white/60 backdrop-blur-2xl saturate-150 border border-white/80
          shadow-[0_4px_24px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.9)]
          dark:bg-white/8 dark:border-white/15
          dark:shadow-[0_8px_32px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.2)]"
        >
          {/* Title bar: orange light / blue dark */}
          <div className="flex items-center gap-2 px-3 py-1.5
            bg-[linear-gradient(180deg,#f0a030,#e08020_15%,#d07010_50%,#d07010_85%,#e08020)]
            dark:bg-[linear-gradient(180deg,#3b7dd8,#2a5db0_15%,#1a4a94_50%,#1a4a94_85%,#2a5db0)]"
          >
            <span className="w-3.5 h-3.5 rounded-full flex-shrink-0 border border-black/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.3)]"
              style={{ background: "linear-gradient(180deg, #f0a030, #e08020)" }}
            />
            <SparkleIcon />
            <span className="text-xs font-semibold text-white tracking-wide [text-shadow:0_1px_2px_rgba(0,0,0,0.5)]">
              RAG Wiki QA
            </span>
            <div className="flex-1" />
            <button
              onClick={() => setDark((d) => !d)}
              className="w-3.5 h-3.5 rounded-full border border-black/30 cursor-pointer flex-shrink-0 shadow-[inset_0_1px_0_rgba(255,255,255,0.3)]"
              style={{
                background: dark
                  ? "linear-gradient(180deg, #5ad2ff, #2d9ee0)"
                  : "linear-gradient(180deg, #f0a030, #e08020)",
              }}
              title="Toggle theme"
            />
          </div>
          <div className="p-3">
            <h2 className="text-sm font-semibold text-[#333] dark:text-white [text-shadow:0_1px_3px_rgba(0,0,0,0.5)]">
              Ask a Question
            </h2>
            <p className="text-[11px] text-[#888] dark:text-[#a0c8e8] mb-1.5">
              Get answers from your PDF textbooks
            </p>
            <div className="flex gap-2 items-start">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                placeholder="e.g. What is a hash table?"
                disabled={loading}
                className="flex-1 min-h-[24px] px-1.5 py-0.5 rounded text-xs text-[#1a1a1a]
                  bg-white/90 border border-black/30 shadow-[inset_0_1px_3px_rgba(0,0,0,0.1)]
                  focus:border-[#1565a8] focus:shadow-[inset_0_1px_3px_rgba(0,0,0,0.1),0_0_0_2px_rgba(21,101,168,0.3)] focus:outline-none
                  disabled:opacity-50"
              />
              <button
                onClick={handleAsk}
                disabled={loading || !question.trim()}
                className="inline-flex items-center gap-1 min-h-[24px] px-4 py-0.5 rounded text-xs font-semibold cursor-pointer
                  disabled:opacity-50 disabled:cursor-default
                  bg-[linear-gradient(180deg,#f0a030,#e08020_50%,#d07010)]
                  border border-[#b06010] text-white [text-shadow:0_1px_0_rgba(0,0,0,0.3)]
                  shadow-[inset_0_1px_0_rgba(255,255,255,0.3),0_1px_3px_rgba(0,0,0,0.3)]
                  hover:bg-[linear-gradient(180deg,#f5b040,#e89030_50%,#d88020)] hover:border-[#a05808]
                  active:bg-[linear-gradient(180deg,#d07010,#c06008_50%,#a05000)]
                  dark:bg-[linear-gradient(180deg,#4ec2f7,#2d9ee0_50%,#1c80c4)]
                  dark:border-[#1565a8]
                  dark:hover:bg-[linear-gradient(180deg,#5ad2ff,#3aa8e8_50%,#2890cc)] dark:hover:border-[#0d5a9e]
                  dark:active:bg-[linear-gradient(180deg,#1c80c4,#1565a8_50%,#0d4a82)]"
              >
                {loading ? (
                  <span className="inline-flex items-center gap-1">
                    <LoadingDots /> Thinking
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5">
                    <SendIcon /> Ask
                  </span>
                )}
              </button>
            </div>

          </div>
        </div>

        {/* Upload card */}
        <div className="mb-2 overflow-hidden rounded-lg
          bg-white/60 backdrop-blur-2xl saturate-150 border border-white/80
          shadow-[0_4px_24px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.9)]
          dark:bg-white/8 dark:border-white/15
          dark:shadow-[0_8px_32px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.2)]"
        >
          <div className="flex items-center gap-2 px-3 py-1.5
            bg-[linear-gradient(180deg,#6fcf97,#27ae60_15%,#1e8449_50%,#1e8449_85%,#27ae60)]
            dark:bg-[linear-gradient(180deg,#3b7dd8,#2a5db0_15%,#1a4a94_50%,#1a4a94_85%,#2a5db0)]"
          >
            <span className="w-3.5 h-3.5 rounded-full flex-shrink-0 border border-black/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.3)]"
              style={{ background: "linear-gradient(180deg, #6fcf97, #27ae60)" }}
            />
            <UploadIcon />
            <span className="text-xs font-semibold text-white tracking-wide [text-shadow:0_1px_2px_rgba(0,0,0,0.5)]">
              Upload PDF
            </span>
          </div>
          <div className="p-3">
            <p className="text-[11px] text-[#888] dark:text-[#a0c8e8] mb-1.5">
              Add a PDF to the index so it can be searched and used for answers
            </p>
            <div className="flex gap-2 items-center">
              <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                disabled={uploading}
                className="flex-1 text-xs text-[#1a1a1a] dark:text-[#d0d8e0]
                  file:mr-2 file:py-0.5 file:px-2 file:rounded file:text-xs file:font-semibold
                  file:cursor-pointer file:disabled:opacity-50 file:disabled:cursor-default
                  file:bg-[linear-gradient(180deg,#6fcf97,#27ae60_50%,#1e8449)]
                  file:border file:border-[#1a7a3a] file:text-white file:[text-shadow:0_1px_0_rgba(0,0,0,0.3)]
                  file:shadow-[inset_0_1px_0_rgba(255,255,255,0.3),0_1px_3px_rgba(0,0,0,0.3)]
                  hover:file:bg-[linear-gradient(180deg,#7fdfa7,#37be70_50%,#2e9459)]
                  active:file:bg-[linear-gradient(180deg,#1e8449,#166838_50%,#0e5028)]
                  dark:file:bg-[linear-gradient(180deg,#4ec2f7,#2d9ee0_50%,#1c80c4)]
                  dark:file:border-[#1565a8]
                  dark:hover:file:bg-[linear-gradient(180deg,#5ad2ff,#3aa8e8_50%,#2890cc)]
                  dark:active:file:bg-[linear-gradient(180deg,#1c80c4,#1565a8_50%,#0d4a82)]"
              />
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="inline-flex items-center gap-1 min-h-[24px] px-3 py-0.5 rounded text-xs font-semibold cursor-pointer
                  disabled:opacity-50 disabled:cursor-default
                  bg-[linear-gradient(180deg,#6fcf97,#27ae60_50%,#1e8449)]
                  border border-[#1a7a3a] text-white [text-shadow:0_1px_0_rgba(0,0,0,0.3)]
                  shadow-[inset_0_1px_0_rgba(255,255,255,0.3),0_1px_3px_rgba(0,0,0,0.3)]
                  hover:bg-[linear-gradient(180deg,#7fdfa7,#37be70_50%,#2e9459)] hover:border-[#1a6a30]
                  active:bg-[linear-gradient(180deg,#1e8449,#166838_50%,#0e5028)]
                  dark:bg-[linear-gradient(180deg,#4ec2f7,#2d9ee0_50%,#1c80c4)]
                  dark:border-[#1565a8]
                  dark:hover:bg-[linear-gradient(180deg,#5ad2ff,#3aa8e8_50%,#2890cc)]
                  dark:active:bg-[linear-gradient(180deg,#1c80c4,#1565a8_50%,#0d4a82)]"
              >
                {uploading ? (
                  <span className="inline-flex items-center gap-1">
                    <LoadingDots /> Indexing
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5">
                    <UploadIcon /> Upload
                  </span>
                )}
              </button>
            </div>
            {uploadStatus && (
              <p className="mt-1.5 text-[11px] text-[#555] dark:text-[#b0d0e0] leading-tight">
                {uploadStatus}
              </p>
            )}
            {uploads.length > 0 && (
              <div className="mt-2 border-t border-black/10 dark:border-white/10 pt-2">
                <p className="text-[11px] text-[#888] dark:text-[#a0c8e8] mb-1 font-semibold">
                  Indexed PDFs
                </p>
                {uploads.map((u) => (
                  <div key={u.filename} className="flex items-center gap-1.5 py-0.5">
                    <span className="flex-1 text-[11px] text-[#444] dark:text-[#c0d0e0] truncate">
                      {u.filename}
                    </span>
                    <span className="text-[10px] text-[#888] dark:text-[#8899aa] flex-shrink-0">
                      {u.chunks} chunk(s)
                    </span>
                    <button
                      onClick={async () => {
                        try {
                          await deleteUpload(u.filename);
                          await fetchUploads();
                        } catch { /* ignore */ }
                      }}
                      className="text-[10px] px-1.5 py-0.5 rounded cursor-pointer
                        text-red-600 hover:text-red-800 hover:bg-red-100
                        dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/30"
                      title={`Remove ${u.filename} from index`}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Answer */}
        {answer && (
          <div className="mb-2 overflow-hidden rounded-lg
            bg-white/60 backdrop-blur-2xl saturate-150 border border-white/80
            shadow-[0_4px_24px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.9)]
            dark:bg-white/8 dark:border-white/15
            dark:shadow-[0_8px_32px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.2)]"
          >
            <div className="flex items-center gap-2 px-3 py-1.5
              bg-[linear-gradient(180deg,#f0a030,#e08020_15%,#d07010_50%,#d07010_85%,#e08020)]
              dark:bg-[linear-gradient(180deg,#3b7dd8,#2a5db0_15%,#1a4a94_50%,#1a4a94_85%,#2a5db0)]"
            >
              <span className="w-3.5 h-3.5 rounded-full flex-shrink-0 border border-black/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.3)]"
                style={{ background: "linear-gradient(180deg, #f0a030, #e08020)" }}
              />
              <span className="text-xs font-semibold text-white [text-shadow:0_1px_2px_rgba(0,0,0,0.5)]">
                Answer
              </span>
            </div>
            <div className="p-3">
              <p className="text-sm text-[#444] dark:text-[#d0d8e0] whitespace-pre-wrap leading-relaxed">
                {answer}
              </p>
            </div>
          </div>
        )}

        {/* Sources */}
        {sources.length > 0 && (
          <div className="overflow-hidden rounded-lg
            bg-white/60 backdrop-blur-2xl saturate-150 border border-white/80
            shadow-[0_4px_24px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.9)]
            dark:bg-white/8 dark:border-white/15
            dark:shadow-[0_8px_32px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.2)]"
          >
            <div className="flex items-center gap-2 px-3 py-1.5
              bg-[linear-gradient(180deg,#f0a030,#e08020_15%,#d07010_50%,#d07010_85%,#e08020)]
              dark:bg-[linear-gradient(180deg,#3b7dd8,#2a5db0_15%,#1a4a94_50%,#1a4a94_85%,#2a5db0)]"
            >
              <span className="w-3.5 h-3.5 rounded-full flex-shrink-0 border border-black/30 shadow-[inset_0_1px_0_rgba(255,255,255,0.3)]"
                style={{ background: "linear-gradient(180deg, #6fcf97, #27ae60)" }}
              />
              <span className="text-xs font-semibold text-white [text-shadow:0_1px_2px_rgba(0,0,0,0.5)]">
                Sources
              </span>
            </div>
            <div className="p-3">
              {sources.map((s, i) => (
                <details key={i} className="mb-1 last:mb-0 border border-black/10 rounded dark:border-white/15">
                  <summary className="flex items-center gap-1.5 px-2 py-1 text-xs text-[#333] dark:text-[#e0e0e0] cursor-pointer list-none
                    bg-[linear-gradient(180deg,rgba(255,255,255,0.8),rgba(240,240,240,0.5))]
                    hover:bg-[linear-gradient(180deg,rgba(255,255,255,0.9),rgba(245,245,245,0.6))]
                    dark:bg-[linear-gradient(180deg,rgba(255,255,255,0.12),rgba(255,255,255,0.05))]
                    dark:hover:bg-[linear-gradient(180deg,rgba(255,255,255,0.18),rgba(255,255,255,0.08))]
                    select-none [&::-webkit-details-marker]:hidden"
                  >
                    <span className="text-[#d07010] dark:text-[#6cb4ee] font-medium hover:underline cursor-pointer">
                      {s.source}
                    </span>
                    <span className="inline-block text-[11px] px-1 leading-[18px] rounded
                      bg-[rgba(224,128,32,0.12)] border border-[rgba(224,128,32,0.3)] text-[#b06010]
                      dark:bg-[rgba(45,158,224,0.2)] dark:border-[rgba(45,158,224,0.4)] dark:text-[#8ac4f0]"
                    >
                      score: {s.score.toFixed(3)}
                    </span>
                    <span className="flex-1" />
                    <ChevronIcon />
                  </summary>
                  <p className="text-xs text-[#555] dark:text-[#c0c0c0] leading-relaxed
                    pl-4 ml-2 mb-2 mt-1 pr-2
                    border-l-3 border-[#e08020] dark:border-[#2d9ee0]">
                    {s.excerpt}
                  </p>
                </details>
              ))}
            </div>
          </div>
        )}

        {/* Status bar */}
        <div className="mt-1 px-1.5 py-0.5 flex items-center gap-1.5 border border-black/10 rounded-sm bg-transparent dark:border-white/10 dark:bg-black/30">
          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: "#6fcf97" }} />
          <span className="text-[11px] text-[#888]">
            {sources.length > 0 ? `${sources.length} source(s) retrieved` : "Ready"}
          </span>
        </div>

      </div>
    </div>
  );
}
