def _get_intent_exp_data(intent_exp):
    intent = {
        "intent_id": str(intent_exp.intent.id),
        "intent_name": intent_exp.intent.name
    } if intent_exp.intent else {}

    entity_keywords = intent_exp.entitykeyword_set.all()
    entity_data = [
        {
            "id_entity": ek.entity.id,
            "entity": ek.entity.name,
            "id_entity_kw": ek.id,
            "entity_keyword": ek.text,
            "start_position": ek.start_position,
            "end_position": ek.end_position
        }
        for ek in entity_keywords if ek.entity
    ]

    return {
        "id": str(intent_exp.id),
        "text": intent_exp.text,
        "intent": intent,
        "entity": entity_data
    }

# def _get_intent_exp_data(intent_exp):
#     intent_name = [intent_exp.intent.name] if intent_exp.intent else []
#     entity_keywords = intent_exp.entitykeyword_set.all()
#     entity_name = [ek.entity.name for ek in entity_keywords if ek.entity]
#     return {"id": intent_exp.id, "text": intent_exp.text, "intent": intent_name, "entity": entity_name}
#


def _get_intent_exp_data_detail(intent_exp):
    intent = {
        "intent_id": str(intent_exp.intent.id),
        "intent_name": intent_exp.intent.name
    } if intent_exp.intent else {}

    entity_keywords = intent_exp.entitykeyword_set.all()
    entity_name = [
        {
            "id_entity": ek.entity.id,
            "entity": ek.entity.name,
            "id_entity_kw": ek.id,
            "entity_keyword": ek.text,
            "start_position": ek.start_position,
            "end_position": ek.end_position
        }
        for ek in entity_keywords if ek.entity
    ]
    return {
        "id": intent_exp.id,
        "text": intent_exp.text,
        "intent": intent,
        "entity_name": entity_name
    }
