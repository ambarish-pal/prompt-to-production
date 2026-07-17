"""
UC-X app.py — Answer questions about company policy.

Interactive CLI that answers employee questions about company policy by
reading three plaintext policy documents (HR leave, IT acceptable use,
finance reimbursement) and asking Claude to answer based on them.

Run with:
    python app.py

Type a question and press Enter to get an answer. Type "exit" or "quit"
(or press Ctrl+D / Ctrl+Z) to stop.
"""
import os

from dotenv import load_dotenv
from anthropic import Anthropic

MODEL_NAME = "claude-haiku-4-5-20251001"

# Paths are relative to this file's location.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(APP_DIR)

SYSTEM_PROMPT_PATH = os.path.join(APP_DIR, "system_prompt_naive.md")

POLICY_DOCUMENT_PATHS = [
    os.path.join(REPO_ROOT, "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join(REPO_ROOT, "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join(REPO_ROOT, "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

EXIT_WORDS = {"exit", "quit", "q"}


def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_policy_documents():
    """Read all policy documents once and concatenate them into a single
    context string, each labeled with its source filename."""
    sections = []
    for path in POLICY_DOCUMENT_PATHS:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        sections.append(f"=== {filename} ===\n{content}")
    return "\n\n".join(sections)


def build_user_message(policy_text, question):
    return (
        "Here are the company policy documents:\n\n"
        f"{policy_text}\n\n"
        "Using only the information in these documents, answer the "
        f"following question:\n\n{question}"
    )


def main():
    load_dotenv()

    system_prompt = load_system_prompt()
    policy_text = load_policy_documents()

    client = Anthropic()

    print("Company Policy Q&A. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except EOFError:
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in EXIT_WORDS:
            print("Goodbye.")
            break

        try:
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": build_user_message(policy_text, question),
                    }
                ],
            )
        except Exception as e:
            print(f"\nError calling Claude API: {e}\n")
            continue

        answer_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        print(f"\n{answer_text}\n")


if __name__ == "__main__":
    main()
