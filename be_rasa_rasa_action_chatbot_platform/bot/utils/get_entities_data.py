def _get_entities_data(entity):
    entities_kw = [kw.text for kw in entity.entitykeyword_set.all()]
    return {"id": entity.id, "name": entity.name, "description": entity.description,
            "extract_type": entity.extract_type, "entities_kw": entities_kw}
