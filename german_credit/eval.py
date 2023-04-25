import sys

german_specs = ["credit_amnt_inc", "credit_amnt_dec", "credit_hist_inc", "credit_hist_dec", "installment_rate_inc", "installment_rate_dec", "empl_since_inc", "empl_since_dec", "job_inc", "job_dec"]

for spec in german_specs:
    
    print(spec)
    fname = "results/nb/%s.log" % spec
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
