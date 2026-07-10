import subprocess, sys, os, signal, threading, time

BASE = os.path.dirname(os.path.abspath(__file__))
procs = []

def print_output(proc, prefix):
    for line in iter(proc.stdout.readline, ""):
        if not line:
            break
        sys.stdout.write(f"[{prefix}] {line}")
        sys.stdout.flush()

def cleanup(*_):
    for p in procs:
        p.terminate()
    for p in procs:
        try: p.wait(timeout=5)
        except: p.kill()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

ollama = subprocess.Popen(
    ["ollama", "serve"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
procs.append(ollama)
time.sleep(3)
subprocess.run(["ollama", "pull", "llama3.2"], capture_output=True)

backend = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "route.api:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
)
procs.append(backend)

frontend = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=os.path.join(BASE, "frontend"),
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
)
procs.append(frontend)

threading.Thread(target=print_output, args=(backend, "BACKEND"), daemon=True).start()
threading.Thread(target=print_output, args=(frontend, "FRONTEND"), daemon=True).start()

try:
    while all(p.poll() is None for p in procs):
        time.sleep(1)
except KeyboardInterrupt:
    cleanup()
