"""Check that this clone is ready to run: imports, Python version, Groq API key."""

import os
import sys

from dotenv import load_dotenv

REQUIRED = ["langchain", "langchain_groq", "langchain_chroma", "langchain_huggingface",
            "sentence_transformers", "gradio", "pandas"]


def main() -> int:
    print(f"Python {sys.version.split()[0]}")

    missing = []
    for name in REQUIRED:
        try:
            __import__(name)
            print(f"  ok      {name}")
        except ImportError:
            print(f"  MISSING {name}")
            missing.append(name)

    load_dotenv()
    key = os.getenv("GROQ_API_KEY", "")
    if key.startswith("gsk_") and "your-key-here" not in key:
        print("  ok      GROQ_API_KEY looks valid")
    elif key:
        print("  MISSING GROQ_API_KEY is still the placeholder from .env.example")
        missing.append("GROQ_API_KEY")
    else:
        print("  MISSING GROQ_API_KEY (copy .env.example to .env)")
        missing.append("GROQ_API_KEY")

    if missing:
        print(f"\nNot ready: {', '.join(missing)}")
        return 1
    print("\nSetup looks good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
