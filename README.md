# My CV [![Build CV](https://github.com/mradomsky/my-cv/actions/workflows/build-cv.yml/badge.svg)](https://github.com/mradomsky/my-cv/actions/workflows/build-cv.yml)

## About

This repository contains the LaTeX source for my personal CV/résumé. It is based on a
third-party CV template and customized for my own use.

The template uses the _XeLaTeX_ engine, _[Source Sans Pro](https://github.com/adobe-fonts/source-sans-pro)_
font from Adobe, and _[Font Awesome](http://fontawesome.io/)_ icons to produce a clean, modern PDF.

> **Tip:** Keep compiled `.pdf` files out of version control. The CI workflow compiles the
> PDF with real contact info (injected via GitHub secrets) and uploads it to a private
> AWS S3 URL. See [Automated Builds](#automated-builds-github-actions) for details.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **TeX Live** (2021 or later) | Full installation recommended (`texlive-full`) |
| **XeLaTeX** | Required for custom font support (included in TeX Live) |
| **FontAwesome** font | Place `FontAwesome.otf` in the `fonts/` directory |
| **Source Sans Pro** font | Place the `.otf` files in the `fonts/` directory |

### Install TeX Live on Ubuntu/Debian

```bash
sudo apt-get update && sudo apt-get install -y texlive-full
```

### Install TeX Live on Windows (via Chocolatey)

```powershell
choco install miktex strawberryperl -y
```

### Install TeX Live on macOS (via Homebrew)

```bash
brew install --cask mactex
```

---

## Building Locally

1. Copy the example personal info file and fill in your real values:

   ```bash
   cp personal_info.example.tex personal_info.tex
   # edit personal_info.tex — it is gitignored and will never be committed
   ```

2. Compile the CV with **XeLaTeX**:

   ```bash
   xelatex cv.tex
   ```

The compiled PDF will be written to `cv.pdf` in the same directory.
If `personal_info.tex` is absent the CV compiles cleanly but phone and email will be blank.

---

## How to Customise

### Header

```latex
% Author name (mandatory)
\name{Firstname}{LASTNAME}

% Optional profile photo
\photo{2.5cm}{img/profile}

% Tag line / current position (mandatory)
\tagline{Software Engineer}

\socialinfo{
  \linkedin{your-linkedin}
  \github{your-github}\\
  \email{your.email@example.com}\\
  \smartphone{+00 000 000 000}
}
\makecvheader
```

### Experience Section

```latex
\begin{experiences}
  \experience
    {Present}   {Job Title}{Company}{Country}
    {2020}      {
                  \begin{itemize}
                    \item Achievement or responsibility 1
                    \item Achievement or responsibility 2
                  \end{itemize}
                }
                {Technology 1, Technology 2, Technology 3}
  \emptySeparator
  % additional entries …
\end{experiences}
```

---

## Automated Builds (GitHub Actions)

Every push to the `main` branch triggers `.github/workflows/build-cv.yml`, which:

1. Checks out the repository.
2. Generates `personal_info.tex` on-the-fly from repository secrets (`CV_PHONE`, `CV_EMAIL`).
3. Compiles `cv.tex` using **XeLaTeX** via the `xu-cheng/latex-action` action.
4. Uploads `cv.pdf` to an **AWS S3** bucket at a secret, unguessable path.

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `CV_PHONE` | Your phone number |
| `CV_EMAIL` | Your email address |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret access key |
| `S3_BUCKET` | S3 bucket name (must have public read access on the CV object path) |
| `S3_REGION` | AWS region (e.g. `us-east-1`) |
| `CV_PATH_SECRET` | A random UUID; makes the object path unguessable |

### Setup

1. Ensure your S3 bucket allows public **read** on the specific key path `<CV_PATH_SECRET>/cv.pdf` (recommend a bucket policy limiting `GetObject` on that prefix).
2. Generate a UUID (e.g. `python3 -c "import uuid; print(uuid.uuid4())"`) for `CV_PATH_SECRET`.
3. Add all five secrets above to the repository (**Settings → Secrets and variables → Actions**).

The resulting CV URL is stable on every deploy:
```
https://<bucket>.s3.<region>.amazonaws.com/<CV_PATH_SECRET>/cv.pdf
```

---

## AI-Powered CV Tailoring (Multi-Agent Pipeline)

The `.github/workflows/tailor-cv.yml` workflow automates tailoring the CV and
generating a matching cover letter for a specific job application using OpenAI.

### How It Works

```
workflow_dispatch
       │
       ▼
┌─────────────────────┐
│  Agent 1            │  agents/job_analyzer.py
│  Job Analyzer       │  Fetches the posting, extracts skills /
│                     │  responsibilities / keywords via GPT-4o
└────────┬────────────┘
         │  job_analysis.json
    ┌────┴──────────────────────────┐
    ▼                               ▼
┌──────────────────┐   ┌───────────────────────────┐
│  Agent 2         │   │  Agent 3                  │
│  CV Tailor       │   │  Cover Letter Generator   │
│                  │   │                           │
│  Rewrites        │   │  Generates a complete     │
│  section_        │   │  XeLaTeX cover letter     │
│  headline.tex    │   │  (cover_letter.tex)       │
└────────┬─────────┘   └──────────┬────────────────┘
         │                        │
         ▼                        ▼
   XeLaTeX compile          XeLaTeX compile
   (tailored cv.tex)        (cover_letter.tex)
         │                        │
         └────────────┬───────────┘
                      ▼
              Upload both PDFs to S3
              (job-specific path)
```

### Trigger (workflow_dispatch)

Navigate to **Actions → Tailor CV for Job Application → Run workflow** and fill
in the following inputs:

| Input | Required | Description |
|---|---|---|
| `job_url` | optional | URL of the job posting to scrape |
| `job_text` | optional | Raw job description (used when URL is unavailable) |
| `job_title` | **yes** | Job title (e.g. `Senior Solution Engineer`) |
| `company_name` | **yes** | Company name (e.g. `Acme Corp`) |
| `language` | optional | Language for generated documents: `de` / `en` / `fr` (default: `de`) |

> At least one of `job_url` or `job_text` must be provided.

### Additional Required Secret

| Secret | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (GPT-4o access required) |

All other secrets are the same as for `build-cv.yml` (see table above).

### Output

Both PDFs are uploaded to S3 under:
```
s3://<bucket>/<CV_PATH_SECRET>/jobs/<company-job-slug>/cv.pdf
s3://<bucket>/<CV_PATH_SECRET>/jobs/<company-job-slug>/cover_letter.pdf
```
A workflow summary with clickable S3 links is written at the end of the run.

### Running the Agents Locally

```bash
# 1. Install dependencies
pip install -r agents/requirements.txt

# 2. Set your API key
export OPENAI_API_KEY=sk-...

# 3. Analyse a job posting
python agents/job_analyzer.py \
  --url "https://example.com/jobs/123" \
  --output /tmp/job_analysis.json

# 4. Tailor the CV headline (overwrites section_headline.tex in-place)
python agents/cv_tailor.py \
  --analysis /tmp/job_analysis.json \
  --headline section_headline.tex \
  --language de

# 5. Generate the cover letter
python agents/cover_letter_generator.py \
  --analysis /tmp/job_analysis.json \
  --language de \
  --job-title "Senior Solution Engineer" \
  --company "Acme Corp" \
  --output cover_letter.tex

# 6. Compile
xelatex cv.tex
xelatex cover_letter.tex
```

---

## License

The LaTeX class file `yaac-another-awesome-cv.cls` is published under the
[LPPL Version 1.3c](https://www.latex-project.org/lppl.txt).

All content files are published under the
[CC BY-SA 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/legalcode).

Template attribution required by the upstream licenses is kept here rather than repeated
throughout the source files. The class file comes from the YAAC / Awesome Source CV template
lineage, including work by Alessandro Plasmati and Christophe Roger.

---

## Interesting Positions:
https://fulfillmenttools.dvinci-hr.com/de/jobs/14/senior-solution-engineer-mwd