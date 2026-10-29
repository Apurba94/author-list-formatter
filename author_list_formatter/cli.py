"""Command-line interface for author-list-formatter."""
import argparse
import sys

from .core import read_authors, to_html, to_latex, to_markdown, to_text


def main(argv=None):
    ap = argparse.ArgumentParser(prog="author-list-formatter", description="Format author lists and affiliations.")
    ap.add_argument("csvfile", help="columns: name, affiliations (';'-separated), orcid, email, corresponding, equal")
    ap.add_argument("-f", "--format", choices=["text", "latex", "latex-plain", "markdown", "html"], default="text")
    ap.add_argument("-o", "--output")
    args = ap.parse_args(argv)
    authors = read_authors(args.csvfile)
    if not authors:
        print("error: no authors found", file=sys.stderr)
        return 1
    missing = [a["name"] for a in authors if not a["affiliations"]]
    if missing:
        print("warning: no affiliation for %s" % ", ".join(missing), file=sys.stderr)
    if not any(a["corresponding"] for a in authors):
        print("warning: no corresponding author marked", file=sys.stderr)
    fn = {"text": to_text, "latex": to_latex, "latex-plain": lambda a: to_latex(a, "plain"), "markdown": to_markdown,
          "html": to_html}[args.format]
    out = fn(authors)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(out)
    else:
        sys.stdout.write(out)
    return 0
