import { useState, useCallback, useEffect, useMemo } from "react";
import {
  Container, Box, Typography, TextField, Button, Paper, Chip,
  Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel,
  CircularProgress, CssBaseline, ThemeProvider, createTheme, IconButton,
} from "@mui/material";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LightModeIcon from "@mui/icons-material/LightMode";
import SendIcon from "@mui/icons-material/Send";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import "@fontsource/outfit/300.css";
import "@fontsource/outfit/400.css";
import "@fontsource/outfit/500.css";
import "@fontsource/outfit/600.css";
import "@fontsource/outfit/700.css";
import { askQuestion, askStream } from "./api";
import "./App.css";

function getInitialDark(): boolean {
  const stored = localStorage.getItem("dark-mode");
  if (stored !== null) return stored === "true";
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<{ source: string; score: number; excerpt: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(true);
  const [dark, setDark] = useState(getInitialDark);

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: dark ? "dark" : "light",
          ...(dark
            ? {
                primary: { main: "#a78bfa", light: "#c4b5fd", dark: "#7c3aed" },
                secondary: { main: "#2dd4bf", light: "#5eead4", dark: "#0d9488" },
                background: { default: "#0a0a12", paper: "rgba(18,18,30,0.7)" },
              }
            : {
                primary: { main: "#7c3aed", light: "#a78bfa", dark: "#5b21b6" },
                secondary: { main: "#0d9488", light: "#2dd4bf", dark: "#0f766e" },
                background: { default: "#f0effa", paper: "rgba(255,255,255,0.7)" },
              }),
        },
        typography: {
          fontFamily: '"Outfit", system-ui, sans-serif',
        },
        shape: { borderRadius: 16 },
        components: {
          MuiPaper: {
            styleOverrides: {
              root: {
                backdropFilter: "blur(20px)",
                WebkitBackdropFilter: "blur(20px)",
                border: "1px solid",
                borderColor: dark ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.5)",
              },
            },
          },
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: "none",
                fontWeight: 600,
                padding: "8px 24px",
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                "& .MuiOutlinedInput-root": {
                  backdropFilter: "blur(10px)",
                },
              },
            },
          },
        },
      }),
    [dark],
  );

  useEffect(() => {
    localStorage.setItem("dark-mode", String(dark));
  }, [dark]);

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
          else if (event.type === "error") setAnswer(event.content);
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

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />
      <div className="blob blob-4" />
      <Container maxWidth="md" sx={{ py: 4 }} className="content">
        <Box
          component="header"
          className="flex items-center justify-between mb-8"
        >
          <Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                background: "linear-gradient(135deg, #a78bfa, #2dd4bf)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              RAG Wiki QA
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Ask questions about your PDF textbooks
            </Typography>
          </Box>
          <IconButton
            onClick={() => setDark((d) => !d)}
            aria-label="Toggle dark mode"
            sx={{
              border: 1,
              borderColor: "divider",
              borderRadius: 2,
              backdropFilter: "blur(10px)",
            }}
          >
            {dark ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Box>

        <Paper elevation={0} sx={{ p: 3, mb: 3 }}>
          <Box className="flex items-center gap-2 mb-3">
            <AutoAwesomeIcon color="secondary" fontSize="small" />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Ask a Question
            </Typography>
          </Box>
          <Box className="flex gap-2">
            <TextField
              fullWidth
              size="small"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
              placeholder="e.g. What is a hash table?"
              disabled={loading}
              sx={{
                "& .MuiOutlinedInput-notchedOutline": {
                  borderColor: "divider",
                },
              }}
            />
            <Button
              variant="contained"
              onClick={handleAsk}
              disabled={loading || !question.trim()}
              endIcon={
                loading ? (
                  <CircularProgress size={18} color="inherit" />
                ) : (
                  <SendIcon />
                )
              }
              sx={{
                background: "linear-gradient(135deg, #7c3aed, #2dd4bf)",
                "&:hover": {
                  background: "linear-gradient(135deg, #6d28d9, #0d9488)",
                },
              }}
            >
              {loading ? "Thinking..." : "Ask"}
            </Button>
          </Box>
          <FormControlLabel
            control={
              <Switch
                checked={streaming}
                onChange={() => setStreaming((s) => !s)}
                color="secondary"
              />
            }
            label="Stream response"
            sx={{ mt: 1 }}
          />

          {answer && (
            <Box
              sx={{
                mt: 3,
                pt: 3,
                borderTop: 1,
                borderColor: "divider",
              }}
            >
              <Typography
                variant="subtitle1"
                sx={{ fontWeight: 600, color: "secondary.main" }}
                gutterBottom
              >
                Answer
              </Typography>
              <Typography
                variant="body1"
                sx={{ whiteSpace: "pre-wrap", lineHeight: 1.7 }}
              >
                {answer}
              </Typography>
            </Box>
          )}

          {sources.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography
                variant="subtitle2"
                gutterBottom
                color="text.secondary"
                sx={{ fontWeight: 500 }}
              >
                Sources
              </Typography>
              {sources.map((s, i) => (
                <Accordion
                  key={i}
                  disableGutters
                  elevation={0}
                  sx={{
                    bgcolor: "transparent",
                    border: 1,
                    borderColor: "divider",
                    borderRadius: "12px !important",
                    "&:not(:last-child)": { mb: 0.5 },
                    "&:before": { display: "none" },
                  }}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box className="flex items-center gap-2 flex-wrap">
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {s.source}
                      </Typography>
                      <Chip
                        label={`score: ${s.score.toFixed(3)}`}
                        size="small"
                        variant="outlined"
                        color="secondary"
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        pl: 1.5,
                        borderLeft: 2,
                        borderColor: "secondary.main",
                        whiteSpace: "pre-wrap",
                        lineHeight: 1.6,
                      }}
                    >
                      {s.excerpt}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}
