def _get_chitchat_data(chit):
    int_exps = [exp.text for exp in chit.chitchatintentexample_set.all() if str(exp.chitchat) == str(chit.name)]
    utt_exps = [exp.text for exp in chit.chitchatutterexample_set.all() if str(exp.chitchat) == str(chit.name)]
    return {"id": chit.id, "name": chit.name, "int_exps": int_exps, "utt_exps": utt_exps}
