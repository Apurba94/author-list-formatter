"""Format author lists with numbered affiliations for LaTeX, Markdown/HTML and plain text."""
from .core import read_authors, number_affiliations, to_text, to_latex, to_markdown, to_html

__version__ = "0.1.0"
__all__ = ["read_authors", "number_affiliations", "to_text", "to_latex", "to_markdown", "to_html"]
