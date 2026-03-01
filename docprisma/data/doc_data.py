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
        self.idx: int = 0  # highlighted row
        self.ypos: int = 0
        self.section_width = 0

        self._comparison_partner: "DocData" | None = None
        self._comparison_states: list[dpr.ComparisonState] | None = []


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


    # --------------------------------------------------------------------------
    def get_chars_attrs(self, nlines: int = None) -> tuple[list[str], list[list[int]]]:
        return [], []


    # --------------------------------------------------------------------------
    def get_nodes_path(self) -> str:
        return ""


    # --------------------------------------------------------------------------
    def prev_node(self) -> None:
        return


    # --------------------------------------------------------------------------
    def next_node(self) -> None:
        return


    # --------------------------------------------------------------------------
    def _iter_children(self, nlines: int = None):
        if nlines is None: nlines = len(self.data)
        lines = self.data[self.ypos : self.ypos+nlines]
        yield from lines


    # --------------------------------------------------------------------------
    def _get_comparison_attr(self, idx: int) -> int:
        if self._comparison_states is None: return pr.A_NORMAL
        return dpr.ComparisonState.get_color_pair(self._comparison_states[idx])


# //////////////////////////////////////////////////////////////////////////////
