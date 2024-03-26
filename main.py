import os 
import sys
from antlr4 import *
from lang.NomosLexer import NomosLexer
from lang.NomosParser import NomosParser
from lang.MyNomosVisitor import MyNomosVisitor

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = NomosLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = NomosParser(stream)
    tree = parser.spec()
    
    benchmark = argv[1].split("/")[0]
    spec = argv[1].split("/")[-1].split(".")[0]
    if benchmark == "transpiler":
        assert len(argv) == 3, "Please, provide beam size in addition to path to spec."
        prop_order = argv[1].split("/")[-3]
        beam_size = argv[-1]
        
        os.makedirs(os.path.dirname("%s/harnesses/bs_%s/%s/harness_%s.py" % (benchmark, beam_size, prop_order, spec)), exist_ok=True)
        outfile = open("%s/harnesses/bs_%s/%s/harness_%s.py" % (benchmark, beam_size, prop_order, spec), "w")
    else:
        assert len(argv) == 2, "Please, provide path to spec only."
        outfile = open("%s/harnesses/harness_%s.py" % (benchmark, spec), "w")

    visitor = MyNomosVisitor(outfile)
    _ = visitor.visit(tree)


if __name__ == '__main__':
    main(sys.argv)
