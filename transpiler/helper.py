import os
import re
import time
import torch
import pickle
import random

import numpy as np

from os import listdir
from contextlib import contextmanager
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer

from transpiler.Oracle import Oracle
from transpiler.Transformer import Transformer

from transpiler.translate import Translator
from transpiler.preprocessing.utils import TREE_SITTER_ROOT
from transpiler.preprocessing.lang_processors.cpp_processor import CppProcessor
from transpiler.preprocessing.lang_processors.java_processor import JavaProcessor
from transpiler.preprocessing.lang_processors.python_processor import PythonProcessor

from transpiler.preprocessing.lang_processors.lang_processor import LangProcessor

class transpiler():
    def __init__(self) -> None:
        self.inputs = []
        self.cur_inp = ""
        self.cur_test = ""
        self.merged_func_org = ""
        self.merged_func_trans = []

        self.budget = 0
        self.passed = 0
        self.pred_time  = 0
        self.num_dupl_bugs   = 0
        self.precond_violtn  = 0
        self.postcond_violtn = 0

        self.beam_size=1
        self.temperature=0.1

        self.bug_inps = set()
        self.unq_bugs = set()
        self.transformer = Transformer()
        self.oracle = Oracle()
        
        self.cached_preds = {}
        self.inp_code_fname_dict = {}
        self.trns_code_fname_dict = {}

    # UTILITY FUNCTIONS
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

    # Set random seed 
    def setSeed(self, seed):
        random.seed(seed)
        torch.manual_seed(seed)
        np.random.seed(seed)
        self.transformer.setSeed(seed)

    def load(self, model_path):
        self.model_name = model_path.lower().split("/")[-1].split(".")[0]

        cache_file = "transpiler/cache/%s_preds.cache" % self.model_name
        if os.path.isfile(cache_file): self.cached_preds = pickle.load(open(cache_file,'rb'))

        if "starcoder" in self.model_name: 
            checkpoint = "bigcode/starcoder"
            device = "cuda"
            tokenizer = AutoTokenizer.from_pretrained(checkpoint, use_auth_token=True)
            transpiler = AutoModelForCausalLM.from_pretrained(checkpoint, trust_remote_code=True, use_auth_token=True).to(device)
            
            self.starcoder_tokenizer = tokenizer
            self.starcoder_transpiler = transpiler
        elif "transcoder_base" in self.model_name or "transcoder_ir" in self.model_name or "transcoder_dobf" in self.model_name:
            transpiler = Translator(model_path, "transpiler/preprocessing/data/bpe/cpp-java-python/codes")
            self.codegen_transpiler = transpiler
        else:
            print("Check model name!")

        prob_dir_java = 'transpiler/benchmark/java/'
        prob_files_java = listdir(prob_dir_java)
        prob_files_java = [pfj.split(".")[0] for pfj in prob_files_java]

        prob_dir_cpp = 'transpiler/benchmark/cpp/'
        prob_files_cpp = listdir(prob_dir_cpp)
        prob_files_cpp = [pfc.split(".")[0] for pfc in prob_files_cpp]

        prob_dir_py = 'transpiler/benchmark/py/'
        prob_files_py = listdir(prob_dir_py)
        prob_files_py = [pfp.split(".")[0] for pfp in prob_files_py]
        prob_files_intrsctn = set(prob_files_java) & set(prob_files_cpp) & set(prob_files_py)
        prob_files_intrsctn = list(prob_files_intrsctn)

        prob_files_intrsctn = sorted(prob_files_intrsctn)
        self.inputs = prob_files_intrsctn

    def randInput(self):
        self.cur_test = ""  # we are starting a new test
        prob_name = random.choice(self.inputs)

        prob_dir_java = 'transpiler/benchmark/java/'
        with open(prob_dir_java + '/' + prob_name + '.java', 'r') as src_f:
            java_code = src_f.read()

        java_lang_processor = LangProcessor.processors["java"](
            root_folder=TREE_SITTER_ROOT
        )
        tok_java_code = java_lang_processor.tokenize_code(java_code)
        cl_func, _ = java_lang_processor.extract_functions(tok_java_code)

        self.cur_inp = cl_func[0]

        self.inp_code_fname_dict[self.cur_inp] = prob_name

        return self.cur_inp

    def preprocess(self, code_list):
        new_code_list = []
        for code in code_list:
            subs = re.search('\((.*?)\)', code)
            if subs is None: return code  # postc violation 
            params = subs.group(1)
            params = params.strip()
            params_list = params.split(",")
            slc, num_f1_prm, num_f2_prm = self.merge_info
            if not len(params_list) == num_f1_prm + num_f2_prm + 1:
                return code
            
            new_params_list = []
            if slc//2 % 2 == 0:
                # will run f1
                for idx, prm in enumerate(params_list):
                    if idx == len(params_list) -1:
                        new_prm = prm + "=True"
                    elif idx >= num_f1_prm:
                        new_prm = prm + "=None"
                    else: new_prm = prm
                    new_params_list.append(new_prm)
            elif slc//2 % 2 == 1:
                # will run f2
                for idx, prm in enumerate(params_list):
                    if idx == len(params_list) -1:
                        new_prm = prm + "=False"
                    elif idx >= num_f2_prm:
                        new_prm = prm + "=None"
                    else: new_prm = prm
                    new_params_list.append(new_prm)

            new_params = ",".join(new_params_list)
            new_code = code.replace(params, new_params)
            new_code_list.append(new_code)

        return new_code_list

    def process_bug(self):
        num_unq_bugs_b = len(self.unq_bugs)
        self.unq_bugs.add(self.cur_test)
        num_unq_bugs_e = len(self.unq_bugs)
        if num_unq_bugs_b == num_unq_bugs_e: self.num_dupl_bugs += 1

        self.bug_inps.add(self.cur_inp)

    def wrap_up(self):
        os.makedirs(os.path.dirname("transpiler/cache/"), exist_ok=True)
        pickle.dump(self.cached_preds, open( "transpiler/cache/%s_preds.cache" % self.model_name, "wb" ))

    # MODEL CALL
    def transpile(self, code, src_lang="java", tgt_lang="cpp"):
        self.cur_test += code

        if (code, self.beam_size, self.temperature) in self.cached_preds:
            out = self.cached_preds[(code, self.beam_size, self.temperature)]
        elif self.model_name == "starcoder": 
            out = self.predictStarCoder(code, src_lang, tgt_lang)
            self.cached_preds[(code, self.beam_size, self.temperature)] = out
        elif "transcoder_base" in self.model_name or "transcoder_ir" in self.model_name or "transcoder_dobf" in self.model_name : 
            out = self.predictCodegen(code, src_lang, tgt_lang)
            self.cached_preds[(code, self.beam_size, self.temperature)] = out
        else:
            print("Transpilation can not be obtained, check model name.")
        
        if code == self.merged_func_org: self.merged_func_trans = out
        for o in out:
            self.trns_code_fname_dict[o] = self.inp_code_fname_dict[code] 

        return out
    
    def predictStarCoder(self, code, src_lang="java", tgt_lang="cpp"):

        if src_lang == "py": src_lang = "python"
        if tgt_lang == "py": tgt_lang = "python"
        assert src_lang != tgt_lang, "Source and target languages can not be the same."

        prompt = src_lang + ":\n" + code + "\n" + tgt_lang + ":"

        s = time.time()
        inputs = self.starcoder_tokenizer.encode(prompt, return_tensors="pt").to("cuda")
        raw_outputs = self.starcoder_transpiler.generate(inputs, do_sample=True, num_return_sequences=self.beam_size, num_beams=self.beam_size, max_length=3*len(inputs[0]), pad_token_id=self.starcoder_tokenizer.eos_token_id)
    
        outputs = []
        for out in raw_outputs:
            dec_out = self.starcoder_tokenizer.decode(out)
            out_ex_prompt = dec_out.split(tgt_lang + ":")[1]
            # starcoder sometimes proceeds with TOFILL etc. after the transpiled code. Probably, copying what it has seen during its training.
            out_clean = out_ex_prompt.split("#TOFILL")[0]
            out_clean = out_clean.split("//TOFILL")[0]
            subs = re.search(r'def (.*?)\(', out_clean)
            if subs is not None:
                func_name = subs.group(1)
                out_final = out_clean.replace(func_name, "f_gold")
                out_final = out_final.replace("self, ", "")
                out_final = out_final.replace("<|endoftext|>", "")
                
                outputs.append(out_final)
            else:
                outputs.append(out_clean)
        e = time.time()
        self.pred_time += e-s

        return outputs

    def predictCodegen(self, code, src_lang="java", tgt_lang="cpp"):

        if src_lang == "py": src_lang = "python"
        if tgt_lang == "py": tgt_lang = "python"
        assert src_lang != tgt_lang, "Source and target languages can not be the same." 

        s = time.time()
        with torch.no_grad():
            output = self.codegen_transpiler.translate(
                code,
                lang1=src_lang,
                lang2=tgt_lang,
                beam_size=self.beam_size,
                sample_temperature=self.temperature,
            )
        
        e = time.time()
        self.pred_time += e-s
        
        return output

    # PROGRAM INSPECTION FUNCTION (COMPIALTION)
    def compiles(self, funcs, lang):
        if not type(funcs) == list: funcs = [funcs]

        # some properties require checkign compilation of input code, some require checking output code, and checking the first element of code list is enough
        if funcs[0] in self.trns_code_fname_dict:
            prob_name = self.trns_code_fname_dict[funcs[0]]  
        else:
            prob_name = self.inp_code_fname_dict[funcs[0]]

        # if there is an intersection, it means that we checking compilation of merged function transpilation, no need to look into merged_func_org - we dont check compilation of input program in merge properties
        if set(self.merged_func_trans) & set(funcs):
            funcs = self.preprocess(funcs)

        comp_ls = []
        for func in funcs:
            if lang == "java":
                res = self.oracle.compileOracleJava(func, prob_name)
            elif lang == "cpp":
                res = self.oracle.compileOracleCpp(func, prob_name)
            elif lang == "py":
                res = self.oracle.compileOraclePy(func, prob_name)

            comp_ls.append(res)
        
        return comp_ls if len(comp_ls) > 1 else comp_ls[0]

    # PROGRAM INSPECTION FUNCTIONS (SYNTACTIC)
    def numLoops(self, funcs, lang):
        if not type(funcs) == list: funcs = [funcs]
        numLoops = []
        for func in funcs:
            if lang == "java":
                numLoops.append(self.oracle.numLoopsJava(func))
            elif lang == "cpp":
                numLoops.append(self.oracle.numLoopsCpp(func))
            elif lang == "py":
                numLoops.append(self.oracle.numLoopsPy(func))
        return numLoops if len(numLoops) > 1 else numLoops[0]

    def numConditionals(self, funcs, lang):
        if not type(funcs) == list: funcs = [funcs]
        numConditionals = []
        for func in funcs:
            if lang == "java":
                numConditionals.append(self.oracle.numConditionalsJava(func))
            elif lang == "cpp":
                numConditionals.append(self.oracle.numConditionalsCpp(func))
            elif lang == "py":
                numConditionals.append(self.oracle.numConditionalsPy(func))
        return numConditionals if len(numConditionals) > 1 else numConditionals[0]

    def arity(self, funcs, lang):
        if not type(funcs) == list: funcs = [funcs]
        arities = []
        for func in funcs:
            if lang == "java":
                arities.append(self.oracle.checkArityJava(func))
            elif lang == "cpp":
                arities.append(self.oracle.checkArityCpp(func))
            elif lang == "py":
                arities.append(self.oracle.checkArityPy(func))
        return arities if len(arities) > 1 else arities[0]
    
    # PROGRAM INSPECTION FUNCTIONS (SEMANTIC)
    def retValues(self, funcs, lang):
        if not type(funcs) == list: funcs = [funcs]

        # some properties require checkign compilation of input code, some require checking output code, and checking the first element of func list is enough
        if funcs[0] in self.trns_code_fname_dict:
            prob_name = self.trns_code_fname_dict[funcs[0]]  
        else:
            prob_name = self.inp_code_fname_dict[funcs[0]]

        # if there is an intersection
        if set(self.merged_func_trans) & set(funcs):
            funcs = self.preprocess(funcs)

        results = []
        for func in funcs:
            if lang == "java":
                res = self.oracle.runJava(func, prob_name)
            elif lang == "cpp":
                res = self.oracle.runCpp(func, prob_name)
            elif lang == "py":
                res = self.oracle.runPy(func, prob_name)
            results.append(res)
        return results if len(results) > 1 else results[0]

    # PROGRAM TRANSFORMATION FUNCTIONS
    def addParam(self, func, lang="java"):
        if lang=="java": 
            out_func = self.transformer.addParamJava(func)
            self.inp_code_fname_dict[out_func] = self.inp_code_fname_dict[func]
            return out_func
        else: return None
    
    def addConditional(self, func, lang="java"):
        if lang=="java": 
            out_func = self.transformer.addIfStmt(func)
            self.inp_code_fname_dict[out_func] = self.inp_code_fname_dict[func]
            return out_func
        else: return None
    
    def chBranchCond(self, func, lang="java"):
        if lang=="java": 
            out_func = self.transformer.chBranchCond(func)
            self.inp_code_fname_dict[out_func] = self.inp_code_fname_dict[func]
            return out_func
        else: return None

    def addLoop(self, func, lang="java"):
        if lang=="java": 
            out_func = self.transformer.addForStmt(func)
            self.inp_code_fname_dict[out_func] = self.inp_code_fname_dict[func]
            return out_func
        else: return None

    def rmLoop(self, func, lang="java"):
        if lang=="java": 
            out_func = self.transformer.rmForStmt(func)
            self.inp_code_fname_dict[out_func] = self.inp_code_fname_dict[func]
            return out_func
        else: return None

    def renameParam(self, func, lang="java"):
        if lang=="java": 
            out_func = self.transformer.renameParam(func)
            self.inp_code_fname_dict[out_func] = self.inp_code_fname_dict[func]
            return out_func
        else: return None

    def merge(self, func1, func2, lang="java"):
        if lang=="java": 
            merged_func, slc, num_f1_prm, num_f2_prm = self.transformer.merge(func1, func2)
            self.merge_info = (slc, num_f1_prm, num_f2_prm)
            self.merged_func_org = merged_func

            f1_func_name = self.inp_code_fname_dict[list(self.inp_code_fname_dict.keys())[0]]
            f2_func_name = self.inp_code_fname_dict[list(self.inp_code_fname_dict.keys())[1]]

            if slc//2 % 2 == 0: 
                self.inp_code_fname_dict[merged_func] = f1_func_name
            else:
                self.inp_code_fname_dict[merged_func] = f2_func_name

            return merged_func

        else: return None
