
CATEGORY_NAMES = {
    "sales": "Sales",
    "customer_service": "Customer Service",
    "content_creation": "Content Creation",
    "operations": "Operations",
    "finance": "Finance"
}

KEYWORDS = {
    "sales": ["sales", "order", "customer", "revenue", "marketing"],
    "customer_service": ["customer", "message", "reply", "support", "whatsapp"],
    "content_creation": ["content", "design", "video", "social", "promotion"],
    "operations": ["manual", "record", "inventory", "organisation", "paperwork"],
    "finance": ["finance", "money", "expense", "budget", "payment", "accounting"]
}


def as_list(value):
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def recommend_tools(business, assessment, limit=3):
    from app import AITool

    tools = AITool.query.all()
    answers = assessment.answers or {}
    scores = assessment.category_scores or {}
    gaps = assessment.priority_gaps or []

    pain_points = " ".join(
        str(item).lower()
        for item in as_list(answers.get("pain_points"))
    )

    business_type = (business.business_type or "").lower()
    channels = [
        str(item).lower()
        for item in as_list(business.channels)
    ]
    budget = (business.monthly_budget or "").lower()

    ranked = []

    for tool in tools:
        category = (tool.category or "").lower().replace(" ", "_")

        if category not in CATEGORY_NAMES:
            # Try to identify a category from the tool's description and tags.
            description = " ".join([
                tool.name or "",
                tool.description or "",
                " ".join(map(str, as_list(tool.tags)))
            ]).lower()

            matches = [
                name for name, keywords in KEYWORDS.items()
                if any(word in description for word in keywords)
            ]
            category = matches[0] if matches else "operations"

        score = (100 - float(scores.get(category, 50))) * 0.60
        reasons = []

        if category in gaps:
            score += 15
            reasons.append(
                f"It addresses your {CATEGORY_NAMES[category]} priority gap."
            )

        tool_text = " ".join([
            tool.name or "",
            tool.description or "",
            " ".join(map(str, as_list(tool.tags)))
        ]).lower()

        if any(word in pain_points for word in KEYWORDS[category]):
            score += 15
            reasons.append("It can help with a challenge you selected.")

        if any(
            word in tool_text
            for word in pain_points.split()
            if len(word) > 3
        ):
            score += 10
            reasons.append("Its features relate to your selected challenges.")

        tool_channels = [
            str(item).lower()
            for item in as_list(tool.channels)
        ]

        if tool_channels and set(channels).intersection(tool_channels):
            score += 10
            reasons.append("It supports one of your customer channels.")

        tool_business_types = [
            str(item).lower()
            for item in as_list(tool.business_types)
        ]

        if tool_business_types and any(
            business_type in item or item in business_type
            for item in tool_business_types
        ):
            score += 5
            reasons.append("It is listed as suitable for your business type.")

        # A simple affordability hint. It does not assume a tool is free.
        pricing = (tool.pricing_info or "").lower()
        if any(word in pricing for word in ["free", "free plan", "free tier"]):
            if any(word in budget for word in ["low", "free", "0", "₦0"]):
                score += 5
                reasons.append("It advertises a free starting option.")

        if not reasons:
            reasons.append(
                f"It may help improve your {CATEGORY_NAMES[category]} activities."
            )

        ranked.append({
            "tool": tool,
            "fit_score": round(score, 2),
            "why_fit": " ".join(reasons),
            "fit_note": tool.pricing_info or
                "Check the official website for current pricing."
        })

    ranked.sort(key=lambda item: item["fit_score"], reverse=True)

    # Prefer different categories when possible.
    selected = []
    used_categories = set()

    for item in ranked:
        category = (item["tool"].category or "").lower().replace(" ", "_")
        if category not in used_categories:
            selected.append(item)
            used_categories.add(category)
        if len(selected) == limit:
            break

    for item in ranked:
        if len(selected) == limit:
            break
        if item not in selected:
            selected.append(item)

    return selected
