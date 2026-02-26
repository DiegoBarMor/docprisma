import json
from pathlib import Path

import docprisma as dpr

# //////////////////////////////////////////////////////////////////////////////
class DocJson(dpr.DocData):
    def __init__(self, path_json: Path):
        super().__init__(path_json)
        self._root : list | dict = json.loads(path_json.read_text()) # the data is actually stored in the root node
        self.data  : list | dict = self._root # "self.data" then becomes a pointer that can move around the nodes' hierarchy

        self._prev_idxs  : list[int] = [] # store the values of "self.idx" for previous nodes
        self._prev_nodes : list[list | dict] = [] # store the pointers for previous nodes


    # --------------------------------------------------------------------------
    def iter_lines(self, nlines: int = None):
        node_is_dict = isinstance(self.data, dict)
        for child in super().iter_lines(nlines, filterkey = None):
            if node_is_dict:
                key = child
                child = self.data[key]
                out = f"{key}: "
            else:
                out = ""

            child_kind = "list" if isinstance(child, list) else "dict"
            yield f"{out}{child_kind}[{len(child)}]"


# //////////////////////////////////////////////////////////////////////////////
