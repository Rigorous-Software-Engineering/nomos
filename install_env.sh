# run this script as follows: bash -l install_env.sh
conda create --name nomos_env python=3.8
conda init
conda activate nomos_env

conda install six stringcase transformers ply slimit astunparse submitit
pip install cython
pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
pip install sacrebleu=="1.2.11" javalang tree_sitter psutil fastBPE
pip install antlr4-python3-runtime==4.13
pip install black==19.10b0
pip install scikit-learn==1.0.2
pip install tensorflow==2.7.0
pip install protobuf==3.20.*
pip install Box2D
pip install cloudpickle
pip install pandas==1.5.3
pip install matplotlib
pip install tensorflow-text==2.7.3

cd transpiler/preprocessing/
git clone https://github.com/glample/fastBPE.git

cd fastBPE
g++ -std=c++11 -pthread -O3 fastBPE/main.cc -IfastBPE -o fast
python setup.py install
cd ../

mkdir tree-sitter
cd tree-sitter
git clone https://github.com/tree-sitter/tree-sitter-cpp.git
git clone https://github.com/tree-sitter/tree-sitter-java.git
git clone https://github.com/tree-sitter/tree-sitter-python.git
