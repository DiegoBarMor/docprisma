import sys
from pathlib import Path

import docprisma as dpr

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    if len(sys.argv) < 2:
        print("usage: docprisma [path_doc]")
        exit(-1)

    PATH_DOC = Path(sys.argv[1])
    dpr.TUIDocPrisma(PATH_DOC).run()


################################################################################
if __name__ == "__main__":
    main()


################################################################################
