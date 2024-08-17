def _get_entities_kw_extract_type(entity):
    entities_kw = [kw.text for kw in entity.entitykeyword_set.all()]
    return {"id": entity.id, "name": entity.name, "extract_type": entity.extract_type, "keyword": entities_kw}
