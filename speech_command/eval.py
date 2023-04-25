import sys

specs = ["wnoise"]

for spec in specs:
    print(spec)
    fname = "results/nn/%s.log" % spec
    logf = open(fname, "r")
    lines = logf.readlines()

    avg_bi = 0
    avg_numb = 0
    for line in lines:
        if "Succeeding" in line:
            passd = int(line.split(" ")[-1])
        elif "Bug inputs" in line:
            bi = int(line.split(" ")[-1])
            avg_bi += bi
        elif "duplicate" in line:
            dupl = int(line.split(":")[-1])
            avg_numb += 5000 - passd - dupl

    print(avg_numb / 10)
    print(avg_bi / 10)
