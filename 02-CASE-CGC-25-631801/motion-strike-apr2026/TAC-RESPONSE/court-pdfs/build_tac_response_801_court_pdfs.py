#!/usr/bin/env python3
"""
Build court-ready PDFs for 801-MOTION-STRIKE-APR-22/TAC-RESPONSE (01–07) using pandoc + pdflatex.

Run from repository root or from this directory:
  python3 build_tac_response_801_court_pdfs.py
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

COURT_PDFS = Path(__file__).resolve().parent
MD_DIR = COURT_PDFS.parent
OUT_DIR = MD_DIR / "OUT"
REPO_ROOT = COURT_PDFS.parent.parent.parent
SIG_IMG = REPO_ROOT / "Support" / "signature.png"

FILING_DATE = "April 22, 2026"
EXEC_CITY = "San Francisco, California"

PREAMBLE_INPUT = r"\input{TAC-801-SHARED-PREAMBLE.tex}" + "\n"


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def blank_hearing_and_order_placeholders(text: str) -> str:
    pairs = [
        ("`[HEARING DATE]`", "`TBD`"),
        ("`[HEARING TIME]`", "`TBD`"),
        ("`[DEPARTMENT]`", "`TBD`"),
        ("`[JUDGE]`", "`TBD`"),
        ("`[RESERVATION NUMBER]`", "`TBD`"),
        ("Dated: `_______________`", "Dated: `TBD`"),
    ]
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def common_replacements(text: str) -> str:
    text = text.replace("`[DATE]`", FILING_DATE)
    text = text.replace("[DATE]", FILING_DATE)
    text = text.replace("`[CITY, STATE]`", EXEC_CITY)
    text = text.replace("[CITY, STATE]", EXEC_CITY)
    text = text.replace("[ADDRESS]", "7624 Melody, Rohnert Park, CA 94928")
    text = text.replace("[PHONE]", "650.488.7510")
    text = text.replace("[EMAIL]", "soltrinox@gmail.com")
    return text


def strip_trailing_dated_block(text: str) -> str:
    pattern = re.compile(
        r"\n(?:Dated|DATED):\s*[^\n]*\n+\s*\*\*Franciscus Dylan Rosario\*\*[^\n]*(?:\n[^\n]*)?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return pattern.sub("\n", text.rstrip()) + "\n"


def strip_tac_newcommand_block(text: str) -> str:
    lines = text.splitlines()
    i = 0
    while i < len(lines) and lines[i].strip().startswith("\\newcommand"):
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].strip() == "---":
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:])


def latex_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")


def slugify_title(title: str) -> str:
    """ASCII slug for hyperref \\label{toc:...}; avoid '.' which breaks link matching."""
    t = title.strip().lower()
    t = re.sub(r"[^\w\s]+", "", t)
    t = re.sub(r"[\s_]+", "-", t)
    t = re.sub(r"-+", "-", t).strip("-")
    return (t[:56] if len(t) > 56 else t) or "section"


def extract_h2_sections(md: str) -> list[tuple[str, str, str]]:
    """Return (roman/number mark, raw title, label slug) for each ## heading."""
    rows: list[tuple[str, str, str]] = []
    roman_head = re.compile(
        r"^(X|IX|VIII|VII|VI|IV|V|III|II|I)([\.\s])"
    )
    for m in re.finditer(r"^##\s+(.+)$", md, re.MULTILINE):
        title = m.group(1).strip()
        if "TABLE OF CONTENTS" in title.upper():
            continue
        mark = ""
        rm = roman_head.match(title)
        if rm:
            mark = rm.group(1) + "."
        rm2 = re.match(r"^(\d+)\.", title)
        if not mark and rm2:
            mark = rm2.group(1) + "."
        slug = slugify_title(title)
        rows.append((mark, title, slug))
    return rows


def generate_toc_latex(sections: list[tuple[str, str, str]]) -> str:
    """Generate TOC rows with internal links and \\pageref (two-pass pdflatex)."""
    lines: list[str] = [
        r"\begin{center}\textbf{TABLE OF CONTENTS}\end{center}",
        r"\vspace{2mm}",
    ]
    for mark, title, slug in sections:
        title_disp = latex_escape(title.upper())
        mark_disp = mark or ""
        lines.append(
            rf"\CourtTOCRow{{{mark_disp}}}{{\tacctoclink{{{slug}}}{{{title_disp}}}}}{{\pageref{{toc:{slug}}}}}"
        )
    lines.append(r"\vspace{4mm}")
    return "\n".join(lines) + "\n"


MEMO_TOA_TEX = r"""
\begin{center}\textbf{TABLE OF AUTHORITIES}\end{center}
\vspace{2mm}
\subsubsection*{Cases}
\caseentry{kulchar}{Kulchar v. Kulchar}{(1969) 1 Cal.3d 467}
\caseentry{modnick}{In re Marriage of Modnick}{(1983) 33 Cal.3d 897}
\caseentry{sanders}{Estate of Sanders}{(1985) 40 Cal.3d 607}
\caseentry{westphal}{Westphal v. Westphal}{(1942) 20 Cal.2d 393}
\caseentry{kougasian}{Kougasian v. TMSL, Inc.}{(2004) 118 Cal.App.4th 1028}
\caseentry{stevenot}{In re Marriage of Stevenot}{(1984) 154 Cal.App.3d 1051}
\caseentry{olivera}{Olivera v. Grace}{(1942) 19 Cal.2d 570}
\caseentry{flatley}{Flatley v. Mauro}{(2006) 39 Cal.4th 299}
\caseentry{actionapt}{Action Apartment Ass'n v. City of Santa Monica}{(2007) 41 Cal.4th 1232}
\caseentry{howard_sd}{Howard v. County of San Diego}{(2010) 184 Cal.App.4th 1422}
\caseentry{morgan}{Morgan v. Superior Court}{(1959) 172 Cal.App.2d 527}
\subsubsection*{Statutes}
\statuteentry{ccp473}{Code Civ. Proc.,}{\textsection~473}
\statuteentry{civ2338}{Civ. Code,}{\textsection~2338}
\statuteentry{bpc6128}{Bus. \& Prof. Code,}{\textsection~6128}
\vspace{4mm}
"""


def inject_section_labels(latex_body: str, sections: list[tuple[str, str, str]]) -> str:
    """Insert \\phantomsection\\label{toc:slug} before each \\section{...} in document order."""
    pattern = re.compile(r"(\\section\{[^}]+\})")
    parts = pattern.split(latex_body)
    out: list[str] = []
    idx = 0
    for chunk in parts:
        if pattern.fullmatch(chunk):
            if idx < len(sections):
                slug = sections[idx][2]
                out.append(f"\\phantomsection\\label{{toc:{slug}}}\n")
                idx += 1
            out.append(chunk)
        else:
            out.append(chunk)
    return "".join(out)


def preprocess_tac_01(text: str) -> str:
    text = strip_tac_newcommand_block(text)
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    idx = text.find("**TO ALL PARTIES")
    if idx == -1:
        idx = text.find("## GROUNDS FOR MOTION")
    if idx == -1:
        raise ValueError("01: expected TO ALL PARTIES or GROUNDS anchor")
    text = text[idx:].strip() + "\n"
    return strip_trailing_dated_block(text)


def preprocess_tac_02(text: str) -> str:
    text = strip_tac_newcommand_block(text)
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    ix = text.find("## I.")
    if ix == -1:
        raise ValueError("02: expected ## I.")
    text = text[ix:].strip() + "\n"
    return strip_trailing_dated_block(text)


def preprocess_tac_03(text: str) -> str:
    text = strip_tac_newcommand_block(text)
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    ix = text.find("I, FRANCISCUS DYLAN ROSARIO")
    if ix == -1:
        ix = text.find("## 1.")
    if ix == -1:
        raise ValueError("03: expected declaration opening")
    text = text[ix:].strip() + "\n"
    text = re.sub(r"\n\*\*Franciscus Dylan Rosario\*\*\s*$", "\n", text.strip()) + "\n"
    return text


def preprocess_tac_04(text: str) -> str:
    text = strip_tac_newcommand_block(text)
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    ix = text.find("## ")
    if ix == -1:
        text = text.strip() + "\n"
    else:
        text = text[ix:].strip() + "\n"
    return strip_trailing_dated_block(text)


def preprocess_tac_05(text: str) -> str:
    text = strip_tac_newcommand_block(text)
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    return text.strip() + "\n"


def preprocess_tac_06(text: str) -> str:
    text = strip_tac_newcommand_block(text)
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    ix = text.find("## SECTION I")
    if ix == -1:
        ix = text.find("# THIRD AMENDED COMPLAINT")
        if ix != -1:
            lines = text[ix:].splitlines()
            for i, ln in enumerate(lines):
                if ln.startswith("## SECTION"):
                    text = "\n".join(lines[i:]).strip() + "\n"
                    break
    else:
        text = text[ix:].strip() + "\n"
    cut = text.find("\n/s/ Franciscus Dylan Rosario")
    if cut != -1:
        text = text[:cut].rstrip() + "\n"
    return text.strip() + "\n"


def preprocess_tac_07(text: str) -> str:
    text = strip_html_comments(text)
    text = blank_hearing_and_order_placeholders(text)
    text = common_replacements(text)
    return text.strip() + "\n"


def fix_executed_subsection(body: str) -> str:
    return re.sub(
        r"\\subsection\{Executed on ([^}]+)\}(?:\\label\{[^}]*\})?\s*",
        r"\\noindent Executed on \1\\par\\smallskip\n",
        body,
    )


def fix_letter_suffix_paragraphs(body: str) -> str:
    return re.sub(
        r"^(\d{1,2}[A-Z])\.(\s)",
        r"\\noindent\\textbf{\1.}\\quad\2",
        body,
        flags=re.MULTILINE,
    )


def pandoc_to_latex(md: str) -> str:
    """Map ## -> LaTeX \\section (negative shift promotes ATX headings for article class)."""
    proc = subprocess.run(
        [
            "pandoc",
            "--shift-heading-level-by=-1",
            "--wrap=none",
            "-f",
            "markdown",
            "-t",
            "latex",
        ],
        input=md.encode("utf-8"),
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode("utf-8")


def postprocess_latex(body: str) -> str:
    # Pandoc longtable without caption sets LTcaptype{none}; hyperref errors on counter 'none'.
    body = body.replace("\\def\\LTcaptype{none}", "\\def\\LTcaptype{table}")
    # Pandoc emits UTF-8 § (section sign); OT1/pdfLaTeX may fail without explicit command.
    body = body.replace("\ufeff", "")  # BOM safety
    body = body.replace("\u00a7", r"\textsection{}").replace("§", r"\textsection{}")
    # Headings and tables may use Unicode arrows; map to textcomp (preamble loads textcomp).
    body = body.replace("\u2192", r"{\textrightarrow{}}")
    body = body.replace("\u2190", r"{\textleftarrow{}}")
    body = body.replace("\u2014", r"---")
    body = body.replace("\u2013", r"--")
    body = re.sub(r"\\texttt\{TBD\}", r"\\underline{\\hspace{1.15in}}", body)
    body = re.sub(r"\\texttt\{\[NUMBER\]\}", r"\\underline{\\hspace{0.65in}}", body)
    body = re.sub(
        r"\\texttt\{\\_+\\}",
        r"\\underline{\\hspace{2.2in}}",
        body,
    )
    body = body.replace("{[}PROPOSED{]}", "[PROPOSED]")
    body = re.sub(r"carefully review\{\[\\}ed\{\]\}", r"carefully review[ed]", body)
    return body


def hearing_block() -> str:
    return (
        "\\begin{singlespace}\n"
        "\\noindent\\textbf{Date:} \\hrulefill \\\\\n"
        "\\textbf{Time:} \\hrulefill \\\\\n"
        "\\textbf{Dept.:} \\hrulefill \\\\\n"
        "\\textbf{Judge:} \\hrulefill \\\\\n"
        "\\textbf{Reservation No.:} \\hrulefill \\\\\n"
        "\\end{singlespace}\n"
        "\\vspace{6mm}\n"
    )


def write_tac_signature_block_tex() -> None:
    path = COURT_PDFS / "TAC-801-SIGNATURE-BLOCK.tex"
    body = (
        "% Generated by build_tac_response_801_court_pdfs.write_tac_signature_block_tex()\n"
        "\\vspace{0.5\\baselineskip}\n"
        "\\begin{singlespace}\n"
        "\\begin{flushleft}\n"
        f"Dated: {FILING_DATE} \\\\\n"
        "\\vspace{0.25in}\n"
        "\\noindent\\includegraphics[height=0.5in]{../../../Support/signature.png}\\\\[\\baselineskip]\n"
        "FRANCISCUS DYLAN ROSARIO \\\\\n"
        "Plaintiff, In Pro Per \\\\\n"
        "\\vspace{0.15in}\n"
        "7624 Melody \\\\\n"
        "Rohnert Park, CA 94928 \\\\\n"
        "650.488.7510 \\\\\n"
        "E: soltrinox@gmail.com\n"
        "\\end{flushleft}\n"
        "\\end{singlespace}\n"
    )
    path.write_text(body, encoding="utf-8")


def signature_block_input() -> str:
    return "\\input{TAC-801-SIGNATURE-BLOCK.tex}\n"


def tac_verification_sig() -> str:
    return (
        "\\vspace{6mm}\n"
        "\\noindent /s/ Franciscus Dylan Rosario\\\\\n"
        "\\vspace{4mm}\n"
        "\\noindent\\includegraphics[height=0.5in]{../../../Support/signature.png}\n"
    )


LEFT_CAPTION_TAC = (
    "    \\textbf{Franciscus Dylan Rosario,} \\\\ \\textbf{PLAINTIFF}, \\\\\n"
    "    \\hspace{1cm} v. \\\\\n"
    "    \\small\n"
    "    CSAA Insurance Exchange; \\\\\n"
    "    Carbone, Smith \\& Koyama, LLP; \\\\\n"
    "    Michael R. Chambers; \\\\\n"
    "    Phillips, Spallas \\& Angstadt LLP; \\\\\n"
    "    Priya D. Navaratnasingham; \\\\\n"
    "    Alberto Reyna; \\\\\n"
    "    and DOES 1 through 20, inclusive; \\\\\n"
    "    \\normalsize\n"
    "    \\textbf{DEFENDANTS}\n"
    "    \\makebox[3in]{\\hrulefill}\n"
)


def wrap_tac_document(
    *,
    right_column: str,
    body: str,
    linenumbers: bool,
    hearing: bool,
    sig_mode: str,
) -> str:
    """sig_mode: none | full | declaration_tail | tac"""
    parts = [
        PREAMBLE_INPUT,
        "\\begin{document}\n",
        "\\nolinenumbers\n",
        "\\begin{singlespace}\n",
        "Franciscus Dylan Rosario, \\\\\n",
        "7624 Melody \\\\\n",
        "Rohnert Park, CA 94928 \\\\\n",
        "E: soltrinox@gmail.com \\\\\n",
        "Plaintiff, In Pro Per \\\\\n",
        "\\end{singlespace}\n",
        "\\vspace*{9mm}\n",
        "\\begin{tightcenter}\n",
        "\\textbf{SUPERIOR COURT OF THE STATE OF CALIFORNIA} \\\\\n",
        "\\textbf{COUNTY OF SAN FRANCISCO}\n",
        "\\end{tightcenter}\n",
        "\\vspace*{2.25mm}\n",
        "\\nolinenumbers\n",
        "\\begin{minipage}[t]{3in}\n",
        "    \\raggedright\n",
        LEFT_CAPTION_TAC,
        "\\end{minipage}%\n",
        "\\hspace{3mm}\n",
        "\\begin{minipage}[t]{0.5pt}\n",
        "    \\vspace{0pt}\n",
        "    \\rule{0.5pt}{3.1in}\n",
        "\\end{minipage}\n",
        "\\hspace{3mm}\n",
        "\\begin{minipage}[t]{3in}\n",
        "    \\raggedright\n",
        right_column,
        "\\end{minipage}\n",
        "\\vspace*{6mm}\n",
    ]
    if linenumbers:
        parts.append("\\linenumbers\n")
    else:
        parts.append("\\nolinenumbers\n")
    if hearing:
        parts.append(hearing_block())
    parts.append(body)
    if sig_mode == "full":
        parts.append("\n\\nolinenumbers\n")
        parts.append(signature_block_input())
    elif sig_mode == "declaration_tail":
        parts.append("\n\\nolinenumbers\n")
        parts.append(
            "\\vspace{6mm}\n"
            "\\noindent\\includegraphics[height=0.5in]{../../../Support/signature.png}\n"
        )
    elif sig_mode == "tac":
        parts.append("\n\\nolinenumbers\n")
        parts.append(tac_verification_sig())
    parts.append("\n\\end{document}\n")
    return "".join(parts)


def build_one(
    stem: str,
    md_name: str,
    preprocess,
    right_column: str,
    *,
    linenumbers: bool = True,
    hearing: bool = False,
    sig_mode: str = "full",
    extra_body_fix=None,
    toc_from_md: bool = False,
    toa_tex: str | None = None,
) -> None:
    md_path = MD_DIR / md_name
    raw_md = md_path.read_text(encoding="utf-8")
    md_for_sections = preprocess(raw_md)
    sections = extract_h2_sections(md_for_sections) if toc_from_md else []

    text = md_for_sections
    latex_body = postprocess_latex(pandoc_to_latex(text))

    prefix = ""
    if toc_from_md and sections:
        prefix += generate_toc_latex(sections)
        if toa_tex:
            prefix += toa_tex
        latex_body = inject_section_labels(latex_body, sections)

    latex_body = prefix + latex_body

    if extra_body_fix:
        latex_body = extra_body_fix(latex_body)

    full = wrap_tac_document(
        right_column=right_column,
        body=latex_body,
        linenumbers=linenumbers,
        hearing=hearing,
        sig_mode=sig_mode,
    )
    out_tex = COURT_PDFS / f"{stem}.tex"
    out_tex.write_text(full, encoding="utf-8")
    pdf_name = f"{stem}.pdf"
    for pass_num in range(1, 3):
        proc = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-jobname={stem}",
                str(out_tex.name),
            ],
            cwd=COURT_PDFS,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout or "")
            sys.stderr.write(proc.stderr or "")
            raise RuntimeError(f"pdflatex failed for {stem} (pass {pass_num})")
    pdf_path = COURT_PDFS / pdf_name
    if not pdf_path.is_file():
        raise RuntimeError(f"Missing output {pdf_path}")
    dest = OUT_DIR / pdf_name
    shutil.copy2(pdf_path, dest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build TAC-RESPONSE court PDFs for CGC-25-631801.")
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Write signature block and .tex sources only; do not run pdflatex",
    )
    args = parser.parse_args()

    if not SIG_IMG.is_file():
        raise SystemExit(f"Missing signature image: {SIG_IMG}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_tac_signature_block_tex()

    rc_notice = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{NOTICE OF MOTION AND MOTION FOR LEAVE} \\\\\n"
        "    \\textbf{TO FILE THIRD AMENDED COMPLAINT} \\\\\n"
        "    \\vspace{2mm}\n"
        "    \\begin{singlespace}\n"
        "    \\setlength{\\parindent}{0pt}\n"
        "    \\noindent\\makebox[\\linewidth]{\\textbf{Date:}\\hfill\\underline{\\hspace{1.15in}}}\\\\\n"
        "    \\noindent\\makebox[\\linewidth]{\\textbf{Time:}\\hfill\\underline{\\hspace{1.15in}}}\\\\\n"
        "    \\noindent\\makebox[\\linewidth]{\\textbf{Dept.:}\\hfill\\underline{\\hspace{1.15in}}}\\\\\n"
        "    \\noindent\\makebox[\\linewidth]{\\textbf{Judge:}\\hfill\\underline{\\hspace{1.15in}}}\\\\\n"
        "    \\noindent\\makebox[\\linewidth]{\\textbf{Reservation No.:}\\hfill\\underline{\\hspace{1.15in}}}\\\\\n"
        "    \\end{singlespace}\n"
    )
    rc_mpa = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{MEMORANDUM OF POINTS AND AUTHORITIES} \\\\\n"
        "    \\textbf{IN SUPPORT OF LEAVE TO FILE THIRD AMENDED COMPLAINT}\n"
    )
    rc_decl = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{DECLARATION OF FRANCISCUS DYLAN ROSARIO} \\\\\n"
        "    \\textbf{IN SUPPORT OF MOTION FOR LEAVE TO FILE} \\\\\n"
        "    \\textbf{THIRD AMENDED COMPLAINT}\n"
    )
    rc_rjn = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{REQUEST FOR JUDICIAL NOTICE} \\\\\n"
        "    \\textbf{(ISO LEAVE TO FILE TAC)} \\\\\n"
        "    ~\\\\\n"
        "    \\mbox{(Evid. Code, \\S\\S\\ 452, 453)}\n"
    )
    rc_order = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{[PROPOSED] ORDER GRANTING LEAVE (SAC / TAC)} \\\\\n"
        "    \\textbf{— TIER 1 AND TIER 2 DISPOSITION}\n"
    )
    rc_tac = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{THIRD AMENDED COMPLAINT} \\\\\n"
        "    \\textbf{FOR EXTRINSIC FRAUD AND EQUITABLE RELIEF}\n"
    )
    rc_matrix = (
        "    \\noindent \\textbf{Case No.: CGC-25-631801} \\\\\n"
        "    \\textbf{(Related: CGC-21-594102)} \\\\\n"
        "    ~\\\\\n"
        "    \\textbf{CURE MATRIX — DEFENSE OBJECTION MAP}\n"
    )

    builders = [
        (
            "TAC-801-01-NOTICE",
            "01-NOTICE-OF-MOTION-FOR-LEAVE-TO-FILE-TAC.md",
            preprocess_tac_01,
            rc_notice,
            dict(hearing=False, sig_mode="full"),
        ),
        (
            "TAC-801-02-MEMORANDUM",
            "02-MEMORANDUM-ISO-LEAVE-TAC.md",
            preprocess_tac_02,
            rc_mpa,
            dict(sig_mode="full", toc_from_md=True, toa_tex=MEMO_TOA_TEX),
        ),
        (
            "TAC-801-03-DECLARATION",
            "03-DECLARATION-OF-ROSARIO-ISO-LEAVE.md",
            preprocess_tac_03,
            rc_decl,
            dict(sig_mode="declaration_tail", extra_body_fix=fix_letter_suffix_paragraphs),
        ),
        (
            "TAC-801-04-RFJN",
            "04-REQUEST-FOR-JUDICIAL-NOTICE.md",
            preprocess_tac_04,
            rc_rjn,
            dict(sig_mode="full"),
        ),
        (
            "TAC-801-05-PROPOSED-ORDER",
            "05-PROPOSED-ORDER-GRANTING-LEAVE.md",
            preprocess_tac_05,
            rc_order,
            dict(linenumbers=False, sig_mode="none"),
        ),
        (
            "TAC-801-06-TAC",
            "06-THIRD-AMENDED-COMPLAINT.md",
            preprocess_tac_06,
            rc_tac,
            dict(sig_mode="tac", toc_from_md=True, extra_body_fix=fix_executed_subsection),
        ),
        (
            "TAC-801-07-CURE-MATRIX",
            "07-CURE-MATRIX-DEFENSE-OBJECTION-MAP.md",
            preprocess_tac_07,
            rc_matrix,
            dict(sig_mode="full"),
        ),
    ]

    for stem, md_name, pre, rc, kw in builders:
        if args.skip_pdf:
            md_path = MD_DIR / md_name
            raw = md_path.read_text(encoding="utf-8")
            md_for_sections = pre(raw)
            sections = extract_h2_sections(md_for_sections) if kw.get("toc_from_md") else []
            text = md_for_sections
            latex_body = postprocess_latex(pandoc_to_latex(text))
            prefix = ""
            if kw.get("toc_from_md") and sections:
                prefix += generate_toc_latex(sections)
                if kw.get("toa_tex"):
                    prefix += kw["toa_tex"]
                latex_body = inject_section_labels(latex_body, sections)
            latex_body = prefix + latex_body
            eb = kw.get("extra_body_fix")
            if eb:
                latex_body = eb(latex_body)
            full = wrap_tac_document(
                right_column=rc,
                body=latex_body,
                linenumbers=kw.get("linenumbers", True),
                hearing=kw.get("hearing", False),
                sig_mode=kw.get("sig_mode", "full"),
            )
            (COURT_PDFS / f"{stem}.tex").write_text(full, encoding="utf-8")
            continue
        build_one(stem, md_name, pre, rc, **kw)

    if args.skip_pdf:
        print("Wrote .tex files (no pdflatex). Output dir:", COURT_PDFS)
        return

    print("Built:", COURT_PDFS)
    print("Mirrored to:", OUT_DIR)
    for p in sorted(COURT_PDFS.glob("TAC-801-*.pdf")):
        print(" ", p.name)


if __name__ == "__main__":
    main()
