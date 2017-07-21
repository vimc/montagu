SOURCES = $(wildcard *.dot)
TARGETS = $(patsubst %.dot,%.png,${SOURCES})

all: ${TARGETS}

%.png: %.dot
	dot $< -Tpng -o $@

clean: rm -f ${TARGETS}

.PHONY: all clean
