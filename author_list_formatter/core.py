"""Authors CSV: name, affiliations (separated by ';'), orcid, email, corresponding (yes), equal (yes)."""
import csv
import html
import re

SUP = str.maketrans("0123456789,*†", "⁰¹²³⁴⁵⁶⁷⁸⁹˒*†")


def read_authors(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        name = (r.get("name") or "").strip()
        if not name:
            continue
        out.append({"name": name,
                    "affiliations": [a.strip() for a in (r.get("affiliations") or r.get("affiliation") or "").split(";") if a.strip()],
                    "orcid": (r.get("orcid") or "").strip().rsplit("/", 1)[-1],
                    "email": (r.get("email") or "").strip(),
                    "corresponding": (r.get("corresponding") or "").strip().lower() in ("yes", "y", "x", "1", "true"),
                    "equal": (r.get("equal") or "").strip().lower() in ("yes", "y", "x", "1", "true")})
    return out


def _norm(aff):
    return re.sub(r"\s+", " ", aff.strip().rstrip(".")).lower()


def number_affiliations(authors):
    """Number affiliations in order of first appearance; identical affiliations (ignoring case/spacing) share a number.
    Returns (affiliation list, {author index: [numbers]})."""
    order, index, marks = [], {}, {}
    for i, a in enumerate(authors):
        nums = []
        for aff in a["affiliations"]:
            k = _norm(aff)
            if k not in index:
                order.append(aff.strip().rstrip("."))
                index[k] = len(order)
            if index[k] not in nums:
                nums.append(index[k])
        marks[i] = nums
    return order, marks


def _symbols(a):
    return ("†" if a["equal"] else "") + ("*" if a["corresponding"] else "")


def _join(names, sep=", ", last=" and "):
    return names[0] if len(names) == 1 else sep.join(names[:-1]) + last + names[-1]


def notes(authors):
    out = []
    if any(a["equal"] for a in authors):
        out.append("† These authors contributed equally.")
    corr = [a for a in authors if a["corresponding"]]
    if corr:
        out.append("* Corresponding author%s: %s" % ("s" if len(corr) > 1 else "",
                   "; ".join("%s (%s)" % (a["name"], a["email"]) if a["email"] else a["name"] for a in corr)))
    return out


def to_text(authors):
    affs, marks = number_affiliations(authors)
    names = [a["name"] + (",".join(map(str, marks[i])) + _symbols(a)).translate(SUP) for i, a in enumerate(authors)]
    lines = [_join(names), ""] + ["%s %s" % (str(n).translate(SUP), aff) for n, aff in enumerate(affs, 1)]
    return "\n".join(lines + [""] + notes(authors)) + "\n"


def _tex(s):
    return re.sub(r"([&%$#_])", r"\\\1", s)


def to_latex(authors, package="authblk"):
    """authblk: \\author[1,2]{Name} ... \\affil[1]{...}; plain: superscripts in \\author{}."""
    affs, marks = number_affiliations(authors)
    lines = []
    if package == "authblk":
        lines.append("% \\usepackage{authblk}")
        for i, a in enumerate(authors):
            extra = ("\\textsuperscript{\\textdagger}" if a["equal"] else "") + ("\\thanks{Corresponding author: %s}" % _tex(a["email"])
                                                                                if a["corresponding"] and a["email"] else "")
            orcid = "\\,\\orcidlink{%s}" % a["orcid"] if a["orcid"] else ""
            lines.append("\\author[%s]{%s%s%s}" % (",".join(map(str, marks[i])), _tex(a["name"]), orcid, extra))
        lines += ["\\affil[%d]{%s}" % (n, _tex(aff)) for n, aff in enumerate(affs, 1)]
    else:
        names = ["%s\\textsuperscript{%s%s}" % (_tex(a["name"]), ",".join(map(str, marks[i])), _symbols(a).replace("†", "\\textdagger"))
                 for i, a in enumerate(authors)]
        lines.append("\\author{%s\\\\[1ex]\n%s}" % (", ".join(names),
                     "\\\\\n".join("\\textsuperscript{%d}%s" % (n, _tex(aff)) for n, aff in enumerate(affs, 1))))
    return "\n".join(lines) + "\n"


def to_markdown(authors):
    affs, marks = number_affiliations(authors)
    names = []
    for i, a in enumerate(authors):
        name = "[%s](https://orcid.org/%s)" % (a["name"], a["orcid"]) if a["orcid"] else a["name"]
        names.append("%s<sup>%s%s</sup>" % (name, ",".join(map(str, marks[i])), _symbols(a)))
    return "\n".join([_join(names), ""] + ["<sup>%d</sup> %s  " % (n, aff) for n, aff in enumerate(affs, 1)] + [""] + notes(authors)) + "\n"


def to_html(authors):
    affs, marks = number_affiliations(authors)
    names = []
    for i, a in enumerate(authors):
        n = html.escape(a["name"])
        if a["orcid"]:
            n = '<a href="https://orcid.org/%s">%s</a>' % (a["orcid"], n)
        names.append("%s<sup>%s%s</sup>" % (n, ",".join(map(str, marks[i])), html.escape(_symbols(a))))
    out = ['<p class="authors">%s</p>' % _join(names), '<ol class="affiliations">']
    out += ["  <li>%s</li>" % html.escape(aff) for aff in affs]
    out.append("</ol>")
    out += ['<p class="note">%s</p>' % html.escape(n) for n in notes(authors)]
    return "\n".join(out) + "\n"
