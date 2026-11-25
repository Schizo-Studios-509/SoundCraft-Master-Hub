import os
import platform
import requests
import json
import re

# ---------------------------------------------------------------
# Ollama API endpoint
# ---------------------------------------------------------------
# Replace this with your desktop or server IP running Ollama
OLLAMA_API = "http://192.168.1.100:11434/api/chat"
MODEL = "llama3"

# ---------------------------------------------------------------
# Environment summary
# ---------------------------------------------------------------
def describe_env():
    return {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cwd": os.getcwd(),
    }

# ---------------------------------------------------------------
# Terminal output sanitisation
# ---------------------------------------------------------------
# Remove C0 control characters (including ESC, BEL and CR) except newline
# and tab, as well as DEL and the C1 control range (0x80-0x9F), which
# includes single-byte CSI/OSC introducers. Without ESC or C1 introducers,
# injected ANSI/OSC sequences are rendered as inert text.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def sanitize_terminal_text(value) -> str:
    """Return ``value`` as text with terminal control characters removed."""
    return _CONTROL_CHARS_RE.sub("", str(value))


# ---------------------------------------------------------------
# Talk to Ollama API
# ---------------------------------------------------------------
def chat(prompt: str):
    system_prompt = (
        "You are SoundCraft AI — a metaphysical music assistant. "
        "You understand sound healing, sacred tunings, and harmonic resonance. "
        "Guide the user in composing metaphysical and healing soundscapes."
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
    }

    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=90)
        response.raise_for_status()
        data = response.json()
        if "message" in data:
            return sanitize_terminal_text(data["message"]["content"])
        elif "error" in data:
            return sanitize_terminal_text(f"⚠️ Ollama API error: {data['error']}")
        else:
            return sanitize_terminal_text(json.dumps(data, indent=2))
    except Exception as e:
        return sanitize_terminal_text(f"⚠️ Connection error: {e}")

# ---------------------------------------------------------------
# Interactive CLI loop
# ---------------------------------------------------------------
def main():
    print("🎧 SoundCraft AI (Pyto) initialized.")
    print("Type 'exit' to quit.\n")
    print(f"Environment: {describe_env()}\n")

    while True:
        try:
            user_in = input("SoundCraft AI > ").strip()
            if user_in.lower() in ("exit", "quit"):
                print("Session ended.")
                break
            result = chat(user_in)
            print(sanitize_terminal_text(result))
        except KeyboardInterrupt:
            print("\nSession interrupted.")
            break
        except Exception as e:
            print(sanitize_terminal_text(f"⚠️ Error: {e}"))

if __name__ == "__main__":
    main()