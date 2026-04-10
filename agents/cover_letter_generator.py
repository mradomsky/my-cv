#!/usr/bin/env python3
"""Agent 3 — Cover Letter Generator.

Reads the structured job analysis produced by job_analyzer.py and the
candidate's CV sections, then generates a complete, standalone LaTeX cover
letter file (cover_letter.tex) that XeLaTeX can compile directly.

Usage:
    python cover_letter_generator.py
        --analysis  <path/to/job_analysis.json>
        --language  <de|en|fr>
        --job-title <job title>
        --company   <company name>
        --output    <path/to/cover_letter.tex>
"""

import argparse
import json
import os
import sys
import textwrap

from openai import OpenAI

# ---------------------------------------------------------------------------
# LaTeX preamble & footer (static parts of the cover letter document)
# ---------------------------------------------------------------------------

LATEX_PREAMBLE = r"""\documentclass[12pt,a4paper]{article}
\usepackage[a4paper, top=2.5cm, bottom=2.5cm, left=3cm, right=3cm]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{parskip}
\usepackage{microtype}

% Use the same font family as the CV
\setmainfont[
  Path=./fonts/,
  BoldFont=SourceSansPro-Bold.otf,
  ItalicFont=SourceSansPro-It.otf,
  BoldItalicFont=SourceSansPro-BoldIt.otf,
  Ligatures=TeX
]{SourceSansPro-Regular.otf}

\definecolor{darkgray}{HTML}{333333}
\color{darkgray}
\hypersetup{colorlinks=true, urlcolor=darkgray, linkcolor=darkgray}
\pagestyle{empty}

% Load personal contact info from gitignored file (same pattern as cv.tex).
\IfFileExists{personal_info.tex}{\input{personal_info.tex}}{\def\myphone{}\def\myemail{}}

\begin{document}
"""

LATEX_FOOTER = r"""
\end{document}
"""

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert cover-letter writer who creates professional, personalised
    application letters for software engineers and architects.

    You will receive:
    1. A JSON object with the job analysis.
    2. Context from the candidate's CV (skills, experience, education).

    Your task: write the BODY of a cover letter (the part that goes inside the
    LaTeX document environment, after \\pagestyle{empty}).

    The body must contain:
    1. A header block (sender on the left, date on the right, then recipient).
    2. A subject line (bold).
    3. A salutation.
    4. 3–4 body paragraphs (opening, experience match, motivation/fit, closing).
    5. A complimentary close and signature placeholder.

    LaTeX constraints:
    - Use only standard LaTeX2e commands (no extra packages beyond those in the
      preamble: geometry, fontspec, xcolor, hyperref, parskip, microtype).
    - For the sender phone use \\myphone and for email use \\myemail (already
      defined in the preamble via personal_info.tex).
    - The candidate name and location are provided by the caller in the user message.
    - Keep paragraphs separated by blank lines (parskip handles spacing).
    - Use \\textbf{} for emphasis where appropriate.
    - Do NOT wrap the output in \\begin{document} / \\end{document}.
    - Do NOT add markdown fences or any non-LaTeX text.
    - Language: write everything in the language specified by the caller.
""")


def build_user_message(analysis: dict, cv_context: str,
                       language: str, job_title: str, company: str,
                       candidate_name: str, candidate_location: str) -> str:
    return textwrap.dedent(f"""\
        Target language: {language}
        Target job title: {job_title or analysis.get('job_title', '')}
        Target company: {company or analysis.get('company_name', '')}
        Candidate name: {candidate_name}
        Candidate location: {candidate_location}

        === Job Analysis (JSON) ===
        {json.dumps(analysis, ensure_ascii=False, indent=2)}

        === CV context (headline + experience summary) ===
        {cv_context}
    """)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        print(f"[cover_letter_generator] WARNING: Cannot read {path}: {exc}", file=sys.stderr)
        return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a tailored cover letter in LaTeX.")
    parser.add_argument("--analysis",  required=True, help="Path to job_analysis.json")
    parser.add_argument("--language",  default="de",  help="Target language: de / en / fr")
    parser.add_argument("--job-title", default="",    help="Override job title")
    parser.add_argument("--company",   default="",    help="Override company name")
    parser.add_argument("--name",      default="Maksym Radomsky",
                        help="Candidate full name (default: Maksym Radomsky)")
    parser.add_argument("--location",  default="Köln, Deutschland",
                        help="Candidate location shown in the letter header (default: Köln, Deutschland)")
    parser.add_argument("--output",    required=True, help="Path to write cover_letter.tex")
    args = parser.parse_args()

    # --- load job analysis ---
    with open(args.analysis, encoding="utf-8") as fh:
        analysis = json.load(fh)

    # --- build CV context from existing section files ---
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cv_context = "\n\n".join(filter(None, [
        read_file(os.path.join(repo_root, "section_headline.tex")),
        read_file(os.path.join(repo_root, "section_competences.tex")),
        read_file(os.path.join(repo_root, "section_experience_short.tex")),
        read_file(os.path.join(repo_root, "section_scolarite.tex")),
    ]))

    # --- call OpenAI ---
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[cover_letter_generator] ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    print("[cover_letter_generator] Generating cover letter …", file=sys.stderr)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_message(
                    analysis, cv_context,
                    args.language,
                    args.job_title,
                    args.company,
                    args.name,
                    args.location,
                ),
            },
        ],
        temperature=0.5,
    )
    body_tex = response.choices[0].message.content.strip()

    # --- strip accidental markdown fences ---
    if body_tex.startswith("```"):
        lines = body_tex.splitlines()
        body_tex = "\n".join(
            ln for ln in lines
            if not ln.startswith("```")
        ).strip()

    # --- assemble full document ---
    cover_letter_tex = LATEX_PREAMBLE + body_tex + LATEX_FOOTER

    # --- write output ---
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(cover_letter_tex)

    print(f"[cover_letter_generator] Cover letter written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
