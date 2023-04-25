import sys
sys.path.append('..')
from lang.NomosParser import NomosParser
from lang.NomosVisitor import NomosVisitor

class MyNomosVisitor(NomosVisitor):
    def __init__(self, outfile):
        self.outfile       = outfile
        self.inpVars       = set()
        self.commonVars    = set()
        self.outVars       = set()
        self.assignedVars  = set()
        self.condition     = ""
        self.mathOperation = ""
        self.dataset       = ""
        self.currentAssgn  = ""

    def visitSpec(self, ctx: NomosParser.SpecContext):
        return super().visitSpec(ctx)

    def visitImport_(self, ctx: NomosParser.Import_Context):
        self.dataset = ctx.dataset.text
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
        self.outfile.write("%s.budget = budget\n" % self.dataset)
        self.outfile.write("pbar = tqdm(desc='test loop', total=budget)\n")
        self.outfile.write("while budget > 0:\n")
        self.outfile.write("\ttry:\n")
        return super().visitImport_(ctx)

    def visitInput_(self, ctx: NomosParser.Input_Context):
        var = self.visit(ctx.inp)        
        if var in self.inpVars:
            message = "WARNING: Multiple input variable instantiation!"
            self.warning(message)
        self.inpVars.add(var)

        if self.dataset == "lunar" or self.dataset == "bipedal":
            self.outfile.write("\t\t%s = %s.randState()\n" % (var, self.dataset))
        else:
            self.outfile.write("\t\t%s = %s.randInput() \n" % (var, self.dataset))
            # self.outfile.write("\tr = random.randint(0, len(inputs)-1)\n")
            # self.outfile.write("\t%s, l%s = inputs[r], labels[r]\n" % (var, var[1:] ))

    def visitPrecondition(self, ctx: NomosParser.PreconditionContext):
        super().visitPrecondition(ctx)
        if self.condition:
            self.outfile.write("\n\t\tif not(%s) :\n" % self.condition)
            self.outfile.write("\t\t\t%s.precond_violtn += 1\n" % self.dataset)
            self.outfile.write("\t\t\tcontinue\n")
            # self.outfile.write("\t\tprint(\"Precondition violation!\")\n")

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

        self.outfile.write("\n\n\t\tif %s :\n" % self.condition)
        # self.outfile.write("\t\tprint(\"No property violation\")\n")
        self.outfile.write("\t\t\t%s.passed += 1\n" % self.dataset)
        self.outfile.write("\t\telse:\n")
        # self.outfile.write("\t\tprint(\"Property violation found!\")\n")
        self.outfile.write("\t\t\t%s.postcond_violtn += 1\n" % self.dataset)
        inpvars = "("
        for iv in list(self.inpVars):
            inpvars += iv + ", "
        inpvars = inpvars[:-2]
        inpvars += ")" 
        # self.outfile.write("\t\t\t%s.bugs.append(%s)\n" % (self.dataset, inpvars))  not used at the moment
        self.outfile.write("\t\t\t%s.process_bug()\n" % self.dataset)
        self.outfile.write("\t\t%s.cur_rand = ()\n" % self.dataset)
        self.outfile.write("\t\tbudget -= 1\n")
        self.outfile.write("\t\tpbar.update(1)\n")
        self.outfile.write("\texcept:\n")
        # self.outfile.write("\t\tprint('Exception occured! Remaining test budget: %d' % budget)\n" )
        self.outfile.write("\t\t%s.exceptions += 1\n" % self.dataset)
        self.outfile.write("\t\t%s.cur_rand = ()\n" % self.dataset)

        # summary    
        self.outfile.write("\nprint('Test budget: ' + str(%s.budget))\n" % self.dataset)
        self.outfile.write("print('Assertion violation: ' + str(%s.precond_violtn))\n" % self.dataset)
        self.outfile.write("print('Succeeding tests: ' + str(%s.passed))\n" % self.dataset)
        self.outfile.write("print('Bug inputs: ' + str(len(%s.bug_inps)))\n" % self.dataset)
        self.outfile.write("print('Number of exceptions: ' + str(%s.exceptions))\n" % self.dataset)
        # self.outfile.write("num_dupl = %s.deduplicate()\n" % self.dataset)
        self.outfile.write("print('Number of duplicate bugs:' + str(%s.num_dupl_bugs))" % self.dataset)
        # %d violations found out of %d tests. %d tests') % (%s)")

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

            func, params = self.visit(ctx.right_rec)
            self.outfile.write("\t\t%s = %s.%s(%s)\n" % (lVar, self.dataset, func, params))

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
            self.outfile.write("\t\t%s = %s\n" % (lVar, num))

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
            self.outfile.write("\t\t%s = copy.copy(%s)\n" % (lVar, rVar))

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
            self.outfile.write("\t\t%s = %s[%s]\n" % (lVar, rVar, rFtr))
        
        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right_math, NomosParser.MathBinaryContext): 
            lVar = self.visit(ctx.left)
            if lVar in self.assignedVars:
                message = "WARNING: Single assignment assumption violation! Please check input."
                self.warning(message)
            if isinstance(ctx.left.children[0], NomosParser.CommonvarContext):
                self.commonVars.add(lVar)

            self.visit(ctx.right_math)
            self.outfile.write("\t\t%s = %s\n" %(lVar, self.mathOperation))
            self.mathOperation = ""
        # THIS PART CHANGED TO SETFEAT
        # elif self.isInstance(ctx.left, NomosParser.RecFtrContext) and (self.isInstance(ctx.right, NomosParser.RecNumContext) or self.isInstance(ctx.right, NomosParser.RecEmptyStrContext)): 
        #     assignedFtr = self.visit(ctx.left)
        #     if assignedFtr == "pos":
        #         assignedFtr = 0
        #     elif assignedFtr == "neg":
        #         assignedFtr = 1
        #     val = ctx.right.getText()
        #     self.outfile.write("\t\t%s[%s] = %s\n" %(self.currentAssgn, assignedFtr, val))

        # elif self.isInstance(ctx.left, NomosParser.RecFtrContext) and self.isInstance(ctx.right, NomosParser.RecFuncContext): 
        #     assignedFtr = self.visit(ctx.left)
        #     if assignedFtr == "pos":
        #         assignedFtr = 0
        #     elif assignedFtr == "neg":
        #         assignedFtr = 1
        #     func, params = self.visit(ctx.right)
        #     self.outfile.write("\t\t%s[%s] = %s.%s(%s)\n" %(self.currentAssgn, assignedFtr, self.dataset, func, params))
        
        # elif self.isInstance(ctx.left, NomosParser.RecFtrContext) and self.isInstance(ctx.right, NomosParser.RecVarFtrContext): 
        #     assignedFtr = self.visit(ctx.left)
        #     if assignedFtr == "pos":
        #         assignedFtr = 0
        #     elif assignedFtr == "neg":
        #         assignedFtr = 1
        #     assigningVar, assigningFtr = self.visit(ctx.right)
        #     self.outfile.write("\t\t%s[%s] = %s[%s]\n" %(self.currentAssgn, assignedFtr, assigningVar, assigningFtr))

        # elif self.isInstance(ctx.left, NomosParser.RecFtrContext) and self.isInstance(ctx.right, NomosParser.RecMathContext): 
        #     assignedFtr = self.visit(ctx.left)
        #     self.visit(ctx.right)
        #     self.outfile.write("\t\t%s[%s] = %s\n" %(self.currentAssgn, assignedFtr, self.mathOperation))

    def visitExprNot(self, ctx: NomosParser.ExprNotContext):
        self.condition += 'not '
        return super().visitExprNot(ctx)

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
            self.condition += "not(" + self.visit(ctx.left) + ") or "
        else:
            message = "WARNING! Unknown binary logic operator."
            self.warning(message)

        self.visit(ctx.right)
        
    def visitExprPred(self, ctx: NomosParser.ExprPredContext):
        op = self.visit(ctx.op)
        if self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right, NomosParser.RecVarContext):
            lVar = self.visit(ctx.left)
            rVar = self.visit(ctx.right)
            pred = "%s %s %s" % (lVar, op, rVar)
            self.condition += pred
        elif self.isInstance(ctx.left, NomosParser.RecVarFtrContext) and self.isInstance(ctx.right, NomosParser.RecVarFtrContext):
            lVar, lFtrInd = self.visit(ctx.left)
            rVar, rFtrInd = self.visit(ctx.right)
            pred = "%s[%s] %s %s[%s]" % (lVar, lFtrInd, op, rVar, rFtrInd)
            self.condition += pred
        elif self.isInstance(ctx.left, NomosParser.RecVarFtrContext) and self.isInstance(ctx.right, NomosParser.RecNumContext):
            lVar, ftrInd = self.visit(ctx.left)
            rVar = self.visit(ctx.right)
            pred = "%s[%s] %s %s" % (lVar, ftrInd, op, rVar)
            self.condition += pred
        elif self.isInstance(ctx.left, NomosParser.RecNumContext) and self.isInstance(ctx.right, NomosParser.RecVarFtrContext):
            lVar = self.visit(ctx.left)
            rVar, ftrInd = self.visit(ctx.right)
            pred = "%s %s %s[%s]" % (lVar, ftrInd, op, rVar)
            self.condition += pred
        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right, NomosParser.RecNumContext) or self.isInstance(ctx.left, NomosParser.RecNumContext) and self.isInstance(ctx.right, NomosParser.RecVarContext):  # order might not be preserved but it is fine
            lVar = self.visit(ctx.left)
            rVar = self.visit(ctx.right)
            pred = "%s %s %s" % (lVar, op, rVar)
            self.condition += pred
        elif self.isInstance(ctx.left, NomosParser.RecVarContext) and self.isInstance(ctx.right, NomosParser.RecFuncContext):
            lVar = self.visit(ctx.left)
            func, params = self.visit(ctx.right)
            pred = "%s %s %s.%s(%s)" % (lVar, op, self.dataset, func, params)
        elif self.isInstance(ctx.left, NomosParser.RecFuncContext) and self.isInstance(ctx.right, NomosParser.RecVarContext):
            func, params = self.visit(ctx.left)
            rVar = self.visit(ctx.right)
            pred = "%s.%s(%s) %s %s" % (self.dataset, func, params, op, lVar)
        else:
            message = "WARNING! Did not match any rule:", ctx.getText()
            self.warning(message)

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

    def visitMathRec(self, ctx: NomosParser.MathRecContext):
        if isinstance(ctx.children[0], NomosParser.RecFuncContext):
            func_name, params = super().visitMathRec(ctx)
            self.mathOperation += "%s.%s(%s)" % (self.dataset, func_name, params)
        else:
            self.mathOperation += ctx.getText()
        # return super().visitMathRec(ctx)

    # def visitMathFtr(self, ctx: NomosParser.MathFtrContext):
    #     var = self.visit(ctx.var)
    #     if var not in self.inpVars:
    #         message = "WARNING: Variable %s is not declared!" % var
    #         self.warning(message)
    #     feature = self.visit(ctx.ftr)
    #     if feature == "pos":
    #         feature = 0
    #     elif feature == "neg":
    #         feature = 1
    #     self.mathOperation += "%s[%s]" % (var, feature)

    # def visitMathFunc(self, ctx: NomosParser.MathFuncContext):
    #     print(self.mathOperation)
    #     print(ctx.getText())
    #     self.mathOperation += ctx.getText()

    # def visitMathCommon(self, ctx: NomosParser.MathCommonContext):
    #     self.mathOperation += ctx.getText()

    # def visitMathNum(self, ctx: NomosParser.MathNumContext):
    #     self.mathOperation += str(ctx.NUM())

    def visitProgram(self, ctx: NomosParser.ProgramContext):
        progLines = ctx.prog.text.split('\n')
        self.outfile.write("\t\t")
        program = '\n\t\t'.join(progLines[1:-1])
        program = program.replace("    ", "\t")  # without this tabs-spaces inconsistency occurs
        self.outfile.write(program)

    def visitRecFunc(self, ctx: NomosParser.RecFuncContext):
        func = ctx.func.text

        self.params = []  # will be filled in the next call
        params = self.visit(ctx.params) # this is needed to check if new variable found in right hand side and also for filling params
        
        # params = ctx.params.getText()
        # super().visitRecFunc(ctx)  
        params = ','.join(self.params)
        return func, params

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

        # if the variable is not defined before
        if var is not None and var not in self.inpVars and var not in self.commonVars:
            message = "WARNING: Variable %s is not declared!" % var
            self.warning(message)

        return super().visitFuncParam(ctx)
    
    def visitRecNum(self, ctx: NomosParser.RecNumContext):
        return ctx.NUM().getText()

    def visitRecEmptyStr(self, ctx: NomosParser.RecEmptyStrContext):
        print("here")
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
