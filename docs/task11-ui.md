# Task 11: Gradio chat UI

![SellerPulse chat UI](screenshots/task11-ui.png)

- Run: `uv run python agent.py` (local) / `uv run python agent.py --share` (public link)
- Query tested: "Why is my Boho Wall Hanging listing underperforming?" → grounded diagnosis citing REV-1024, REV-1028, REV-1002
- Other examples: (one line each: policy / sales / draft reply — pass or what went wrong)
- Share link: `--share` failed on the corporate laptop ("Could not create share link") — tunnel blocked by company network/security. Not bypassed. Next: Biswajit runs `--share` from his machine (also tests Task 4: clone + README); permanent link in Task 34 (deployment).
- Design: gr.ChatInterface; history shown but not sent to the LLM (memory is Week 2); share is opt-in to protect the Groq free quota
