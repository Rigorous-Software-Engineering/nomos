# NOMOS

This repository contains our implementation of the NOMOS specification language and its application to testing and re-training of ML models. This language and our testing framework are introduced in our paper "Specifying and Testing _k_-Safety Properties for Machine-Learning Models".


## Spcification Language

The NOMOS grammar is presented in the `Nomos.g4` file of the main directory. We use *ANTLR4* for parsing the grammar and the language semantics are implemeted in `lang/MyNomosVisitor.py`. The parser, lexer and other necessary files have to be created using the following command:

`antlr4 -Dlanguage=Python3 Nomos.g4 -visitor -o lang`

This requires an *ANTLR4* installation, including its *python-runtime*. The above command will generate the parser, lexer and other necessary files under the `lang` folder. `main.py` translates a NOMOS specification into Python3 code, namely the test harness. The following command illustrates how to translate a specification file:

`python3 main.py <benchmark_name> <path_to_spec_file>`

`<benchmark_name>` refers to the name of the benchmark that the ML model is traind on. A folder with this name must exist in the main directory and it should contain a file named `helper.py`; this file needs to provide necessary functions for testing the specification such as loading the model and loading inputs. See `compas/helper.py` for an example. `<path_to_spec_file>` refers to the path to the specification file. Check the following section to see where to find the specifications tested in the paper. 

Upon successful execution of the above command a python file should be created und `<benchmark_name>/harness_<spec_name>.py`, where `<spec_name>` is the specification file name without the `.nom` file extension. See `compas/harness_felony_inc.py` for an example. We describe how to test the model below.


## Specifications

This repository also contains all NOMOS specifications that we used to test models in the above paper. The specification files can be found in the following directories:

- `compas/specs/*.nom`
- `german_credit/specs/*.nom`
- `mnist/specs/*.nom`
- `speech_command/specs/*.nom`
- `hotel_review/specs/*.nom`
- `lunar/specs/*.nom`


## Testing Models

The created test harness is used to check if the specification holds for a given ML model. A harness takes three inputs from the user:

1. a random seed: an integer to seed the random number generator
2. the path to the model: the path of the model file that will be loaded by `helper.py`
3. the test budget (i.e., the number of inputs for which the postcondition should be checked)

For example, the following command runs the test harness `compas.harness_felony_inc` for our Compas model `compas/compas_dt_model.p` with random seed 42 and budget 5000:

`python3 -m compas.harness_felony_inc 42 compas/compas_dt_model.p 5000`

Upon successful execution, a summary of the testing campaign is printed to the standard output.

## Feasibility Study: Using Bugs for Model Training

For our feasibility study, we devise a new /guided/ RL training scheme (by extending standard PPO training) where we incorporate the states on which we identify bugs in the current or past policies. Our guided training algorithm can be started using the following command:

`python3 -m lunar.train_agents <timesteps> guided <rand_seed>`

`<timesteps>` is (usually) a large integer such as 1 million and `<rand_seed>` is an integer to seed the random number generator that is used for training.
