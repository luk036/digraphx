# Build pipeline for "Novel Multi-Corner Delay Padding ...".
# Run from paper/  (`make paper` builds delay_padding.pdf).
#
# Flag rationale (see also the md-to-latex skill); recorded here so the
# knowledge is not tribal:
#   - Title/author/abstract live in metadata.yaml, so the body headings start
#     at `#` and map directly to \section.  We therefore do NOT pass
#     --shift-heading-level-by=-1 (there is no title H1 in the body).
#   - --citeproc --csl=ieee.csl : IEEE numeric in-text citations and a numeric
#     reference list.  ieee.csl is vendored here and is self-contained (no
#     <link rel="independent-parent">), so the build needs no network access.
#   - -N : number sections/subsections.
#   - --pdf-engine=pdflatex : every equation and caption is ASCII, so pdflatex
#     is sufficient; no xelatex / Unicode font fallback is required.
#   - -V geometry:margin=1in : comfortable single-column page.
#
# Figures are native TikZ pulled in with \input{figures/*.tikz}.  We do not
# convert SVGs (a fontless rsvg-convert silently drops every <text>), and the
# four structural configurations ship as .tikz sources next to this Makefile.
#
# We deliberately do NOT use pandoc-crossref/cleveref: plain LaTeX
# \label/\ref/\eqref handles every cross-reference and is robust across
# document classes.

PANDOC ?= pandoc
CSL    ?= ieee.csl
BIB    ?= refs.bib
MD      = delay_padding.md
OUT     = delay_padding.pdf

PDFFLAGS = -s -t latex -N --pdf-engine=pdflatex \
           --pdf-engine-opt=-interaction=nonstopmode \
           --citeproc --csl=$(CSL) \
           -V geometry:margin=1in

.PHONY: paper pdf html tex clean

paper: pdf

pdf: $(OUT)

$(OUT): $(MD) metadata.yaml latex.yaml $(BIB) $(CSL) $(wildcard figures/*.tikz)
	$(PANDOC) $(PDFFLAGS) metadata.yaml latex.yaml $(MD) -o $(OUT)

html: $(MD) metadata.yaml latex.yaml $(BIB) $(CSL)
	$(PANDOC) -s -t html5 --citeproc --csl=$(CSL) --mathjax --embed-resources \
	  metadata.yaml latex.yaml $(MD) -o delay_padding.html

tex: $(MD) metadata.yaml latex.yaml $(BIB) $(CSL)
	$(PANDOC) -s -t latex -N --citeproc --csl=$(CSL) \
	  metadata.yaml latex.yaml $(MD) -o delay_padding.tex

clean:
	rm -f $(OUT) delay_padding.tex delay_padding.html
