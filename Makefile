PAPER = paper
PDFLATEX := $(shell command -v pdflatex 2>/dev/null)
TECTONIC := $(shell command -v tectonic 2>/dev/null)
BIBTEX := $(shell command -v bibtex 2>/dev/null)

.PHONY: pdf clean

pdf: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex references.bib
ifeq ($(PDFLATEX),)
	@if [ -n "$(TECTONIC)" ]; then \
		$(TECTONIC) $(PAPER).tex; \
	else \
		echo "Neither pdflatex nor tectonic is installed."; \
		exit 1; \
	fi
else
	$(PDFLATEX) $(PAPER)
	$(BIBTEX) $(PAPER)
	$(PDFLATEX) $(PAPER)
	$(PDFLATEX) $(PAPER)
endif

clean:
	rm -f $(PAPER).{aux,bbl,blg,log,out,pdf,toc,fls,fdb_latexmk,xdv}
