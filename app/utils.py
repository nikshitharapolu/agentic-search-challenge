def dedupe_entities(rows):
    """
    Deduplicate entities by name, type
    If multiple sources mention the same entity, we keep just one row
    """
    seen = set()
    out = []
    for r in rows:
        key = (r.entity_name.lower().strip(), r.entity_type.lower().strip())
        if key not in seen:
            seen.add(key)
            out.append(r)

    return out