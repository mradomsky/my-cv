#!/usr/bin/env python3
"""Agent 2 — CV Tailor.

Reads the structured job analysis produced by job_analyzer.py, plus the
current CV section files, and rewrites `section_headline.tex` (the
professional-summary paragraph) so it is better aligned with the target role.

All other section files are left untouched; the tailored headline is the
highest-impact edit for ATS and recruiter relevance.

Usage:
    python cv_tailor.py --analysis  <path/to/job_analysis.json>
                        --headline  <path/to/section_headline.tex>
                        --language  <de|en|fr>
                        [--job-title  <override title>]
                        [--company    <override company>]
"""

import argparse
import json
import os
import sys
import textwrap

from openai import OpenAI

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert CV writer who specialises in tailoring professional summaries
    (headline / Profil paragraphs) to specific job postings.

    You will receive:
    1. A JSON object with the job analysis.
    2. The current LaTeX source of the candidate's CV headline section.
    3. Supporting context from the candidate's CV (skills, experience).

    Your task: rewrite the LaTeX headline section so it:
    - Is written in the language specified by the `language` parameter (de/en/fr).
    - Highlights the candidate's existing skills and experience that are most
      relevant to the target role.
    - Naturally incorporates key ATS keywords from the job analysis.
    - Remains honest and grounded in the candidate's real background.
    - Keeps a similar length to the original (2–5 sentences, one \\par block).
    - Preserves the exact LaTeX structure: one \\par{ ... } block with a
      leading comment line.

    Return ONLY the complete raw LaTeX for the section (no prose, no markdown
    fences, no explanations).
""")


def build_user_message(analysis: dict, headline_tex: str,
                       competences_tex: str, language: str,
                       job_title: str, company: str) -> str:
    return textwrap.dedent(f"""\
        Target language: {language}
        Target job title: {job_title or analysis.get('job_title', '')}
        Target company: {company or analysis.get('company_name', '')}

        === Job Analysis (JSON) ===
        {json.dumps(analysis, ensure_ascii=False, indent=2)}

        === Current headline section (section_headline.tex) ===
        {headline_tex}

        === Competences section for context ===
        {competences_tex}
    """)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        print(f"[cv_tailor] WARNING: Cannot read {path}: {exc}", file=sys.stderr)
        return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Tailor CV headline for a specific job.")
    parser.add_argument("--analysis",  required=True, help="Path to job_analysis.json")
    parser.add_argument("--headline",  required=True, help="Path to section_headline.tex (read & overwritten)")
    parser.add_argument("--language",  default="de",  help="Target language: de / en / fr")
    parser.add_argument("--job-title", default="",    help="Override job title")
    parser.add_argument("--company",   default="",    help="Override company name")
    args = parser.parse_args()

    # --- load inputs ---
    with open(args.analysis, encoding="utf-8") as fh:
        analysis = json.load(fh)

    headline_tex    = read_file(args.headline)
    competences_tex = read_file(
        os.path.join(os.path.dirname(args.headline), "section_competences.tex")
    )

    # --- call OpenAI ---
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[cv_tailor] ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    print("[cv_tailor] Generating tailored headline …", file=sys.stderr)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_message(
                    analysis, headline_tex, competences_tex,
                    args.language, args.job_title, args.company,
                ),
            },
        ],
        temperature=0.4,
    )
    tailored_tex = response.choices[0].message.content.strip()

    # --- strip accidental markdown fences if the model added them ---
    if tailored_tex.startswith("```"):
        lines = tailored_tex.splitlines()
        # drop first and last fence lines
        tailored_tex = "\n".join(
            ln for ln in lines
            if not ln.startswith("```")
        ).strip()

    # --- write result ---
    with open(args.headline, "w", encoding="utf-8") as fh:
        fh.write(tailored_tex + "\n")

    print(f"[cv_tailor] Tailored headline written to {args.headline}", file=sys.stderr)


if __name__ == "__main__":
    main()
