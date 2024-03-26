from pathlib import Path

TREE_SITTER_ROOT = Path(__file__).parents[0].joinpath("tree-sitter")

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self