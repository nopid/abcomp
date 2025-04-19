SAMPLES=$(wildcard samples/*.qmd)
OUT=$(addprefix out/, $(addsuffix .zip,$(basename $(SAMPLES:samples/%=%))))

all: $(OUT)

out/%.zip: samples/%.qmd
	@echo "################## $@ #######################"
	(mkdir -p out; cd out; ../render ../$^)

clean:
	-rm $(OUT)

