import os 
import re
from contextlib import contextmanager
from pathlib import Path

class Oracle():
    def __init__(self) -> None:
        pass

    # ============================================
    # ============= UTILITY FUNCS ================
    # ============================================

    @contextmanager
    def cd(self ,path: Path):
        """Sets the cwd within the context

        Args:
            path (Path): The path to the cwd

        Yields:
            None
        """

        origin = Path().absolute()
        try:
            os.chdir(path)
            yield
        finally:
            os.chdir(origin)

    def get_func_call(self, code):
        # this regex is greedy ie returns as big as possible
        ffill_call_cand = re.findall(r'f_filled(\(.*\))', code)[0]
        ffill_call = ""
        opn_prn = 0
        for ffc in ffill_call_cand:
            ffill_call += ffc
            if ffc == "(": 
                opn_prn += 1
            elif ffc == ")": opn_prn -= 1
            if opn_prn == 0: break
        
        ffill_call = "f_filled" + ffill_call
        return ffill_call


    # ============================================
    # ============= COMPILE ORACLE ===============
    # ============================================

    def compileOracleJava(self, func, prob_name):
        prob_fname = prob_name + ".java"
        with open("transpiler/benchmark/java/%s" % prob_fname, "r") as prbf:
            java_code = prbf.read()
            java_code = re.sub(r'import javafx.util.Pair;\n', "\n", java_code, count=0, flags=0)

        # TODO: Support replacing other func names
        func = re.sub(r'f_gold', 'f_filled', func, count=0, flags=0)
        try:
            java_code = re.sub(r'//TOFILL\n', func, java_code, count=0, flags=0)
        except:
            return False  # most probably, some strange character produced by the model
        
        os.makedirs(os.path.dirname("transpiler/java_eval/"), exist_ok=True)
        with open("transpiler/java_eval/%s" % prob_fname, "w") as tout:
            tout.write(java_code)
        with self.cd("transpiler/java_eval"):
            os.system("javac %s > %s_err 2>&1" % (prob_fname, prob_name))
        with open("transpiler/java_eval/%s_err" % prob_name, mode="r", errors='ignore') as errf:
            out = errf.read()
            if not "error" in out: return True
            else: return False
    
    def compileOracleCpp(self, func, prob_name):
        prob_fname = prob_name + ".cpp"
        with open("transpiler/benchmark/cpp/%s" % prob_fname, "r") as prbf:
            cpp_code = prbf.read()

        # TODO: Support replacing other func names
        func = re.sub(r'f_gold', 'f_filled', func, count=0, flags=0)
        # if a new parameter is added (ie new_prm) as transformation, we add a default value to it manually as the wrapping code (that calls the function) is not aware of the new addition.

        new_prm_ref_match = re.search(r'(.*f_filled\s*\([\w\W]*?int\s*\&\s*prm\w{3})\s*\)\s*\{', func)
        new_prm_othr_match = re.search(r'(.*f_filled\s*\([\w\W]*?int\s*\*?\s*prm\w{3})\s*\)\s*\{', func)
        if new_prm_othr_match is not None:
            new_prm_match_str = new_prm_othr_match.group(1)
            func = func.replace(new_prm_match_str, new_prm_match_str+"=0")
        elif new_prm_ref_match is not None:
            new_prm_match_str = new_prm_ref_match.group(1)
            func = func.replace(new_prm_match_str, "int a = 0;\n" + new_prm_match_str+"=a")
        else: pass

        try:
            cpp_code = re.sub(r'//TOFILL\n', func, cpp_code, count=0, flags=0)
        except:
            return False  # most probably, some strange character produced by the model
        
        os.makedirs(os.path.dirname("transpiler/cpp_eval/"), exist_ok=True)
        with open("transpiler/cpp_eval/%s" % prob_fname, "w") as tout:
            tout.write(cpp_code)
        
        with self.cd("transpiler/cpp_eval"):
            os.system("g++ %s -o out.o > %s_err 2>&1" % (prob_fname, prob_name) )

        with open("transpiler/cpp_eval/%s_err" % prob_name, mode="r", errors='ignore') as errf:
            out = errf.read()
            if "error" in out: return False
            else: return True
        

    def compileOraclePy(self, func, prob_name):
        prob_fname = prob_name + ".py"
        with open("transpiler/benchmark/py/%s" % prob_fname, "r") as prbf:
            py_code = prbf.read()
        func = str(func)
        func = re.sub(r'f_gold', 'f_filled', func, count=0, flags=0)
        # if a new parameter is added (ie new_prm) as transformation, we add a default value to it manually as the wrapping code (that calls the function) is not aware of the new addition.
        new_prm_match = re.search(r'(f_filled\s*\(.*?prm\w{3})\s*\)\s*:', func)
        if new_prm_match is not None: 
            new_prm_match_str = new_prm_match.group(1)
            func = func.replace(new_prm_match_str, new_prm_match_str+"=0")

        try:
            py_code = re.sub(r'#TOFILL\n', func, py_code, count=0, flags=0)
        except:
            return False  # most probably, some strange character produced by the model

        os.makedirs(os.path.dirname("transpiler/py_eval/"), exist_ok=True)
        with open("transpiler/py_eval/%s" % prob_fname, "w") as tout:
            tout.write(py_code)

        with self.cd("transpiler/py_eval"):
            os.system("timeout 30 python %s > %s_err 2>&1" % (prob_fname, prob_name))

        with open("transpiler/py_eval/%s_err" % prob_name, mode="r", errors='ignore') as errf:
            out = errf.read()
            if "#Results:" not in out: return False
            else: return True
        

    # ============================================
    # ============= SYNTACTIC ORACLES ============
    # ============================================


    def checkArityGnrc(self, func):
        subs = re.search('\((.*?)\)', func)
        if subs is None: return -1  # postc violation 
        params = subs.group(1)
        params = params.strip()
        if not params: return 0
        else: return params.count(",") + 1
    
    def checkArityCpp(self, func):
        return self.checkArityGnrc(func)

    def checkArityPy(self, func):
        return self.checkArityGnrc(func)

    def checkArityJava(self, func):
        return self.checkArityGnrc(func)

    def numConditionalsJava(self, func):
        all_br = re.findall(r'((\{|\}|\s+)(if|switch)\s*\([\S\s]+?\))', func)
        all_br_elseif = re.findall(r'((\{|\}|\s+)else if\s*\([\S\s]+?\))', func)
        return len(all_br) - len(all_br_elseif)

    def numConditionalsCpp(self, func):
        return self.numConditionalsJava(func)

    def numConditionalsPy(self, func):
        all_br = re.findall(r'(\s+(if|match)\s+[^\n]+?\s*:)|(\s+if\s+[^\n]+?\s+else)', func)
        return len(all_br)

    def numLoopsJava(self, func):
        all_loops = re.findall(r'((\{|\}|\s+)(for|while)\s*\([\S\s]+?\))', func)
        return len(all_loops)

    def numLoopsCpp(self, func):
        return self.numLoopsJava(func)

    def numLoopsPy(self, func):
        all_loops = re.findall(r'(\s+(for|while)\s+[^\n]+?\s*:)', func)
        return len(all_loops)
    
    def imports(self, scode, lib):
        return lib in scode


    # ============================================
    # ============= SEMANTIC ORACLE ==============
    # ============================================

    def runJava(self, func, prob_name):
        
        prob_fname = prob_name + ".java"

        with open("./transpiler/benchmark/java/%s" % prob_fname, "r") as srcf:
            java_code = srcf.read()
            java_code = re.sub(r'import javafx.util.Pair;\n', "\n", java_code, count=0, flags=0)

        ffill_call = self.get_func_call(java_code)

        print_res = "System.out.println(%s);\n" % ffill_call
        java_code = re.sub(r'\{\s+n_success+=1;\s+\}', "{\nn_success+=1;\n}\n%s" % print_res, java_code, count=0, flags=0)

        try:
            java_code = re.sub(r'//TOFILL', func, java_code, count=0, flags=0)
        except:
            return None  # most probably, some strange character produced by the model
            
        os.makedirs(os.path.dirname("transpiler/java_eval/"), exist_ok=True)
        with open("transpiler/java_eval/%s" % prob_fname, "w") as tout:
            tout.write(java_code)

        with self.cd("transpiler/java_eval"):
            os.system("javac %s > %s_err 2>&1" % (prob_fname, prob_name))
            
        with open("transpiler/java_eval/%s_err" % prob_name, mode="r", errors='ignore') as errf:
            out = errf.read()
            if "error" in out: return None

        with self.cd("transpiler/java_eval"):
            exec_fname = prob_fname.split(".")[0]
            os.system("timeout 30 java %s > %s_out 2>&1" % (exec_fname, prob_name))  # 30secs timeout - measurement against infinite loops

        with open("transpiler/java_eval/%s_out" % prob_name, mode="r", errors='ignore') as outf:
            out = outf.read()
            if "error" in out: return None
            else: return out

    def runCpp(self, func, prob_name):

        prob_fname = prob_name + ".cpp"
        with open("transpiler/benchmark/cpp/%s" % prob_fname, "r") as prbf:
            cpp_code = prbf.read()

        ffill_call = self.get_func_call(cpp_code)
        
        print_res = "cout << %s ;\n" % ffill_call
        try:
            cpp_code = re.sub(r'\{\s+n_success\+=1;\s+\}', "{\nn_success+=1;\n}\n%s" % print_res, cpp_code, count=0, flags=0)
        except:
            return None  # most probably, some strange character produced by the model

        func = re.sub(r'f_gold', 'f_filled', func, count=0, flags=0)
        # if a new parameter is added (ie new_prm) as transformation, we add a default value to it manually as the wrapping code (that calls the function) is not aware of the new addition.
        new_prm_match = re.search(r'(.*f_filled\s*\([\w\W]*?int\s*(\&|\*?)\s*prm\w{3})\s*\)\s*\{', func)
        if new_prm_match is not None:
            new_prm_match_str = new_prm_match.group(1)
            func = func.replace(new_prm_match_str, new_prm_match_str+"=0")
        else: pass

        try:
            cpp_code = re.sub(r'//TOFILL\n', func, cpp_code, count=0, flags=0)
        except:
            return None  # most probably, some strange character produced by the model

        os.makedirs(os.path.dirname("transpiler/cpp_eval_run/"), exist_ok=True)
        with open("transpiler/cpp_eval_run/%s" % prob_fname, "w") as tout:
            tout.write(cpp_code)
            
        with self.cd("transpiler/cpp_eval_run"):
            os.system("g++ %s -o out.o > %s_err 2>&1" % (prob_fname, prob_name) )

        with open("transpiler/cpp_eval_run/%s_err" % prob_name, mode="r", errors='ignore') as errf:
            out = errf.read()
            if "error" in out: return None

        with self.cd("transpiler/cpp_eval_run"):
            os.system("timeout 30 ./out.o > %s_out 2>&1" % prob_name )  # 30secs timeout - measurement against infinite loops

        with open("transpiler/cpp_eval_run/%s_out" % prob_name, mode="r", errors='ignore') as outf:
            out = outf.read()
            if "error" in out: return None
            else: return out


    def runPy(self, func, prob_name):
        prob_fname = prob_name + ".py"
        with open("transpiler/benchmark/py/%s" % prob_fname, "r") as prbf:
            py_code = prbf.read()

        ffill_call = "f_filled(*parameters_set)"
        print_res = "print(%s)\n" % ffill_call
        py_code = py_code.replace("\t\tif f_filled(*parameters_set)", "\t\t%s\n\t\tif f_filled(*parameters_set)" % print_res) 
        
        # TODO: Support replacing other func names
        func = re.sub(r'f_gold', 'f_filled', func, count=0, flags=0)

        # if a new parameter is added (ie new_prm) as transformation, we add a default value to it manually as the wrapping code (that calls the function) is not aware of the new addition.
        new_prm_match = re.search(r'(f_filled\s*\(.*?prm\w{3})\s*\)\s*:', func)
        if new_prm_match is not None: 
            new_prm_match_str = new_prm_match.group(1)
            func = func.replace(new_prm_match_str, new_prm_match_str+"=0")

        try:
            py_code = re.sub(r'#TOFILL\n', func, py_code, count=0, flags=0)
        except:
            return None  # most probably, some strange character produced by the model

        os.makedirs(os.path.dirname("transpiler/py_eval_run/"), exist_ok=True)
        with open("transpiler/py_eval_run/%s" % prob_fname, "w") as tout:
            tout.write(py_code)

        with self.cd("transpiler/py_eval_run"):
            os.system("timeout 30 python %s > %s_err 2>&1" % (prob_fname, prob_name))  # 30secs timeout - measurement against infinite loops

        with open("transpiler/py_eval_run/%s_err" % prob_name, mode="r", errors='ignore') as errf:
            out = errf.read()
            if "#Results:" not in out: return None
            else: return out
