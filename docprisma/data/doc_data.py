from pathlib import Path

import prismatui as pr

import docprisma as dpr

# //////////////////////////////////////////////////////////////////////////////
class DocData:
    # --------------------------------------------------------------------------
    def __init__(self, path_doc: Path):
        self.path: Path = path_doc
        self.name: str  = path_doc.name
        self.data: list | dict = None
        self.idx: int = 0  # highlighted row
        self.ypos: int = 0
        self.section_width = 0

    # --------------------------------------------------------------------------
    @staticmethod
    def load_doc(path_doc: Path) -> "DocData":
        if path_doc.suffix.lower() == ".json":
            return dpr.DocJson(path_doc)
        if path_doc.suffix.lower() == ".csv":
            raise NotImplementedError()
        raise NotImplementedError()

    # --------------------------------------------------------------------------
    def iter_lines(self, nlines: int = None, filterkey: callable = None):
        if nlines    is None: nlines = len(self.data)
        if filterkey is None: filterkey = lambda _: True

        lines = tuple(
            filter(filterkey, self.data)
        )[self.ypos : self.ypos+nlines]

        for line in lines:
            yield line

    # --------------------------------------------------------------------------
    def get_chars_attrs(self, nlines: int = None):
        lines = tuple(self.iter_lines(nlines))
        w_max = max(map(len, lines), default = 0)
        chars = [line.ljust(w_max) for line in lines]
        attrs = [w_max*[pr.A_REVERSE if i == self.idx else pr.A_NORMAL] for i in range(len(chars))]
        return chars, attrs

    # --------------------------------------------------------------------------
    def get_nodes_path(self) -> str:
        return ""

    # --------------------------------------------------------------------------
    def prev_node(self) -> None:
        pass

    # --------------------------------------------------------------------------
    def next_node(self) -> None:
        pass


# //////////////////////////////////////////////////////////////////////////////
