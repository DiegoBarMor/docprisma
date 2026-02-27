import json
from pathlib import Path

import prismatui as pr

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
            for i,child in enumerate(children[self.ypos : self.ypos+nlines]):
                idx = i + self.ypos

                if node_is_dict:
                    key = child
                    child = self._node[key]
                    out = f"{key}: "
                else:
                    out = f"({type(child).__name__}): "

                if isinstance(child, list):
                    out = f"{out}list[{len(child)}]"
                elif isinstance(child, dict):
                    out = f"{out}dict[{len(child)}]"
                else:
                    out = f"{out}{child}"

                highlight_end = len(out) if idx == self.idx else 0
                yield out, 0, highlight_end
            return

        i0 = 0
        out = ""
        highlight_start = 0
        highlight_end = 0
        children = tuple(map(str, children))
        for idx,child in enumerate(children):
            last_iter = idx == len(children) - 1

            if idx == self.idx:
                highlight_start = len(out)
                highlight_end = highlight_start + len(child)

            out += child + " "

            next_len = len(out) + (len(children[idx+1]) if not last_iter else 0)

            if not last_iter and (next_len < self.section_width):
                continue

            i1 = idx + 1

            yield ' '.join(children[i0:i1]), highlight_start, highlight_end
            highlight_start = 0
            highlight_end = 0
            out = ""
            i0 = i1


    # --------------------------------------------------------------------------
    def get_chars_attrs(self, nlines: int = None):
        lines,h_starts,h_ends = zip(*self.iter_lines(nlines))
        w_max = max(map(len, lines), default = 0)
        chars = [line.ljust(w_max) for line in lines]
        attrs = [
            hs*[pr.A_NORMAL] + (he-hs)*[pr.A_REVERSE] + (w_max-he)*[pr.A_NORMAL]
            for hs,he in zip(h_starts, h_ends)
        ]
        return chars, attrs


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
