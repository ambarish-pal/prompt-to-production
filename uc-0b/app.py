"""
UC-0B app.py — Summarize the policy document.

Usage:
    python app.py --input <path_to_policy_txt> --output <path_to_write_summary_txt>
"""
import argparse
import os

from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL_NAME = "claude-sonnet-5"


def load_system_prompt():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    system_prompt_path = os.path.join(script_dir, "system_prompt_naive.md")
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(description="Summarize a policy document using Claude.")
    parser.add_argument("--input", required=True, help="Path to the input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    system_prompt = load_system_prompt()

    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": policy_text}
        ],
    )

    summary_text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
