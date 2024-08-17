def _get_intent_data(intent):
    int_exps = [exp.text for exp in intent.intentexample_set.all() if str(exp.intent) == str(intent.name)]
    return {"id": intent.id, "description": intent.description, "name": intent.name, "int_exps": int_exps}
