def _get_entities_filter_kw(entity, entity_example_text):
    entities_kw = []
    for kw in entity.entitykeyword_set.all():
        if entity_example_text in kw.text:
            entities_kw.append(kw.text)
    if len(entities_kw) != 0:
        return {"id": entity.id, "name": entity.name, "description": entity.description,
                "extract_type": entity.extract_type, "keyword": entities_kw}
    else:
        return None
