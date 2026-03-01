from enum import Enum, auto

import docprisma as dpr

# //////////////////////////////////////////////////////////////////////////////
class ComparisonState(Enum):
    UNMATCHED = auto()
    DIFFERENT = auto()
    EQUAL = auto()

    # --------------------------------------------------------------------------
    @classmethod
    def get_color_pair(cls, state: "ComparisonState"):
        match state:
            case cls.UNMATCHED: return dpr.COLOR_PAIR_UNMATCHED
            case cls.DIFFERENT: return dpr.COLOR_PAIR_DIFFERENT
            case cls.EQUAL: return dpr.COLOR_PAIR_EQUAL


    # --------------------------------------------------------------------------
    @classmethod
    def compare_lists(cls, data: list, ref: list) -> list["ComparisonState"]:
        min_len, max_len = sorted((len(data), len(ref)))
        comparison = [cls.EQUAL if d == r else cls.DIFFERENT for d,r in zip(data, ref)]
        if min_len != max_len:
            comparison += [cls.UNMATCHED for _ in range(max_len - min_len)]
        return comparison


    # --------------------------------------------------------------------------
    @classmethod
    def compare_dicts(cls, keys: list, data: dict, ref: dict) -> list["ComparisonState"]:
        return [cls._compare_d(k, data, ref) for k in keys]


    # --------------------------------------------------------------------------
    @classmethod
    def _compare_d(cls, key, data: dict, ref: dict) -> "ComparisonState":
        if key not in ref: return cls.UNMATCHED
        return cls.EQUAL if data[key] == ref[key] else cls.DIFFERENT


# //////////////////////////////////////////////////////////////////////////////
