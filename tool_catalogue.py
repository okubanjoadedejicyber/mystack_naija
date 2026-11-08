
from app import app, db, AITool, Recommendation

# MyStack Naija: 20 selected AI tools
TOOLS = [
    # Sales
    {
        "name": "ChatGPT",
        "category": "sales",
        "description": "Helps businesses write sales messages, respond to enquiries and generate business ideas.",
        "website": "https://chatgpt.com",
        "tags": ["sales", "writing", "research", "marketing"]
    },
    {
        "name": "Perplexity AI",
        "category": "sales",
        "description": "Helps businesses research markets, competitors and potential customers.",
        "website": "https://www.perplexity.ai",
        "tags": ["sales", "research", "market_analysis"]
    },

    # Operations
    {
        "name": "Google Gemini",
        "category": "operations",
        "description": "Provides AI assistance for research, planning and everyday business tasks.",
        "website": "https://gemini.google.com",
        "tags": ["operations", "research", "productivity"]
    },
    {
        "name": "Microsoft Copilot",
        "category": "operations",
        "description": "Assists with workplace productivity, documents and business tasks.",
        "website": "https://copilot.microsoft.com",
        "tags": ["operations", "productivity", "documents"]
    },
    {
        "name": "Zapier",
        "category": "operations",
        "description": "Connects applications and automates repetitive business tasks.",
        "website": "https://zapier.com",
        "tags": ["operations", "automation", "workflows"]
    },
    {
        "name": "Make",
        "category": "operations",
        "description": "Automates business workflows by connecting different applications.",
        "website": "https://www.make.com",
        "tags": ["operations", "automation", "integration"]
    },
    {
        "name": "n8n",
        "category": "operations",
        "description": "Provides workflow automation connecting applications and AI tools.",
        "website": "https://n8n.io",
        "tags": ["operations", "automation", "workflows"]
    },
    {
        "name": "Notion AI",
        "category": "operations",
        "description": "Helps organise business notes, documents, tasks and team information.",
        "website": "https://www.notion.com",
        "tags": ["operations", "planning", "productivity"]
    },
    {
        "name": "Airtable",
        "category": "operations",
        "description": "Organises business records, projects and workflows using a flexible database.",
        "website": "https://www.airtable.com",
        "tags": ["operations", "records", "database"]
    },

    # Customer service
    {
        "name": "Manychat",
        "category": "customer_service",
        "description": "Automates customer conversations on supported messaging and social platforms.",
        "website": "https://manychat.com",
        "tags": ["customer_service", "chatbot", "whatsapp", "instagram"]
    },
    {
        "name": "Tidio",
        "category": "customer_service",
        "description": "Provides live chat and AI-assisted customer support.",
        "website": "https://www.tidio.com",
        "tags": ["customer_service", "live_chat", "sales"]
    },
    {
        "name": "Chatbase",
        "category": "customer_service",
        "description": "Creates AI chatbots that answer questions using business information.",
        "website": "https://www.chatbase.co",
        "tags": ["customer_service", "chatbot", "automation"]
    },
    {
        "name": "Intercom",
        "category": "customer_service",
        "description": "Helps businesses manage customer messages and support conversations.",
        "website": "https://www.intercom.com",
        "tags": ["customer_service", "live_chat", "sales"]
    },

    # Content creation
    {
        "name": "Grammarly",
        "category": "content_creation",
        "description": "Improves business writing, grammar and communication.",
        "website": "https://www.grammarly.com",
        "tags": ["content_creation", "writing", "editing"]
    },
    {
        "name": "Canva Magic Studio",
        "category": "content_creation",
        "description": "Creates graphics, presentations and promotional materials using AI features.",
        "website": "https://www.canva.com",
        "tags": ["content_creation", "design", "social_media"]
    },
    {
        "name": "Adobe Firefly",
        "category": "content_creation",
        "description": "Generates images and assists with creative design.",
        "website": "https://firefly.adobe.com",
        "tags": ["content_creation", "images", "design"]
    },
    {
        "name": "InVideo AI",
        "category": "content_creation",
        "description": "Helps create promotional and social media videos.",
        "website": "https://invideo.io",
        "tags": ["content_creation", "video", "advertising"]
    },
    {
        "name": "ElevenLabs",
        "category": "content_creation",
        "description": "Creates AI-generated voices and voiceovers.",
        "website": "https://elevenlabs.io",
        "tags": ["content_creation", "audio", "voice"]
    },

    # Finance
    {
        "name": "Microsoft Power BI",
        "category": "finance",
        "description": "Helps analyse business data and create financial and sales reports.",
        "website": "https://www.microsoft.com/power-platform/products/power-bi",
        "tags": ["finance", "analytics", "reports", "sales"]
    },
    {
        "name": "Julius AI",
        "category": "finance",
        "description": "Analyses spreadsheets and business data to generate insights and charts.",
        "website": "https://julius.ai",
        "tags": ["finance", "data_analysis", "spreadsheets"]
    },
    
    {
        "name": "Google Sheets",
        "category": "finance",
        "description": "Organises sales, expenses, inventory and business records using spreadsheets.",
        "website": "https://sheets.google.com",
        "tags": ["spreadsheet", "records", "finance", "sales", "operations"]
    },
    {
        "name": "Microsoft Excel",
        "category": "finance",
        "description": "Supports calculations, budgeting, financial records and business reporting.",
        "website": "https://www.microsoft.com/microsoft-365/excel",
        "tags": ["spreadsheet", "finance", "budgeting", "records"]
    },
    {
        "name": "WhatsApp Business",
        "category": "customer_service",
        "description": "Helps businesses manage customer conversations, product catalogues and enquiries.",
        "website": "https://business.whatsapp.com/",
        "tags": ["whatsapp", "customer_service", "sales", "messaging"]
    },
    {
        "name": "Google Forms",
        "category": "operations",
        "description": "Collects customer feedback, orders, registrations and business enquiries.",
        "website": "https://forms.google.com",
        "tags": ["forms", "data_collection", "customers", "operations"]
    },
    {
        "name": "Google Drive",
        "category": "operations",
        "description": "Stores, organises and shares business documents and digital records.",
        "website": "https://drive.google.com",
        "tags": ["storage", "documents", "records", "operations"]
    }

]


with app.app_context():

    # Remove old catalogue entries that are no longer in the
    # selected list. Preserve entries already used in recommendations.
    selected_names = [tool["name"] for tool in TOOLS]

    old_tools = AITool.query.filter(
        ~AITool.name.in_(selected_names)
    ).all()

    for old_tool in old_tools:
        existing_recommendation = Recommendation.query.filter_by(
            tool_id=old_tool.id
        ).first()

        if existing_recommendation:
            raise RuntimeError(
                f"Cannot remove {old_tool.name}: it is already used "
                "in a recommendation."
            )

        db.session.delete(old_tool)

    # Insert new tools or update existing ones.
    for item in TOOLS:

        tool = AITool.query.filter_by(
            name=item["name"]
        ).first()

        if tool:
            tool.category = item["category"]
            tool.description = item["description"]
            tool.website = item["website"]
            tool.pricing_info = "Check official website"
            tool.budget_level = "varies"
            tool.business_types = []
            tool.channels = []
            tool.tags = item["tags"]

        else:
            new_tool = AITool(
                name=item["name"],
                category=item["category"],
                description=item["description"],
                website=item["website"],
                pricing_info="Check official website",
                budget_level="varies",
                business_types=[],
                channels=[],
                tags=item["tags"]
            )

            db.session.add(new_tool)

    db.session.commit()

    print("AI tool catalogue updated successfully!")
    print(f"Tools in catalogue: {AITool.query.count()}")

