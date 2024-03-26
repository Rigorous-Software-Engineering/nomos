import sys
sys.path.append('..')
from lang.NomosParser import NomosParser
from lang.NomosVisitor import NomosVisitor


class MyNomosVisitor(NomosVisitor):
    def __init__(self, outfile, beam_size=1):
        self.beam_size     = int(beam_size)
        self.outfile       = outfile
        self.inpVars       = set()
        self.commonVars    = set()
        self.outVars       = set()
        self.assignedVars  = set()
        self.condition     = ""
        self.mathOperation = ""
        self.dataset       = ""
        self.currentAssgn  = ""
        self.commonVarToOutVar = {}

    def visitSpec(self, ctx: NomosParser.SpecContext):
        return super().visitSpec(ctx)

    def visitImport_(self, ctx: NomosParser.Import_Context):
        self.dataset = ctx.dataset.text

        self.outfile.write("import sys\n")
        self.outfile.write("import copy\n")
        self.outfile.write("import time\n")
        self.outfile.write("import random\n\n")
        
        self.outfile.write("from tqdm.auto import tqdm\n")
        self.outfile.write("from %s.helper import %s\n" % (self.dataset, self.dataset))

        self.outfile.write("%s = %s()\n\n" % (self.dataset, self.dataset))

        self.outfile.write("rseed = int(sys.argv[1])\n")
        self.outfile.write("%s.setSeed(rseed)\n" % self.dataset)
        self.outfile.write("print('Seed set to: ' + str(rseed))\n\n")

        self.outfile.write("model_path = sys.argv[2]\n")
        self.outfile.write("%s.load(model_path)\n" % self.dataset)
        self.outfile.write("print('Test set size: ' + str(len(%s.inputs)))\n\n" % self.dataset)

        self.outfile.write("budget = int(sys.argv[3])\n")
        self.outfile.write("print('Test budget: ' + str(budget))\n\n")

        if self.dataset == "transpiler":
            self.outfile.write("%s.beam_size = %d\n" % (self.dataset, self.beam_size))
            self.outfile.write("print('Beam size set to %d')\n" % self.beam_size)

        self.outfile.write("\npbar = tqdm(desc='test loop', total=budget)\n")
        self.outfile.write("stime = time.time()\n")
        self.outfile.write("while budget > 0:\n")
        return super().visitImport_(ctx)

    def visitInput_(self, ctx: NomosParser.Input_Context):
        var = self.visit(ctx.inp)
        if var in self.inpVars:
            message = "WARNING: Multiple input variable instantiation!"
            self.warning(message)
        self.inpVars.add(var)

        if self.dataset == "lunar" or self.dataset == "bipedal":
            self.outfile.write("\t%s = %s.randState()\n" % (var, self.dataset))
        else:
            self.outfile.write("\t%s = %s.randInput() \n" % (var, self.dataset))

    def visitPrecondition(self, ctx: NomosParser.PreconditionContext):
        super().visitPrecondition(ctx)
        if self.condition:
            self.outfile.write("\n\tif not(%s) :\n" % self.condition)
            self.outfile.write("\t\t%s.precond_violtn += 1\n" % self.dataset)
            self.outfile.write("\t\tcontinue\n")

    def visitOutput(self, ctx: NomosParser.OutputContext):
        var = self.visit(ctx.out)
        if var in self.outVars:
            message = "WARNING: Multiple output variable instantiation!"
            self.warning(message)

        self.outVars.add(var)

    def visitPostcondition(self, ctx: NomosParser.PostconditionContext):
        self.condition = ""
        super().visitPostcondition(ctx)
        if self.condition == "":
            message = "WARNING: Empty postcondition is not allowed!"
            self.warning(message)

        if self.beam_size == 1:
            self.outfile.write("\n\tif %s :\n" % self.condition)
            self.outfile.write("\t\t%s.passed += 1\n" % self.dataset)
            self.outfile.write("\telse:\n")
            self.outfile.write("\t\t%s.postcond_violtn += 1\n" % self.dataset)
            self.outfile.write("\t\t%s.process_bug()\n" % self.dataset)

        elif self.beam_size > 1:
            self.outfile.write("\n\tis_passed=False\n")
            loop_itr = ["i", "j", "k", "l"]
            indentation = "\t"
            for i in range(len(self.outVars)):
                li = loop_itr[i]
                self.outfile.write(indentation*i + "\tfor %s in range(%s):\n" % (li, self.beam_size))
            for idx, ov in enumerate(self.outVars): self.condition = self.condition.replace(ov, ov+"[%s]" % loop_itr[idx])
            for cv in self.commonVars: 
                if cv in self.commonVarToOutVar:
                    idx = list(self.outVars).index(self.commonVarToOutVar[cv])
                    self.condition = self.condition.replace(cv, cv+"[%s]" % loop_itr[idx])
            self.outfile.write(indentation*i + "\t\tif %s :\n" % self.condition)
            self.outfile.write(indentation*i + "\t\t\t%s.passed += 1\n" % self.dataset)
            self.outfile.write(indentation*i + "\t\t\tis_passed = True\n")
            self.outfile.write(indentation*i + "\t\t\tbreak\n")  # crucial
            self.outfile.write("\tif not is_passed:\n")
            self.outfile.write("\t\t%s.postcond_violtn += 1\n" % self.dataset)
            self.outfile.write("\t\t%s.process_bug()\n" % self.dataset)

        self.outfile.write("\tbudget -= 1\n")
        self.outfile.write("\tpbar.update(1)\n")
        
        self.outfile.write("\n%s.wrap_up()\n" % self.dataset)
        self.outfile.write("etime = time.time()\n")

        # summary
        self.outfile.write("\nprint('Precondition violation: ' + str(%s.precond_violtn))\n" % self.dataset)
        self.outfile.write("print('Postcondition violation: ' + str(%s.postcond_violtn))\n" % self.dataset)
        self.outfile.write("print('Number of duplicate bugs: ' + str(%s.num_dupl_bugs))\n" % self.dataset)
        self.outfile.write("print('Bug inputs: ' + str(len(%s.bug_inps)))\n" % self.dataset)
        self.outfile.write("print('Prediction time: ' + str(%s.pred_time))\n" % (self.dataset))
        self.outfile.write("print('Total time: ', etime-stime)")

    def visitAssignment(self, ctx: NomosParser.AssignmentContext):

        if isinstance(ctx.left.children[0], NomosParser.OutvarContext):
            message = "WARNING: Output variable can not be assigned."
            self.warning(message)

        if self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right_rec, NomosParser.RecFuncContext):
            lVar = self.visit(ctx.left)
            if lVar in self.assignedVars:
                message = "WARNING: Single assignment assumption violation! Please check input."
                self.warning(message)

            if isinstance(ctx.left.children[0], NomosParser.CommonvarContext):
                self.commonVars.add(lVar)
            elif isinstance(ctx.left.children[0], NomosParser.InpvarContext):
                self.inpVars.add(lVar)
            else:
                message = "WARNING: There is a problem in variable assignment."
                self.warning(message)
            self.assignedVars.add(lVar)

            funcCall = self.visit(ctx.right_rec)
            self.outfile.write("\t%s = %s\n" % (lVar,funcCall))
            params = funcCall.split("(")[1]
            for ov in self.outVars: 
                if ov in params: self.commonVarToOutVar[lVar] = ov
                

        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right_rec, NomosParser.RecNumContext):
            lVar = self.visit(ctx.left)
            if lVar in self.assignedVars:
                message = "WARNING: Single assignment assumption violation! Please check input."
                self.warning(message)

            if isinstance(ctx.left.children[0], NomosParser.CommonvarContext):
                self.commonVars.add(lVar)
            elif isinstance(ctx.left.children[0], NomosParser.InpvarContext):
                self.inpVars.add(lVar)
            else:
                message = "WARNING: There is a problem in variable assignment."
                self.warning(message)

            self.assignedVars.add(lVar)
            num = self.visit(ctx.right_rec)
            self.outfile.write("\t%s = %s\n" % (lVar, num))

        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right_rec, NomosParser.RecFtrAssContext):
            lVar = self.visit(ctx.left)
            if lVar in self.assignedVars:
                message = "WARNING: Single assignment assumption violation! Please check input."
                self.warning(message)

            if isinstance(ctx.left.children[0], NomosParser.CommonvarContext):
                self.commonVars.add(lVar)
            elif isinstance(ctx.left.children[0], NomosParser.InpvarContext):
                self.inpVars.add(lVar)
            else:
                message = "WARNING: There is a problem in variable assignment."
                self.warning(message)

            self.assignedVars.add(lVar)
            self.currentAssgn = lVar

            rVar = self.visit(ctx.right_rec.var)
            if rVar not in self.inpVars:
                message = "WARNING: Variable %s is not declared!" % rVar
                self.warning(message)
            self.outfile.write("\t%s = copy.copy(%s)\n" % (lVar, rVar))

            self.visit(ctx.right_rec)  # recursively calls this method and enters below branch

        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right_rec, NomosParser.RecVarFtrContext):
            lVar = self.visit(ctx.left)
            if lVar in self.assignedVars:
                message = "WARNING: Single assignment assumption violation! Please check input."
                self.warning(message)

            if isinstance(ctx.left.children[0], NomosParser.CommonvarContext):
                self.commonVars.add(lVar)
            elif isinstance(ctx.left.children[0], NomosParser.InpvarContext):
                self.inpVars.add(lVar)
            else:
                message = "WARNING: There is a problem in variable assignment."
                self.warning(message)

            self.assignedVars.add(lVar)

            rVar, rFtr = self.visit(ctx.right_rec)
            self.outfile.write("\t%s = %s[%s]\n" % (lVar, rVar, rFtr))

        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right_math, NomosParser.MathBinaryContext):
            lVar = self.visit(ctx.left)
            if lVar in self.assignedVars:
                message = "WARNING: Single assignment assumption violation! Please check input."
                self.warning(message)
            if isinstance(ctx.left.children[0], NomosParser.CommonvarContext):
                self.commonVars.add(lVar)

            self.mathOperation = ""  # clear before use
            rmath = self.visit(ctx.right_math)
            self.outfile.write("\t%s = %s\n" %(lVar, rmath))

    def visitExprNot(self, ctx: NomosParser.ExprNotContext):
        self.condition += 'not '
        return super().visitExprNot(ctx)

    def visitExprRec(self, ctx: NomosParser.ExprRecContext):
        if self.isInstance(ctx.children[0], NomosParser.RecFuncContext):
            # this is a fucntion call that returns a bool value for either pre- or post-condition
            funcCall = self.visit(ctx.children[0])
            self.condition += funcCall
        elif self.isInstance(ctx.children[0], NomosParser.RecVarContext):
            var = self.visit(ctx.children[0])
            self.condition += var

    def visitExprPrn(self, ctx: NomosParser.ExprPrnContext):
        self.condition += '( '
        super().visitExprPrn(ctx)
        self.condition += ' )'

    def visitExprBinary(self, ctx: NomosParser.ExprBinaryContext):
        if ctx.AND():
            self.visit(ctx.left)
            self.condition += " and "
        elif ctx.OR():
            self.visit(ctx.left)
            self.condition += " or "
        elif ctx.IMPL():
            self.visit(ctx.left)
            self.condition = "not(" + self.condition + ") or "
        else:
            message = "WARNING! Unknown binary logic operator."
            self.warning(message)

        self.visit(ctx.right)

    def visitExprPred(self, ctx: NomosParser.ExprPredContext):
        op = self.visit(ctx.op)
        self.mathOperation = ""  # clear before use
        lVar = self.visit(ctx.left)
        self.mathOperation = ""  # clear before use
        rVar = self.visit(ctx.right)
        pred = "%s %s %s" % (lVar, op, rVar)
        self.condition += pred
        
        return pred


    def visitMathPrn(self, ctx: NomosParser.MathPrnContext):
        self.mathOperation += '( '
        super().visitMathPrn(ctx)
        self.mathOperation += ' )'

    def visitMathBinary(self, ctx: NomosParser.MathBinaryContext):
        self.visit(ctx.left)

        if ctx.PLUS():
            self.mathOperation += " + "
        elif ctx.MULT():
            self.mathOperation +=  " * "
        elif ctx.MINUS():
            self.mathOperation +=  " - "
        elif ctx.DIV():
            self.mathOperation +=  " / "
        else:
            message = "WARNING! Unknown binary math operator."
            self.warning(message)

        self.visit(ctx.right)

        return self.mathOperation

    def visitMathRec(self, ctx: NomosParser.MathRecContext):
        ret = super().visitMathRec(ctx)
        self.mathOperation += ret
        return self.mathOperation
    

    def visitProgram(self, ctx: NomosParser.ProgramContext):
        progLines = ctx.prog.text.split('\n')
        self.outfile.write("\t")
        program = '\n\t'.join(progLines[1:-1])
        program = program.replace("    ", "\t")  # without this tabs-spaces inconsistency occurs
        program = program + "\n"
        self.outfile.write(program)

    def visitRecFunc(self, ctx: NomosParser.RecFuncContext):
        func = ctx.func.text
        self.params = []  # will be filled in the next call
        params = self.visit(ctx.params) # this is needed to check if new variable found in right hand side and also for filling params

        params = ','.join(self.params)
        return "%s.%s(%s)" % (self.dataset, func, params)

    def visitFuncParam(self, ctx: NomosParser.FuncParamContext):
        var = None
        if self.isInstance(ctx.param, NomosParser.RecNumContext) or self.isInstance(ctx.param, NomosParser.RecEmptyStrContext) or self.isInstance(ctx.param, NomosParser.RecVarContext):
            prm = self.visit(ctx.param)
            self.params.append(prm)
        elif self.isInstance(ctx.param, NomosParser.RecVarFtrContext):
            var, ftr = self.visit(ctx.param)
            if ftr == "pos": ftr = "0"
            elif ftr == "neg": ftr = "1"
            param = "%s[%s]" % (var, ftr)
            self.params.append(param)
        elif self.isInstance(ctx.param, NomosParser.RecStrContext):
            self.params.append(ctx.param.getText())
            
        # if the variable is not defined before
        if var is not None and var not in self.inpVars and var not in self.commonVars:
            message = "WARNING: Variable %s is not declared!" % var
            self.warning(message)

        return super().visitFuncParam(ctx)

    def visitRecNum(self, ctx: NomosParser.RecNumContext):
        return ctx.NUM().getText()

    def visitRecEmptyStr(self, ctx: NomosParser.RecEmptyStrContext):
        return ctx.EMPTYSTR().getText()

    def visitInpvar(self, ctx: NomosParser.InpvarContext):
        return ctx.getText()

    def visitOutvar(self, ctx: NomosParser.OutvarContext):
        return ctx.getText()

    def visitCommonvar(self, ctx: NomosParser.CommonvarContext):
        return ctx.getText()

    def visitLlvlFeature(self, ctx: NomosParser.LlvlFeatureContext):
        return ctx.NUM()

    def visitHlvlFeature(self, ctx: NomosParser.HlvlFeatureContext):
        return ctx.getText()

    def visitRecVarFtr(self, ctx: NomosParser.RecVarFtrContext):
        var = self.visit(ctx.var)
        feature = self.visit(ctx.ftr)
        return var, feature
    
    def visitRecNull(self, ctx: NomosParser.RecNullContext):
        return "None"

    def visitCmpOp(self, ctx: NomosParser.CmpOpContext):
        return ctx.getText()

    ###################
    ##### HELPERS #####
    ###################

    def isInstance(self, obj, ctx):
        if obj.__class__ == ctx:
            return True
        return False

    def warning(self, message):
        print(message)
        exit()
