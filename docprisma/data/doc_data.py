from pathlib import Path

import docprisma as dpr

# //////////////////////////////////////////////////////////////////////////////
class DocData:
    # --------------------------------------------------------------------------
    def __init__(self, path_doc: Path):
        self.path: Path = path_doc
        self.name: str  = path_doc.name
        self.data: list | dict = None
        self.idx : int = 0 # idx of the current row from self.data

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
        if nlines    is None: nlines = len(self.data) - self.idx
        if filterkey is None: filterkey = lambda _: True

        lines = tuple(
            filter(filterkey, self.data)
        )[self.idx : self.idx+nlines]

        for line in lines:
            yield line


# //////////////////////////////////////////////////////////////////////////////
