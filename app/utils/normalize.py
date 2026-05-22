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
