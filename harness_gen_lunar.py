import os 

specs = ["relax", "unrelax"]

for spec in specs:
    print("Generating harness for lunar/specs/%s.nom" % (spec))
    os.system("python main.py lunar/specs/%s.nom" % (spec))

