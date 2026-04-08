# My CV [![Build CV](https://github.com/mradomsky/my-cv/actions/workflows/build-cv.yml/badge.svg)](https://github.com/mradomsky/my-cv/actions/workflows/build-cv.yml)

## About

This repository contains the LaTeX source for my personal CV/résumé. It is based on the
**[Awesome Source LaTeX CV](https://github.com/darwiin/awesome-neue-latex-cv)** template originally
created by Alessandro Plasmati and refined by Christophe Roger.

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

## License

The LaTeX class file `awesome-source-cv.cls` is published under the
[LPPL Version 1.3c](https://www.latex-project.org/lppl.txt).

All content files are published under the
[CC BY-SA 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/legalcode).

---

## Interesting Positions:
https://fulfillmenttools.dvinci-hr.com/de/jobs/14/senior-solution-engineer-mwd