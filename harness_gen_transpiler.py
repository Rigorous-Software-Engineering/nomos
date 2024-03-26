import os 

oracles = ["compile", "syn_arity", "syn_numLoops", "syn_numConditionals", "sem_retValues"]
# transformations =  ["merge"]  #
transformations =  ["addLoop", "rmLoop", "addConditional", "chBranchCond", "addParam", "renameParam" ]

prp_order = "2safety"
# prp_order = "3safety"
src_tgt_lang = "java-py"
# src_tgt_lang = "java-cpp"
beam_size = 1
# beam_size = 3

for orc in oracles:
    if prp_order == "1safety":
        print("Generating harness for bs_%d/%s/%s/%s_%s.nom" % (beam_size, prp_order, src_tgt_lang, orc, src_tgt_lang))
        os.system("python main.py transpiler/specs/%s/%s/%s_%s.nom %d" % (prp_order, src_tgt_lang, orc, src_tgt_lang, beam_size))
    else:
        for trns in transformations:
            if os.path.exists("transpiler/specs/%s/%s/%s_%s_%s.nom" % (prp_order, src_tgt_lang, orc, trns, src_tgt_lang)):
                print("Generating harness for bs_%d/%s/%s/%s_%s_%s.nom" % (beam_size, prp_order, src_tgt_lang, orc, trns, src_tgt_lang))
                os.system("python main.py transpiler/specs/%s/%s/%s_%s_%s.nom %d" % (prp_order, src_tgt_lang, orc, trns, src_tgt_lang, beam_size))

