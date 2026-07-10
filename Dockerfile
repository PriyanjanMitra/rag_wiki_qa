FROM debian:latest

RUN apt-get update && apt-get install -y python3 python3-venv curl zstd && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv

WORKDIR /app

COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cd frontend && npm ci && npm run build

EXPOSE 8000 5173

CMD ["/venv/bin/python3", "run.py"]
