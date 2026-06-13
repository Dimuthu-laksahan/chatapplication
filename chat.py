# ...existing code...
import requests
import json
import sys

HOST = "http://localhost:11434"   # Ollama server
MODEL = "smollm2:135m"
TIMEOUT = 30

def extract_text(j):
    if isinstance(j, str):
        return j
    if not isinstance(j, dict):
        return str(j)
    if "choices" in j:
        parts = []
        for c in j.get("choices", []):
            if isinstance(c, dict):
                msg = c.get("message") or c.get("delta")
                if isinstance(msg, dict) and "content" in msg:
                    parts.append(msg["content"])
                elif "text" in c:
                    parts.append(c["text"])
        return "\n".join(parts).strip()
    for k in ("text", "response", "answer", "output"):
        if k in j:
            v = j[k]
            if isinstance(v, list):
                return "\n".join(map(str, v))
            return str(v)
    return json.dumps(j)

def send_chat(messages):
    url = f"{HOST}/api/chat"
    payload = {"model": MODEL, "messages": messages}
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        if r.status_code == 404:
            # fallback to /api/generate for older Ollama
            url2 = f"{HOST}/api/generate"
            payload2 = {"model": MODEL, "prompt": "\n".join(m["content"] for m in messages if m["role"]!="system")}
            r = requests.post(url2, headers=headers, json=payload2, timeout=TIMEOUT)
        r.raise_for_status()
        return extract_text(r.json())
    except Exception as e:
        return f"[error] {e}"

def main():
    print(f"Chat with {MODEL} at {HOST} — type Ctrl+C or 'exit' to quit.")
    conversation = [{"role":"system","content":"You are a helpful assistant."}]
    try:
        while True:
            user = input("You: ").strip()
            if not user:
                continue
            if user.lower() in ("exit", "quit"):
                break
            conversation.append({"role":"user","content":user})
            reply = send_chat(conversation)
            print("\nAssistant:", reply, "\n")
            conversation.append({"role":"assistant","content":reply})
    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)

if __name__ == "__main__":
    main()
# ...existing code...