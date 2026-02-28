import sys
from pathlib import Path

import docprisma as dpr

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("usage: docprisma [paths...]")
        exit(-1)

    PATHS_DOC = [Path(p) for p in sys.argv[1:]]
    dpr.TUIDocPrisma(*PATHS_DOC).run()


################################################################################
if __name__ == "__main__":
    main()


################################################################################
