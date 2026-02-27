import json
from pathlib import Path

import docprisma as dpr

# ------------------------------------------------------------------------------
def is_container(node) -> bool:
    return isinstance(node, (list, dict))

# //////////////////////////////////////////////////////////////////////////////
class DocJson(dpr.DocData):
    def __init__(self, path_json: Path):
        super().__init__(path_json)
        self.data : list = [] # either a list from the json directly, or the sorted keys if the current json node is a dict

        self._root : list | dict = json.loads(path_json.read_text()) # the data is actually stored in the root node
        self._node : list | dict = self._root # pointer that can move around the nodes' hierarchy
        self._prev_idxs  : list[int] = [] # store the values of "self.idx" for previous nodes
        self._prev_nodes : list[list | dict] = [] # store the pointers for previous nodes
        self._nodes_path : str = "/" # string with the path of the current node

        self._update_data()

    # --------------------------------------------------------------------------
    def iter_lines(self, nlines: int = None):
        node_is_dict = isinstance(self._node, dict)
        children = tuple(super().iter_lines(nlines = None, filterkey = None))

        if node_is_dict or any(map(is_container, children)):
            for child in children[self.ypos : self.ypos+nlines]:
                if node_is_dict:
                    key = child
                    child = self._node[key]
                    out = f"{key}: "
                else:
                    out = f"({type(child).__name__}): "

                if isinstance(child, list):
                    yield f"{out}list[{len(child)}]"
                elif isinstance(child, dict):
                    yield f"{out}dict[{len(child)}]"
                else:
                    yield f"{out}{child}"
            return

        # children: list[str] = [
        #     f'"{child}"' if isinstance(child, str) else str(child)
        #     for child in children
        # ]


        children = tuple(map(str, children))

        w = 0; i0 = 0
        for idx,child in enumerate(children):
            w += len(child) + 1
            if w <= self.section_width: continue
            w = 0

            i1 = idx if idx != i0 else i0+1
            yield ' '.join(children[i0:i1])
            i0 = i1
        yield ' '.join(children[i0:])


    # --------------------------------------------------------------------------
    def get_nodes_path(self) -> str:
        return self._nodes_path


    # --------------------------------------------------------------------------
    def prev_node(self) -> None:
        if not self._prev_nodes: return
        self.idx = self._prev_idxs.pop()
        self._node = self._prev_nodes.pop()
        self._nodes_path = self._nodes_path.rsplit('/', 2)[0] + '/'
        self._update_data()


    # --------------------------------------------------------------------------
    def next_node(self):
        key = self.data[self.idx] if isinstance(self._node, dict) else self.idx
        child = self._node[key]

        if not is_container(child): return

        self._prev_idxs.append(self.idx)
        self._prev_nodes.append(self._node)
        self.idx = 0
        self._node = child
        self._nodes_path += f"{key}/"
        self._update_data()


    # --------------------------------------------------------------------------
    def _update_data(self):
        self.data = self._node if isinstance(self._node, list) else sorted(self._node.keys())


# //////////////////////////////////////////////////////////////////////////////
