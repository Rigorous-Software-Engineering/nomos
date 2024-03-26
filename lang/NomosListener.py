# Generated from Nomos.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .NomosParser import NomosParser
else:
    from NomosParser import NomosParser

# This class defines a complete listener for a parse tree produced by NomosParser.
class NomosListener(ParseTreeListener):

    # Enter a parse tree produced by NomosParser#spec.
    def enterSpec(self, ctx:NomosParser.SpecContext):
        pass

    # Exit a parse tree produced by NomosParser#spec.
    def exitSpec(self, ctx:NomosParser.SpecContext):
        pass


    # Enter a parse tree produced by NomosParser#import_.
    def enterImport_(self, ctx:NomosParser.Import_Context):
        pass

    # Exit a parse tree produced by NomosParser#import_.
    def exitImport_(self, ctx:NomosParser.Import_Context):
        pass


    # Enter a parse tree produced by NomosParser#input_.
    def enterInput_(self, ctx:NomosParser.Input_Context):
        pass

    # Exit a parse tree produced by NomosParser#input_.
    def exitInput_(self, ctx:NomosParser.Input_Context):
        pass


    # Enter a parse tree produced by NomosParser#output.
    def enterOutput(self, ctx:NomosParser.OutputContext):
        pass

    # Exit a parse tree produced by NomosParser#output.
    def exitOutput(self, ctx:NomosParser.OutputContext):
        pass


    # Enter a parse tree produced by NomosParser#vars_.
    def enterVars_(self, ctx:NomosParser.Vars_Context):
        pass

    # Exit a parse tree produced by NomosParser#vars_.
    def exitVars_(self, ctx:NomosParser.Vars_Context):
        pass


    # Enter a parse tree produced by NomosParser#program.
    def enterProgram(self, ctx:NomosParser.ProgramContext):
        pass

    # Exit a parse tree produced by NomosParser#program.
    def exitProgram(self, ctx:NomosParser.ProgramContext):
        pass


    # Enter a parse tree produced by NomosParser#assignment.
    def enterAssignment(self, ctx:NomosParser.AssignmentContext):
        pass

    # Exit a parse tree produced by NomosParser#assignment.
    def exitAssignment(self, ctx:NomosParser.AssignmentContext):
        pass


    # Enter a parse tree produced by NomosParser#precondition.
    def enterPrecondition(self, ctx:NomosParser.PreconditionContext):
        pass

    # Exit a parse tree produced by NomosParser#precondition.
    def exitPrecondition(self, ctx:NomosParser.PreconditionContext):
        pass


    # Enter a parse tree produced by NomosParser#postcondition.
    def enterPostcondition(self, ctx:NomosParser.PostconditionContext):
        pass

    # Exit a parse tree produced by NomosParser#postcondition.
    def exitPostcondition(self, ctx:NomosParser.PostconditionContext):
        pass


    # Enter a parse tree produced by NomosParser#exprRec.
    def enterExprRec(self, ctx:NomosParser.ExprRecContext):
        pass

    # Exit a parse tree produced by NomosParser#exprRec.
    def exitExprRec(self, ctx:NomosParser.ExprRecContext):
        pass


    # Enter a parse tree produced by NomosParser#exprNot.
    def enterExprNot(self, ctx:NomosParser.ExprNotContext):
        pass

    # Exit a parse tree produced by NomosParser#exprNot.
    def exitExprNot(self, ctx:NomosParser.ExprNotContext):
        pass


    # Enter a parse tree produced by NomosParser#exprBinary.
    def enterExprBinary(self, ctx:NomosParser.ExprBinaryContext):
        pass

    # Exit a parse tree produced by NomosParser#exprBinary.
    def exitExprBinary(self, ctx:NomosParser.ExprBinaryContext):
        pass


    # Enter a parse tree produced by NomosParser#exprPred.
    def enterExprPred(self, ctx:NomosParser.ExprPredContext):
        pass

    # Exit a parse tree produced by NomosParser#exprPred.
    def exitExprPred(self, ctx:NomosParser.ExprPredContext):
        pass


    # Enter a parse tree produced by NomosParser#exprPrn.
    def enterExprPrn(self, ctx:NomosParser.ExprPrnContext):
        pass

    # Exit a parse tree produced by NomosParser#exprPrn.
    def exitExprPrn(self, ctx:NomosParser.ExprPrnContext):
        pass


    # Enter a parse tree produced by NomosParser#recNum.
    def enterRecNum(self, ctx:NomosParser.RecNumContext):
        pass

    # Exit a parse tree produced by NomosParser#recNum.
    def exitRecNum(self, ctx:NomosParser.RecNumContext):
        pass


    # Enter a parse tree produced by NomosParser#recStr.
    def enterRecStr(self, ctx:NomosParser.RecStrContext):
        pass

    # Exit a parse tree produced by NomosParser#recStr.
    def exitRecStr(self, ctx:NomosParser.RecStrContext):
        pass


    # Enter a parse tree produced by NomosParser#recNull.
    def enterRecNull(self, ctx:NomosParser.RecNullContext):
        pass

    # Exit a parse tree produced by NomosParser#recNull.
    def exitRecNull(self, ctx:NomosParser.RecNullContext):
        pass


    # Enter a parse tree produced by NomosParser#recEmptyStr.
    def enterRecEmptyStr(self, ctx:NomosParser.RecEmptyStrContext):
        pass

    # Exit a parse tree produced by NomosParser#recEmptyStr.
    def exitRecEmptyStr(self, ctx:NomosParser.RecEmptyStrContext):
        pass


    # Enter a parse tree produced by NomosParser#recVar.
    def enterRecVar(self, ctx:NomosParser.RecVarContext):
        pass

    # Exit a parse tree produced by NomosParser#recVar.
    def exitRecVar(self, ctx:NomosParser.RecVarContext):
        pass


    # Enter a parse tree produced by NomosParser#recFtr.
    def enterRecFtr(self, ctx:NomosParser.RecFtrContext):
        pass

    # Exit a parse tree produced by NomosParser#recFtr.
    def exitRecFtr(self, ctx:NomosParser.RecFtrContext):
        pass


    # Enter a parse tree produced by NomosParser#recFunc.
    def enterRecFunc(self, ctx:NomosParser.RecFuncContext):
        pass

    # Exit a parse tree produced by NomosParser#recFunc.
    def exitRecFunc(self, ctx:NomosParser.RecFuncContext):
        pass


    # Enter a parse tree produced by NomosParser#recVarFtr.
    def enterRecVarFtr(self, ctx:NomosParser.RecVarFtrContext):
        pass

    # Exit a parse tree produced by NomosParser#recVarFtr.
    def exitRecVarFtr(self, ctx:NomosParser.RecVarFtrContext):
        pass


    # Enter a parse tree produced by NomosParser#recFtrAss.
    def enterRecFtrAss(self, ctx:NomosParser.RecFtrAssContext):
        pass

    # Exit a parse tree produced by NomosParser#recFtrAss.
    def exitRecFtrAss(self, ctx:NomosParser.RecFtrAssContext):
        pass


    # Enter a parse tree produced by NomosParser#mathPrn.
    def enterMathPrn(self, ctx:NomosParser.MathPrnContext):
        pass

    # Exit a parse tree produced by NomosParser#mathPrn.
    def exitMathPrn(self, ctx:NomosParser.MathPrnContext):
        pass


    # Enter a parse tree produced by NomosParser#mathBinary.
    def enterMathBinary(self, ctx:NomosParser.MathBinaryContext):
        pass

    # Exit a parse tree produced by NomosParser#mathBinary.
    def exitMathBinary(self, ctx:NomosParser.MathBinaryContext):
        pass


    # Enter a parse tree produced by NomosParser#mathRec.
    def enterMathRec(self, ctx:NomosParser.MathRecContext):
        pass

    # Exit a parse tree produced by NomosParser#mathRec.
    def exitMathRec(self, ctx:NomosParser.MathRecContext):
        pass


    # Enter a parse tree produced by NomosParser#funcParam.
    def enterFuncParam(self, ctx:NomosParser.FuncParamContext):
        pass

    # Exit a parse tree produced by NomosParser#funcParam.
    def exitFuncParam(self, ctx:NomosParser.FuncParamContext):
        pass


    # Enter a parse tree produced by NomosParser#cmpOp.
    def enterCmpOp(self, ctx:NomosParser.CmpOpContext):
        pass

    # Exit a parse tree produced by NomosParser#cmpOp.
    def exitCmpOp(self, ctx:NomosParser.CmpOpContext):
        pass


    # Enter a parse tree produced by NomosParser#commonvar.
    def enterCommonvar(self, ctx:NomosParser.CommonvarContext):
        pass

    # Exit a parse tree produced by NomosParser#commonvar.
    def exitCommonvar(self, ctx:NomosParser.CommonvarContext):
        pass


    # Enter a parse tree produced by NomosParser#inpvar.
    def enterInpvar(self, ctx:NomosParser.InpvarContext):
        pass

    # Exit a parse tree produced by NomosParser#inpvar.
    def exitInpvar(self, ctx:NomosParser.InpvarContext):
        pass


    # Enter a parse tree produced by NomosParser#outvar.
    def enterOutvar(self, ctx:NomosParser.OutvarContext):
        pass

    # Exit a parse tree produced by NomosParser#outvar.
    def exitOutvar(self, ctx:NomosParser.OutvarContext):
        pass


    # Enter a parse tree produced by NomosParser#llvlFeature.
    def enterLlvlFeature(self, ctx:NomosParser.LlvlFeatureContext):
        pass

    # Exit a parse tree produced by NomosParser#llvlFeature.
    def exitLlvlFeature(self, ctx:NomosParser.LlvlFeatureContext):
        pass


    # Enter a parse tree produced by NomosParser#hlvlFeature.
    def enterHlvlFeature(self, ctx:NomosParser.HlvlFeatureContext):
        pass

    # Exit a parse tree produced by NomosParser#hlvlFeature.
    def exitHlvlFeature(self, ctx:NomosParser.HlvlFeatureContext):
        pass



del NomosParser