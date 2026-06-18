from __future__ import annotations

import re


MOJIBAKE_MARKERS = ("窶", "遯", "蜀", "闃", "謨", "ｦ", "")

ASCII_PUNCT_TRANSLATION = str.maketrans({
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
})

EXACT_MOJIBAKE_REPLACEMENTS: tuple[tuple[str, str], ...] = ()

REGEX_MOJIBAKE_REPLACEMENTS = (
    (re.compile(r"n窶冲"), "n't"),
    (re.compile(r"(\w)窶冱"), r"\1's"),
    (re.compile(r"(\w)窶决e"), r"\1're"),
    (re.compile(r"(\w)窶冤l"), r"\1'll"),
    (re.compile(r"(\w)窶囘"), r"\1'd"),
    (re.compile(r"(\w)窶况e"), r"\1've"),
    (re.compile(r"窶ｦ"), "..."),
    (re.compile(r"窶拿n"), '"\n'),
    (re.compile(r"窶・"), '"'),
)


def normalize_char_attribute(raw_attribute : dict) -> dict:
    data = dict(raw_attribute)

    if data.get("characterId") and not data.get("characterIds"):
        data["characterIds"] = [data.get("characterId")]
    elif data.get("characterName") and not data.get("characterNames"):
        data["characterNames"] = [data.get("characterName")]
    
    return data

def normalize(var):
    if isinstance(var, list):
        var = var[0]
    return var


def _ascii_normalize_text(text: str) -> str:
    normalized = text.translate(ASCII_PUNCT_TRANSLATION)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n", "\n", normalized)
    return normalized


def repair_mojibake_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    if not any(marker in text for marker in MOJIBAKE_MARKERS):
        return text

    repaired = text

    for old, new in EXACT_MOJIBAKE_REPLACEMENTS:
        repaired = repaired.replace(old, new)

    for pattern, replacement in REGEX_MOJIBAKE_REPLACEMENTS:
        repaired = pattern.sub(replacement, repaired)

    repaired = repaired.translate(ASCII_PUNCT_TRANSLATION)
    repaired = repaired.encode("ascii", "ignore").decode("ascii")

    repaired = re.sub(r" {2,}", " ", repaired)
    repaired = re.sub(r" *\n", "\n", repaired)

    return repaired


def sanitize_agent_output(text: str) -> tuple[str, bool]:
    repaired = repair_mojibake_text(text)
    return repaired, repaired != text
