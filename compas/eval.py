import sys

compas_specs = ["felony_inc", "felony_dec", "misd_inc", "misd_dec", "priors_inc", "priors_dec", "other_inc", "other_dec", "is_recid_set", "is_recid_unset", "is_violnt_recid_set", "is_violnt_recid_unset"]

for spec in compas_specs:
    
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
    print()
