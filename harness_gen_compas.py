import os 

specs = ["felony_dec", "felony_inc", "is_recid_set", "is_recid_unset", "is_violnt_recid_set", "is_violnt_recid_unset", "misd_dec", "misd_inc", "other_dec", "other_inc", "priors_dec", "priors_inc"]

for spec in specs:
    print("Generating harness for compas/specs/%s.nom" % (spec))
    os.system("python main.py compas/specs/%s.nom" % (spec))

