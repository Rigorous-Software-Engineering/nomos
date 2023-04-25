import sys
from antlr4 import *
from lang.NomosLexer import NomosLexer
from lang.NomosParser import NomosParser
from lang.MyNomosVisitor import MyNomosVisitor

def initializeHarness(outfile):
    outfile.write("import sys\n")
    outfile.write("import copy\n")
    outfile.write("import random\n\n")
    # outfile.write("import tensorflow as tf\n")
    # outfile.write("from utils import *\n\n")

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = NomosLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = NomosParser(stream)
    tree = parser.spec()
    
    benchmark = argv[1].split("/")[0]
    spec = argv[1].split("/")[-1].split(".")[0]
    outfile = open("%s/harness_%s.py" % (benchmark, spec), "w")
    initializeHarness(outfile)

    visitor = MyNomosVisitor(outfile)
    _ = visitor.visit(tree)


if __name__ == '__main__':
    main(sys.argv)
