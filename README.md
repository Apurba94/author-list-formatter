# author-list-formatter

**Keep authors, affiliations, ORCIDs and corresponding-author details in one CSV and generate the
author block for LaTeX (authblk), Markdown, HTML or plain text, with affiliations numbered and deduplicated.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Large author lists are a recurring headache: affiliations must be numbered in order of appearance,
identical institutions merged, symbols for equal contribution and corresponding authors added, and the
whole block rebuilt for every format (LaTeX manuscript, Word cover page, conference website, preprint).
One mistyped number silently attributes someone to the wrong institution.

## Features

- CSV columns: `name`, `affiliations` (`;`-separated), `orcid`, `email`, `corresponding`, `equal`
- Affiliations numbered by first appearance; duplicates merged ignoring case, spacing and trailing dots
- Equal contribution (dagger) and corresponding author (*) markers with footnotes
- Outputs: plain text with Unicode superscripts, LaTeX `authblk` (with `\orcidlink`), LaTeX without packages,
  Markdown with ORCID links, HTML
- Warnings for missing affiliations or no corresponding author

## Usage

```bash
pip install .
author-list-formatter authors.csv -f latex -o authors.tex
author-list-formatter authors.csv -f text
author-list-formatter authors.csv -f html -o authors.html
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
