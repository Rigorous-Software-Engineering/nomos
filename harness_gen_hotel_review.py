import os 

specs = ["neg-add", "neg-del", "pos-add", "pos-del"]

for spec in specs:
    print("Generating harness for hotel_review/specs/%s.nom" % (spec))
    os.system("python main.py hotel_review/specs/%s.nom" % (spec))

