import os 

specs = ["blur"]

for spec in specs:
    print("Generating harness for mnist/specs/%s.nom" % (spec))
    os.system("python main.py mnist/specs/%s.nom" % (spec))

