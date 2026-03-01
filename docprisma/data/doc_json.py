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
        self._prev_idxs  : list[int] = [] # store the values of "self.idx_child_current" for previous nodes
        self._prev_nodes : list[list | dict] = [] # store the pointers for previous nodes
        self._nodes_path : str = "/" # string with the path of the current node

        self._update_data()


    # --------------------------------------------------------------------------
    def get_chars_attrs(self, nlines: int = None):
        if nlines <= 0: return [], []

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
        self._node = self._prev_nodes.pop()
        self._nodes_path = self._nodes_path.rsplit('/', 2)[0] + '/'

        self.idx_child_current = self._prev_idxs.pop()
        self.idx_row_current = self.idx_child_current

        self._update_data()


    # --------------------------------------------------------------------------
    def next_node(self):
        key = self.data[self.idx_child_current] if isinstance(self._node, dict) else self.idx_child_current
        child = self._node[key]

        if not is_container(child): return
        self._node = child
        self._nodes_path += f"{key}/"
        self._prev_nodes.append(self._node)

        self._prev_idxs.append(self.idx_child_current)
        self.idx_child_current = 0
        self.idx_row_current = 0
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
    def update_idx_row_current(self):
        if self._node_is_leaf: return
        super().update_idx_row_current()


    # --------------------------------------------------------------------------
    def _update_data(self):
        has_container_children = any(map(is_container, self._iter_children()))

        self._node_is_dict = isinstance(self._node, dict)
        self._node_is_leaf = not (self._node_is_dict or has_container_children)
        self.data = sorted(self._node.keys()) if self._node_is_dict else self._node


    # --------------------------------------------------------------------------
    def _subroutine_chars_attrs_leaf_idxs(self, children, nlines: int):
        i0 = 0
        cum_len = 0
        yield_count = 0
        comparison_colors = []

        highlight_start = 0
        highlight_end = 0
        highlighted_row: int | None = None

        for idx_child,child in enumerate(children):
            if (highlighted_row is not None) and (yield_count > nlines): break

            i1 = idx_child + 1
            is_last_iter = i1 == len(children)
            this_len = len(child)
            next_len = len(children[i1]) if not is_last_iter else 0

            if idx_child == self.idx_child_current:
                highlight_start = cum_len
                highlight_end = cum_len + this_len
                highlighted_row = yield_count
                yield_count = 0

            this_len += 1 # account for the space between rows
            comparison_colors.extend(self._get_comparison_attr(idx_child) for _ in range(this_len))
            cum_len += this_len

            if not is_last_iter and (cum_len + next_len < self.section_width):
                continue

            yield i0, i1, highlight_start, highlight_end, highlighted_row, comparison_colors

            cum_len = 0
            yield_count += 1
            highlight_start = 0
            highlight_end = 0
            comparison_colors = []
            i0 = i1


    # --------------------------------------------------------------------------
    def _iter_chars_attrs_leaf(self, nlines: int):
        self.idx_row_top = 0 # ignore previous corrections when fetching the children
        children = tuple(map(str, self._iter_children()))

        arr_i0, arr_i1s, arr_hs, arr_he, arr_highlighted, arr_colors =\
            zip(*self._subroutine_chars_attrs_leaf_idxs(children, nlines))

        idx_highlighted = max((i for i in arr_highlighted if i is not None), default = 0)
        self.idx_row_current = idx_highlighted # bring back self.idx_row_top to an useful value
        self.update_idx_row_top(ref_h = nlines)

        zipped = zip(arr_i0, arr_i1s, arr_hs, arr_he, arr_colors)
        for idx_row,(i0, i1, hstart, hend, colors) in enumerate(zipped):
            if idx_row < self.idx_row_top: continue
            if idx_row > self.idx_row_top + nlines: break

            row_chars = ' '.join(children[i0:i1])
            row_attrs = [
                color | (pr.A_REVERSE if hstart <= j < hend else pr.A_NORMAL)
                for j,color in enumerate(colors)
            ]
            yield row_chars, row_attrs


    # --------------------------------------------------------------------------
    def _iter_chars_attrs_nonleaf(self, nlines: int):
        children = self._iter_children(nlines)
        for i,child in enumerate(tuple(children)):
            idx = i + self.idx_row_top

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

            attr_highlight = pr.A_REVERSE if idx == self.idx_child_current else pr.A_NORMAL
            color = self._get_comparison_attr(idx)
            row_attrs = [color | attr_highlight for _ in row_chars]

            yield row_chars, row_attrs


# //////////////////////////////////////////////////////////////////////////////
