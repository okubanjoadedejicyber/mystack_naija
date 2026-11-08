
def calculate_score(answers):
    categories = {
        "sales": [],
        "customer_service": [],
        "content_creation": [],
        "operations": [],
        "finance": []
    }

    # How the business currently uses digital and AI tools
    tool_use_scores = {
        "not_using": 0,
        "basic_digital": 35,
        "some_ai": 70,
        "regular_ai": 100
    }
    tool_use = tool_use_scores[answers["tool_use"]]

    # How much work is repetitive or manual
    manual_work_scores = {
        "most_tasks": 10,
        "many_tasks": 30,
        "some_tasks": 65,
        "few_tasks": 90
    }
    manual_work = manual_work_scores[answers["manual_work"]]

    for category in categories:
        categories[category].extend([tool_use, manual_work])

    # Customer communication
    message_scores = {
        "personal_only": 20,
        "quick_replies": 55,
        "organised_inbox": 75,
        "automated_support": 100
    }
    message_score = message_scores[answers["customer_messages"]]
    categories["customer_service"].append(message_score)
    categories["sales"].append(message_score)

    # Content creation
    content_scores = {
        "rarely": 15,
        "when_time": 35,
        "weekly": 65,
        "planned": 90
    }
    categories["content_creation"].append(
        content_scores[answers["content_frequency"]]
    )

    # Business record keeping
    record_scores = {
        "paper_memory": 10,
        "phone_notes": 30,
        "spreadsheets": 65,
        "business_software": 95
    }
    record_score = record_scores[answers["record_keeping"]]
    categories["operations"].append(record_score)
    categories["finance"].append(record_score)

    # Sales and financial tracking
    money_scores = {
        "not_tracked": 5,
        "roughly": 25,
        "spreadsheet": 65,
        "software": 95
    }
    money_score = money_scores[answers["money_tracking"]]
    categories["finance"].append(money_score)
    categories["sales"].append(money_score)

    category_scores = {
        name: round(sum(scores) / len(scores), 2)
        for name, scores in categories.items()
    }

    overall_score = round(
        sum(category_scores.values()) / len(category_scores), 2
    )

    priority_gaps = sorted(
        category_scores,
        key=category_scores.get
    )[:2]

    if overall_score < 30:
        score_label = "Getting started"
    elif overall_score < 55:
        score_label = "Early adopter"
    elif overall_score < 75:
        score_label = "Growing adoption"
    else:
        score_label = "Advanced adoption"

    return {
        "category_scores": category_scores,
        "overall_score": overall_score,
        "priority_gaps": priority_gaps,
        "score_label": score_label
    }
