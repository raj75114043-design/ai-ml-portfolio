import re
from rapidfuzz import fuzz, process

SUFFIXES = r"\b(pvt|private|ltd|limited|inc|llp)\b"


def normalise(name: str) -> str:
    name = re.sub(SUFFIXES, "", name.lower())
    return re.sub(r"[^a-z0-9 ]", "", name).strip()


def resolve(name: str, master: dict, threshold: int = 85):
    """Map a free-text vendor name to a master vendor ID.

    Returns (vendor_id, score). Matches below the threshold return None for manual review.
    """
    choices = {vid: normalise(vname) for vid, vname in master.items()}
    match = process.extractOne(normalise(name), choices, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        return match[2], round(match[1], 1)
    return None, round(match[1], 1) if match else 0
