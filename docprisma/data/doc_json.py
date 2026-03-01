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
        self._node_is_dict = False
        self._node_is_leaf = False

        self._root : list | dict = json.loads(path_json.read_text()) # the data is actually stored in the root node
        self._node : list | dict = self._root # pointer that can move around the nodes' hierarchy
        self._prev_idxs  : list[int] = [] # store the values of "self.idx" for previous nodes
        self._prev_nodes : list[list | dict] = [] # store the pointers for previous nodes
        self._nodes_path : str = "/" # string with the path of the current node

        self._update_data()


    # --------------------------------------------------------------------------
    def get_chars_attrs(self, nlines: int = None):
        iterator = self._iter_chars_attrs_leaf if self._node_is_leaf else self._iter_chars_attrs_nonleaf
        lines,attrs = zip(*iterator(nlines))
        w_max = max(map(len, lines), default = 0)
        chars = [line.ljust(w_max) for line in lines]
        attrs = [
            row_attrs + (w_max-len(row_attrs))*[pr.A_NORMAL]
            for row_attrs in attrs
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
    def update_comparison_states(self) -> None:
        if self._comparison_partner is None:
            self._comparison_states = None
            return

        other = self._comparison_partner
        if not isinstance(other, DocJson):
            self._comparison_states = None
            return

        if self._node_is_dict:
            self ._comparison_states = dpr.ComparisonState.compare_dicts(
                keys = self.data, data = self._node, ref = other._node
            ) if other._node_is_dict else None

        else:
            self._comparison_states = dpr.ComparisonState.compare_lists(
                data = self._node, ref = other._node
            ) if not other._node_is_dict else None


    # --------------------------------------------------------------------------
    def _update_data(self):
        has_container_children = any(map(is_container, self._iter_children()))

        self._node_is_dict = isinstance(self._node, dict)
        self._node_is_leaf = not (self._node_is_dict or has_container_children)
        self.data = sorted(self._node.keys()) if self._node_is_dict else self._node


    # --------------------------------------------------------------------------
    def _iter_chars_attrs_leaf(self, nlines: int):
        i0 = 0
        highlight_start = 0
        highlight_end = 0
        buffer = ""
        comparison_colors = []
        children = tuple(map(str, self._iter_children()))
        for idx,child in enumerate(children):
            last_iter = idx == len(children) - 1

            if idx == self.idx:
                highlight_start = len(buffer)
                highlight_end = highlight_start + len(child)

            child += " "

            buffer += child
            comparison_colors += [self._get_comparison_attr(idx) for _ in child]

            next_len = len(buffer) + (len(children[idx+1]) if not last_iter else 0)

            if not last_iter and (next_len < self.section_width):
                continue

            i1 = idx + 1

            row_chars = ' '.join(children[i0:i1])
            row_attrs = [
                color | (pr.A_REVERSE if highlight_start <= j < highlight_end else pr.A_NORMAL)
                for j,color in enumerate(comparison_colors)
            ]

            yield row_chars, row_attrs
            highlight_start = 0
            highlight_end = 0
            buffer = ""
            comparison_colors.clear()
            i0 = i1


    # --------------------------------------------------------------------------
    def _iter_chars_attrs_nonleaf(self, nlines: int):
        children = self._iter_children(nlines)
        for i,child in enumerate(tuple(children)):
            idx = i + self.ypos

            if self._node_is_dict:
                key = child
                child = self._node[key]
                row_chars = f"{key}: "
            else:
                row_chars = f"({type(child).__name__}): "

            if isinstance(child, list):
                row_chars = f"{row_chars}list[{len(child)}]"
            elif isinstance(child, dict):
                row_chars = f"{row_chars}dict[{len(child)}]"
            else:
                row_chars = f"{row_chars}{child}"

            attr_highlight = pr.A_REVERSE if idx == self.idx else pr.A_NORMAL
            color = self._get_comparison_attr(idx)
            row_attrs = [color | attr_highlight for _ in row_chars]

            yield row_chars, row_attrs


# //////////////////////////////////////////////////////////////////////////////
