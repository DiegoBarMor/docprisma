from pathlib import Path

import prismatui as pr

import docprisma as dpr

# //////////////////////////////////////////////////////////////////////////////
class DocData:
    # --------------------------------------------------------------------------
    def __init__(self, path_doc: Path = None):
        self.path: Path = path_doc if path_doc is not None else Path()
        self.name: str  = self.path.name
        self.data: list | dict = []
        self.section_width:int = 0
        self.idx_row_top: int = 0
        self.idx_row_current: int = 0 # row with the currently highlighted child
        self.idx_child_current: int = 0  # currently highlighted child

        self._comparison_partner: "DocData" | None = None
        self._comparison_states: list[dpr.ComparisonState] | None = None


    # --------------------------------------------------------------------------
    @staticmethod
    def load_doc(path_doc: Path) -> "DocData":
        if path_doc.suffix.lower() == ".json":
            return dpr.DocJson(path_doc)
        if path_doc.suffix.lower() == ".csv":
            raise NotImplementedError()
        raise NotImplementedError()


    # --------------------------------------------------------------------------
    def link_comparison_partner(self, other: "DocData"):
        self ._comparison_partner = other
        other._comparison_partner = self
        self.update_comparison_states()
        other.update_comparison_states()


    # --------------------------------------------------------------------------
    def update_comparison_states(self) -> None:
        self._comparison_states = None


    # ------------------------------------------------------------------------------
    def update_idx_row_top(self, ref_h: int):
        y_rel = self.idx_row_current - self.idx_row_top
        if y_rel < 0:
            self.idx_row_top = self.idx_row_current
        elif y_rel >= ref_h:
            self.idx_row_top = self.idx_row_current - ref_h + 1


    # --------------------------------------------------------------------------
    def update_idx_row_current(self):
        self.idx_row_current = self.idx_child_current


    # ------------------------------------------------------------------------------
    def reset_idx_row_top(self):
        self.idx_row_top = 0


    # --------------------------------------------------------------------------
    def get_chars_attrs(self, nlines: int = None) -> tuple[list[str], list[list[int]]]:
        return [], []


    # --------------------------------------------------------------------------
    def get_nodes_path(self) -> str:
        return ""


    # --------------------------------------------------------------------------
    def scroll_up(self, nlines: int, href: int):
        self.idx_child_current = max(0, self.idx_child_current - nlines)
        self.update_idx_row_current()
        self.update_idx_row_top(href)


    # --------------------------------------------------------------------------
    def scroll_down(self, nlines: int, href: int):
        self.idx_child_current = min(self.idx_child_current + nlines, len(self.data) - 1)
        self.update_idx_row_current()
        self.update_idx_row_top(href)


    # --------------------------------------------------------------------------
    def prev_node(self) -> None:
        return


    # --------------------------------------------------------------------------
    def next_node(self) -> None:
        return


    # --------------------------------------------------------------------------
    def _iter_children(self, nlines: int = None):
        if nlines is None: nlines = len(self.data)
        lines = self.data[self.idx_row_top : self.idx_row_top+nlines]
        yield from lines


    # --------------------------------------------------------------------------
    def _get_comparison_attr(self, idx: int) -> int:
        if self._comparison_states is None: return pr.A_NORMAL
        return dpr.ComparisonState.get_color_pair(self._comparison_states[idx])


# //////////////////////////////////////////////////////////////////////////////
