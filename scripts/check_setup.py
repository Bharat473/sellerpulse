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
    if os.getenv("ANTHROPIC_API_KEY"):
        print("  ok      ANTHROPIC_API_KEY is set")
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
