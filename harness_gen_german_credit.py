import os 

specs = ["credit_amnt_dec", "credit_amnt_inc", "credit_hist_dec", "credit_hist_inc", "empl_since_dec", "empl_since_inc", "installment_rate_dec", "installment_rate_inc", "job_inc", "job_dec"]

for spec in specs:
    print("Generating harness for german_credit/specs/%s.nom" % (spec))
    os.system("python main.py german_credit/specs/%s.nom" % (spec))

