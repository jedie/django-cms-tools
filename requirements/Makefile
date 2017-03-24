REQUIREMENTS_SOURCES := $(wildcard *.in)
REQUIREMENTS := $(REQUIREMENTS_SOURCES:.in=.txt)

dev.txt: base.txt

prod.txt: base.txt

%.txt: %.in
	pip-compile --output-file $@ $<

all: $(REQUIREMENTS)

check:
	@which pip-compile > /dev/null

clean: check
	rm -f *.txt

.PHONY: all check clean
