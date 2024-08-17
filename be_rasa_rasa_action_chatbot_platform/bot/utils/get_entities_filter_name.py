def _get_entities_filter_name(entity, entity_name):
    if entity_name in entity.name:
        print("search entity name: ", entity_name)
        print("entity.name: ", entity.name)
        entities_kw = [kw.text for kw in entity.entitykeyword_set.all()]
        return {"id": entity.id, "name": entity.name, "description": entity.description,
                "extract_type": entity.extract_type, "keyword": entities_kw}
    else:
        return None
