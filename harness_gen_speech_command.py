import os 

specs = ["wnoise"]

for spec in specs:
    print("Generating harness for speech_command/specs/%s.nom" % (spec))
    os.system("python main.py speech_command/specs/%s.nom" % (spec))

