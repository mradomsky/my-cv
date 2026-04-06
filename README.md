# My CV [![Build CV](https://github.com/mradomsky/my-cv/actions/workflows/build-cv.yml/badge.svg)](https://github.com/mradomsky/my-cv/actions/workflows/build-cv.yml)

## About

This repository contains the LaTeX source for my personal CV/résumé. It is based on the
**[Awesome Source LaTeX CV](https://github.com/darwiin/awesome-neue-latex-cv)** template originally
created by Alessandro Plasmati and refined by Christophe Roger.

The template uses the _XeLaTeX_ engine, _[Source Sans Pro](https://github.com/adobe-fonts/source-sans-pro)_
font from Adobe, and _[Font Awesome](http://fontawesome.io/)_ icons to produce a clean, modern PDF.

---

## Recommended Directory Structure

```
my-cv/
├── .github/
│   └── workflows/
│       └── build-cv.yml        # CI workflow — compiles PDF on every push
├── fonts/                      # Custom font files (.otf / .ttf)
│   ├── FontAwesome.otf
│   └── SourceSansPro-*.otf
├── img/                        # Photos or logo images used in the CV
│   └── profile.jpg
├── awesome-source-cv.cls       # LaTeX class file (layout & styling)
├── cv.tex                      # Main CV source file
├── .gitignore
└── README.md
```

> **Tip:** Keep compiled `.pdf` files out of version control — the CI workflow uploads the
> PDF as a downloadable workflow artifact after every successful build.

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

### Install TeX Live on macOS (via Homebrew)

```bash
brew install --cask mactex
```

---

## Building Locally

Compile the CV with **XeLaTeX** (recommended — supports custom fonts):

```bash
xelatex cv.tex
```

For a full build including bibliography:

```bash
xelatex cv.tex
bibtex cv
xelatex cv.tex
xelatex cv.tex
```

Or use **latexmk** for automatic dependency tracking:

```bash
latexmk -xelatex cv.tex
```

The compiled PDF will be written to `cv.pdf` in the same directory.

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
2. Compiles `cv.tex` using **XeLaTeX** via the `xu-cheng/latex-action` action.
3. Uploads the resulting `cv.pdf` as a downloadable workflow artifact.

Download the latest compiled PDF from the **Actions** tab → most recent workflow run →
**Artifacts** section.

---

## License

The LaTeX class file `awesome-source-cv.cls` is published under the
[LPPL Version 1.3c](https://www.latex-project.org/lppl.txt).

All content files are published under the
[CC BY-SA 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/legalcode).
