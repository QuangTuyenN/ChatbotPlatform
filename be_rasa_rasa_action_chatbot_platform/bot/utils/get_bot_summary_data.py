def _get_summary_data(bot):
    counts = {
        "chitchats": bot.chitchat_set.count(),
        "chitchat_intent_examples": bot.chitchatintentexample_set.count(),
        "chitchat_utter_examples": bot.chitchatutterexample_set.count(),
        "intents": bot.intent_set.count(),
        "intent_examples": bot.intentexample_set.count(),
        "entities": bot.entity_set.count(),
        "stories": bot.story_set.count()
    }

    return counts
