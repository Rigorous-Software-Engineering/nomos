# Generated from Nomos.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .NomosParser import NomosParser
else:
    from NomosParser import NomosParser

# This class defines a complete generic visitor for a parse tree produced by NomosParser.

class NomosVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by NomosParser#spec.
    def visitSpec(self, ctx:NomosParser.SpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#import_.
    def visitImport_(self, ctx:NomosParser.Import_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#input_.
    def visitInput_(self, ctx:NomosParser.Input_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#output.
    def visitOutput(self, ctx:NomosParser.OutputContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#vars_.
    def visitVars_(self, ctx:NomosParser.Vars_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#program.
    def visitProgram(self, ctx:NomosParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#assignment.
    def visitAssignment(self, ctx:NomosParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#precondition.
    def visitPrecondition(self, ctx:NomosParser.PreconditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#postcondition.
    def visitPostcondition(self, ctx:NomosParser.PostconditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#exprRec.
    def visitExprRec(self, ctx:NomosParser.ExprRecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#exprNot.
    def visitExprNot(self, ctx:NomosParser.ExprNotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#exprBinary.
    def visitExprBinary(self, ctx:NomosParser.ExprBinaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#exprPred.
    def visitExprPred(self, ctx:NomosParser.ExprPredContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#exprPrn.
    def visitExprPrn(self, ctx:NomosParser.ExprPrnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recNum.
    def visitRecNum(self, ctx:NomosParser.RecNumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recStr.
    def visitRecStr(self, ctx:NomosParser.RecStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recNull.
    def visitRecNull(self, ctx:NomosParser.RecNullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recEmptyStr.
    def visitRecEmptyStr(self, ctx:NomosParser.RecEmptyStrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recVar.
    def visitRecVar(self, ctx:NomosParser.RecVarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recFtr.
    def visitRecFtr(self, ctx:NomosParser.RecFtrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recFunc.
    def visitRecFunc(self, ctx:NomosParser.RecFuncContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recVarFtr.
    def visitRecVarFtr(self, ctx:NomosParser.RecVarFtrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#recFtrAss.
    def visitRecFtrAss(self, ctx:NomosParser.RecFtrAssContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#mathPrn.
    def visitMathPrn(self, ctx:NomosParser.MathPrnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#mathBinary.
    def visitMathBinary(self, ctx:NomosParser.MathBinaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#mathRec.
    def visitMathRec(self, ctx:NomosParser.MathRecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#funcParam.
    def visitFuncParam(self, ctx:NomosParser.FuncParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#cmpOp.
    def visitCmpOp(self, ctx:NomosParser.CmpOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#commonvar.
    def visitCommonvar(self, ctx:NomosParser.CommonvarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#inpvar.
    def visitInpvar(self, ctx:NomosParser.InpvarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#outvar.
    def visitOutvar(self, ctx:NomosParser.OutvarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#llvlFeature.
    def visitLlvlFeature(self, ctx:NomosParser.LlvlFeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by NomosParser#hlvlFeature.
    def visitHlvlFeature(self, ctx:NomosParser.HlvlFeatureContext):
        return self.visitChildren(ctx)



del NomosParser