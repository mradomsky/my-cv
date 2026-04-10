#!/usr/bin/env python3
"""Agent 1 — Job Analyzer.

Fetches a job posting (by URL or raw text), then calls OpenAI to extract
structured requirements that the downstream tailoring agents can consume.

Usage:
    python job_analyzer.py --url <url> [--text <fallback_text>]
                           --output <path/to/job_analysis.json>
"""

import argparse
import json
import os
import sys
import textwrap

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fetch_job_text(url: str) -> str:
    """Download *url* and return visible text, best-effort."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove boilerplate tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        # Collapse whitespace
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        return "\n".join(lines)
    except Exception as exc:  # noqa: BLE001
        print(f"[job_analyzer] WARNING: Could not fetch URL ({exc}). Falling back to --text.", file=sys.stderr)
        return ""


# Maximum characters of job text sent to the model.
# ~12 000 chars ≈ 3 000 tokens, well within GPT-4o's context window while
# keeping API costs low and avoiding irrelevant boilerplate from large pages.
MAX_JOB_TEXT_LENGTH = 12_000

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert job-application consultant.

    Analyse the supplied job description and return ONLY a JSON object (no prose, no
    markdown fences) with exactly these fields:

    {
      "job_title":           "<string>",
      "company_name":        "<string>",
      "language":            "<de|en|fr>",
      "industry":            "<string>",
      "seniority_level":     "<junior|mid|senior|lead|architect>",
      "company_description": "<1-2 sentence summary>",
      "required_skills":     ["<skill>", ...],
      "preferred_skills":    ["<skill>", ...],
      "key_responsibilities":["<responsibility>", ...],
      "keywords":            ["<keyword>", ...]
    }

    Rules:
    - `language` must reflect the *language of the posting* (de/en/fr).
    - `required_skills` / `preferred_skills`: concrete tech or domain skills only, max 12 each.
    - `key_responsibilities`: max 5, each a short imperative phrase.
    - `keywords`: most important 10 tech/domain terms useful for ATS optimisation.
    - If a field cannot be determined, use an empty string or empty list.
""")


def analyze_with_openai(client: OpenAI, job_text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Job description:\n\n{job_text[:MAX_JOB_TEXT_LENGTH]}"},
        ],
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a job posting and emit structured JSON.")
    parser.add_argument("--url",    default="", help="URL of the job posting")
    parser.add_argument("--text",   default="", help="Raw job description text (fallback / supplement)")
    parser.add_argument("--output", required=True, help="Path to write the JSON analysis")
    args = parser.parse_args()

    # --- gather job text ---
    job_text = ""
    if args.url:
        job_text = fetch_job_text(args.url)
    if not job_text and args.text:
        job_text = args.text
    if not job_text:
        print("[job_analyzer] ERROR: No job text available. Provide --url or --text.", file=sys.stderr)
        sys.exit(1)

    # --- call OpenAI ---
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[job_analyzer] ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    print("[job_analyzer] Sending job description to OpenAI for analysis …", file=sys.stderr)
    analysis = analyze_with_openai(client, job_text)

    # --- write output ---
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(analysis, fh, ensure_ascii=False, indent=2)

    print(f"[job_analyzer] Analysis written to {args.output}", file=sys.stderr)
    print(f"  job_title  : {analysis.get('job_title', '?')}", file=sys.stderr)
    print(f"  company    : {analysis.get('company_name', '?')}", file=sys.stderr)
    print(f"  language   : {analysis.get('language', '?')}", file=sys.stderr)
    print(f"  seniority  : {analysis.get('seniority_level', '?')}", file=sys.stderr)


if __name__ == "__main__":
    main()
