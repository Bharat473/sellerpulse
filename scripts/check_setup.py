"""Check that this clone is ready to run: imports, Python version, API key."""

import os
import sys

from dotenv import load_dotenv

REQUIRED = ["anthropic", "chromadb", "sentence_transformers", "gradio", "pandas"]


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
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if key.startswith("sk-ant-") and "your-key-here" not in key:
        print("  ok      ANTHROPIC_API_KEY looks valid")
    elif key:
        print("  MISSING ANTHROPIC_API_KEY is still the placeholder from .env.example")
        missing.append("ANTHROPIC_API_KEY")
    else:
        print("  MISSING ANTHROPIC_API_KEY (copy .env.example to .env)")
        missing.append("ANTHROPIC_API_KEY")

    if missing:
        print(f"\nNot ready: {', '.join(missing)}")
        return 1
    print("\nSetup looks good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
