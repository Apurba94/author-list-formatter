import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from author_list_formatter.cli import main
from author_list_formatter.core import number_affiliations, read_authors, to_html, to_latex, to_markdown, to_text

CSV = """name,affiliations,orcid,email,corresponding,equal
Ana Silva,"Dept. of Biology, University X; Institute Y",0000-0002-1825-0097,ana@x.edu,yes,yes
Bo Chen,institute y.,,,,yes
Carla Diaz,Lab Z & Co,,,,
"""


def authors():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "a.csv")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(CSV)
    return read_authors(p), p


class FormatTests(unittest.TestCase):
    def setUp(self):
        self.a, self.path = authors()

    def test_affiliation_numbering_dedups(self):
        affs, marks = number_affiliations(self.a)
        self.assertEqual(affs, ["Dept. of Biology, University X", "Institute Y", "Lab Z & Co"])
        self.assertEqual(marks, {0: [1, 2], 1: [2], 2: [3]})

    def test_text(self):
        t = to_text(self.a)
        self.assertTrue(t.startswith("Ana Silva¹˒²†*, Bo Chen²† and Carla Diaz³"))
        self.assertIn("† These authors contributed equally.", t)
        self.assertIn("* Corresponding author: Ana Silva (ana@x.edu)", t)

    def test_latex(self):
        tex = to_latex(self.a)
        self.assertIn("\\author[1,2]{Ana Silva\\,\\orcidlink{0000-0002-1825-0097}\\textsuperscript{\\textdagger}"
                      "\\thanks{Corresponding author: ana@x.edu}}", tex)
        self.assertIn("\\affil[3]{Lab Z \\& Co}", tex)
        self.assertIn("Carla Diaz\\textsuperscript{3}", to_latex(self.a, "plain"))

    def test_markdown_html(self):
        self.assertIn("[Ana Silva](https://orcid.org/0000-0002-1825-0097)<sup>1,2†*</sup>", to_markdown(self.a))
        h = to_html(self.a)
        self.assertIn("<li>Lab Z &amp; Co</li>", h)

    def test_cli(self):
        with redirect_stdout(io.StringIO()) as buf, redirect_stderr(io.StringIO()) as err:
            main([self.path, "-f", "markdown"])
        self.assertIn("<sup>3</sup> Lab Z & Co", buf.getvalue())
        self.assertEqual(err.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
