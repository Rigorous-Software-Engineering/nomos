import re 
import random
from string import ascii_lowercase

class Transformer():
    def __init__(self) -> None:
        pass

    # setting random seed for transformations
    def setSeed(self, rseed):
        random.seed(rseed)

    def addParamJava(self, func):
        # 6 letter long parameter name
        newprm = ''.join(random.choice(ascii_lowercase) for _ in range(3))
        newprm = "prm" + newprm
        randint = random.randint(-10, 10)
        randint2 = random.randint(1, 5)

        choices = [
            "\n%s -= %d;" % (newprm, randint),
            "\n%s += %d;" % (newprm, randint),
            "\n%s = %d;" % (newprm, randint),
            "\nint localVar = %s * %d;" % (newprm, randint),
            "\nint localVar = %s + %d;" % (newprm, randint2),
        ]

        # add a parameter
        subs = re.search(r'\((.*?)\)', func)
        params = subs.group(1)
        new_params = params + ", int %s" % newprm
        new_func = func.replace(params, new_params)

        # use it
        subs = re.search(r'\)\s*\{([\s\S]*)\}', new_func)
        content = subs.group(1)
        new_content = random.choice(choices) + content
        new_func = new_func.replace(content, new_content)

        return new_func

    def renameParam(self, func):
        subs = re.search(r'\((.*?)\)', func)
        params = subs.group(1)
        params_list = params.split(",")
        renamed_param = random.choice(params_list)

        renamed_param = renamed_param.replace("[", "").replace("]", "")
        renamed_param = renamed_param.strip()
        prm_name = renamed_param.split(" ")[-1]

        # 6 letter new parameter name
        newprm_name = ''.join(random.choice(ascii_lowercase) for _ in range(6))

        new_func = self.param_replace(func, prm_name, newprm_name)
        return new_func
        

    def addIfStmt(self, func):

        tmpvar = ''.join(random.choice(ascii_lowercase) for _ in range(6))
        randint = random.randint(-100, 100)
        randint2 = random.randint(-100, 100)
        randstr = ''.join(random.choice(ascii_lowercase) for _ in range(8))
        
        choices = [
            "\nif (true) { int %s = %d; }\n" % (tmpvar, randint),
            "\nif (false) { int %s = %d; }\n" % (tmpvar, randint),
            "\nif (%d == %d) { System.out.print(\"\"); }\n" % (randint, randint),
            "\nif (%d == %d) { System.out.print(\"%s\"); }\n" % (randint, randint, randstr),
            "\nif (%d == %d) { System.out.print(\"\"); }\n" % (randint, randint2),
            "\nif (%d == %d) { System.out.print(\"%s\"); }\n" % (randint, randint2, randstr),
        ]
        subs = re.search(r'\)\s*\{([\s\S]*)\}', func)
        content = subs.group(1)
        new_content = random.choice(choices) + content
        new_func = func.replace(content, new_content)
        return new_func


    def addForStmt(self, func):
        tmpvar = ''.join(random.choice(ascii_lowercase) for _ in range(6))
        tmpstr = ''.join(random.choice(ascii_lowercase) for _ in range(8))
        randint = random.randint(1, 100)

        choices = [
            "\nint %s=0;\nfor (int i=0; i<%d; i++) {%s++;}\n" % (tmpvar, randint, tmpvar),
            "\nint %s=%d;\nfor (int j=0; j<%d; j++) {%s += j;}\n" % (tmpvar, randint, randint, tmpvar),
            "\nint %s=%d;\nfor (int i=0; i<%s; i++) {System.out.print(\"%s\")}\n" % (tmpvar, randint, tmpvar, tmpstr),
        ]
        subs = re.search(r'\)\s*\{([\s\S]*)\}', func)
        content = subs.group(1)
        new_content = random.choice(choices) + content
        new_func = func.replace(content, new_content)
        return new_func
    
    
    def rmForStmt(self, func):
        all_loops = re.findall(r'((\{|\}|\s+)(for|while)\s*\([\S\s]+?\))', func)
        if not all_loops: return None 
        
        rm_loop = random.choice(all_loops)[0]  # each elem is tuple
        rm_loop_ind = func.find(rm_loop) + len(rm_loop)
        
        next_ch = ""
        while not next_ch == "{":
            next_ch = func[rm_loop_ind]
            rm_loop += next_ch
            rm_loop_ind += 1
            if rm_loop_ind == len(func): return None 

        num_open_br = 1
        while not num_open_br == 0:
            next_ch = func[rm_loop_ind]
            rm_loop += next_ch
            rm_loop_ind += 1
            if next_ch == "{": num_open_br += 1
            elif next_ch == "}": num_open_br -= 1
        
        if "return " not in rm_loop:
            new_func = func.replace(rm_loop, "")
            return new_func
        else: return None
        

    def chBranchCond(self, func):
        tmpstr = ''.join(random.choice(ascii_lowercase) for _ in range(8))
        tmpstr2 = ''.join(random.choice(ascii_lowercase) for _ in range(8))

        choices = [
            "%d / %d + %d == %d * %d"  % (random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)),
            "%d.%d / %d == %d.%d" % (random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)),
            "%d * %d == %d" % (random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)),
            "%s == %s" % (tmpstr, tmpstr),
            "%s != %s" % (tmpstr, tmpstr),
            "%s == %s" % (tmpstr, tmpstr2),
            "%s != %s" % (tmpstr, tmpstr2),
        ]
        all_br = re.findall(r'((\{|\}|\s+)(if|switch)\s*\()', func)
        if not all_br: return None

        ch_br = random.choice(all_br)[0]  # each elem is tuple
        condition_start = func.find(ch_br) + len(ch_br)
        
        condition_end = condition_start
        num_open_br = 1
        while not num_open_br == 0:
            next_ch = func[condition_end]
            condition_end += 1
            if next_ch == "(": num_open_br += 1
            elif next_ch == ")": num_open_br -= 1
        
        new_func = func[:condition_start] + random.choice(choices) + func[condition_end-1:]

        return new_func

    def merge(self, func1, func2):
        func1_signature = func1[:func1.index("(")]
        func2_signature = func2[:func2.index("(")]
        f1_ret_type = func1_signature.split(" ")[-2]
        f2_ret_type = func2_signature.split(" ")[-2]
        
        if not f1_ret_type == f2_ret_type: return None

        subs = re.search('\((.*?)\)', func1)
        f1_params = subs.group(1)
        f1_params = f1_params.strip()
        f1_params_list = f1_params.split(",")
        new_f1_params_list = []
        for f1p in f1_params_list:
            f1p = f1p.replace("[", "").replace("]", "")
            f1p = f1p.strip()
            f1p_name = f1p.split(" ")[-1]
            new_func1 = self.param_replace(func1, f1p_name, f1p_name + "_f1")
            new_f1_params_list.append(f1p + "_f1")
            func1 = new_func1
        new_f1_params = ",".join(new_f1_params_list)

        subs = re.search('\((.*?)\)', func2)
        f2_params = subs.group(1)
        f2_params = f2_params.strip()
        f2_params_list = f2_params.split(",")
        new_f2_params_list = []
        for f2p in f2_params_list:
            f2p = f2p.replace("[", "").replace("]", "")
            f2p = f2p.strip()
            f2p_name = f2p.split(" ")[-1]
            new_func2 = self.param_replace(func2, f2p_name, f2p_name + "_f2")
            new_f2_params_list.append(f2p + "_f2")
            func2 = new_func2
        new_f2_params = ",".join(new_f2_params_list)

        subs = re.search(r'\)\s*\{([\s\S]*)\}', new_func1)
        f1_content = subs.group(1)
        subs = re.search(r'\)\s*\{([\s\S]*)\}', new_func2)
        f2_content = subs.group(1)

        randint = random.randint(1, 100)
        randint2 = random.randint(101, 200)

        merged_func_opts = [

            # TYPE 1
            func1_signature + "(%s, %s, boolean f1){ \n if (f1 && %d == %d) {%s} else {%s} }" % (new_f1_params, new_f2_params, randint, randint, f1_content, f2_content),

            func1_signature + "(%s, %s, boolean f1){ \n if (f1 || %d == %d) {%s} else {%s} }" % (new_f1_params, new_f2_params, randint, randint2, f1_content, f2_content),
            
            # TYPE 2
            func1_signature + "(%s, %s, boolean f1){ \n if (f1 && %d == %d) {%s} else {%s} }" % (new_f2_params, new_f1_params, randint, randint, f1_content, f2_content),

            func1_signature + "(%s, %s, boolean f1){ \n if (f1 || %d == %d) {%s} else {%s} }" % (new_f2_params, new_f1_params, randint, randint2, f1_content, f2_content),            

            # TYPE 3
            func1_signature + "(%s, %s, boolean f1){ \n if (!f1 && %d == %d) {%s} else {%s} }" % (new_f1_params, new_f2_params, randint, randint, f2_content, f1_content),

            func1_signature + "(%s, %s, boolean f1){ \n if (!f1 || %d == %d) {%s} else {%s} }" % (new_f1_params, new_f2_params, randint, randint2, f2_content, f1_content),

            # TYPE 4
            func1_signature + "(%s, %s, boolean f1){ \n if (!f1 && %d == %d) {%s} else {%s} }" % (new_f2_params, new_f1_params, randint, randint, f2_content, f1_content),

            func1_signature + "(%s, %s, boolean f1){ \n if (!f1 || %d == %d) {%s} else {%s} }" % (new_f2_params, new_f1_params, randint, randint2, f2_content, f1_content),
        ]

        merged_func_slc = random.randint(0, 7)
        merged_func = merged_func_opts[merged_func_slc]  # random.choice(merged_func_opts)

        return merged_func, merged_func_slc, len(f1_params_list), len(f2_params_list)
    

    def param_replace(self, func, prm_name, new_prm_name):
        var_usages = re.findall(rf"[\W]{prm_name}[\W]", func)
        var_usages = list(set(var_usages))

        subs_seqs = [vu.replace(prm_name, new_prm_name) for vu in var_usages]

        new_func = func
        for vu, ss in zip(var_usages, subs_seqs):
            new_func = new_func.replace(vu, ss)

        return new_func