
import os
from datetime import datetime, timezone

from flask import (
    Flask, render_template, request, jsonify,
    url_for, redirect
)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import text

from scoring import calculate_score

load_dotenv()

db = SQLAlchemy()


class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(150), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)
    monthly_budget = db.Column(db.String(50))
    channels = db.Column(db.JSON)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(
        db.Integer, db.ForeignKey("business.id"), nullable=False
    )
    answers = db.Column(db.JSON, nullable=False)
    category_scores = db.Column(db.JSON)
    overall_score = db.Column(db.Float)
    priority_gaps = db.Column(db.JSON)
    score_label = db.Column(db.String(50))
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


class AITool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    pricing_info = db.Column(db.String(150))
    budget_level = db.Column(db.String(50))
    business_types = db.Column(db.JSON)
    channels = db.Column(db.JSON)
    tags = db.Column(db.JSON)


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessment.id"), nullable=False
    )
    tool_id = db.Column(
        db.Integer, db.ForeignKey("ai_tool.id"), nullable=False
    )
    rank = db.Column(db.Integer, nullable=False)
    fit_score = db.Column(db.Float)
    why_fit = db.Column(db.Text)
    fit_note = db.Column(db.Text)


def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "connect_args": {
        "connect_timeout": 10,
        "sslmode": "require"
    }
}
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from your environment.")
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY is missing from your environment.")

    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/assessment")
    def assessment_page():
        return render_template("assessment.html")

    @app.route("/api/assess", methods=["POST"])
    def submit_assessment():
        data = request.get_json(silent=True) or {}

        business_name = str(data.get("business_name", "")).strip()
        business_type = str(data.get("business_type", "")).strip()
        monthly_budget = str(data.get("monthly_budget", "")).strip()
        channels = data.get("channels", [])
        answers = data.get("answers", {})

        if not business_name or not business_type:
            return jsonify({"error": "Enter your business name and type."}), 400

        if not isinstance(channels, list) or not channels:
            return jsonify({"error": "Select at least one customer channel."}), 400

        if not isinstance(answers, dict):
            return jsonify({"error": "Your assessment answers are invalid."}), 400

        required = [
            "tool_use", "manual_work", "customer_messages",
            "content_frequency", "record_keeping", "money_tracking"
        ]

        allowed = {
            "tool_use": ["not_using", "basic_digital", "some_ai", "regular_ai"],
            "manual_work": ["most_tasks", "many_tasks", "some_tasks", "few_tasks"],
            "customer_messages": ["personal_only", "quick_replies", "organised_inbox", "automated_support"],
            "content_frequency": ["rarely", "when_time", "weekly", "planned"],
            "record_keeping": ["paper_memory", "phone_notes", "spreadsheets", "business_software"],
            "money_tracking": ["not_tracked", "roughly", "spreadsheet", "software"]
        }

        for key in required:
            if answers.get(key) not in allowed[key]:
                return jsonify({"error": "Please complete all assessment questions."}), 400

        pain_points = answers.get("pain_points", [])
        if not isinstance(pain_points, list) or len(pain_points) > 3:
            return jsonify({"error": "Choose up to three challenges."}), 400

        business = Business(
            business_name=business_name,
            business_type=business_type,
            monthly_budget=monthly_budget,
            channels=channels
        )

        db.session.add(business)
        db.session.flush()

        result = calculate_score(answers)

        assessment = Assessment(
            business_id=business.id,
            answers=answers,
            category_scores=result["category_scores"],
            overall_score=result["overall_score"],
            priority_gaps=result["priority_gaps"],
            score_label=result["score_label"]
        )

        db.session.add(assessment)
        db.session.flush()

        from recommender import recommend_tools
        suggestions = recommend_tools(business, assessment, limit=3)

        for position, suggestion in enumerate(suggestions, start=1):
            db.session.add(Recommendation(
                assessment_id=assessment.id,
                tool_id=suggestion["tool"].id,
                rank=position,
                fit_score=suggestion["fit_score"],
                why_fit=suggestion["why_fit"],
                fit_note=suggestion["fit_note"]
            ))

        db.session.commit()

        return jsonify({
            "success": True,
            "redirect": url_for("results_page", assessment_id=assessment.id)
        })

    @app.route("/results/<int:assessment_id>")
    def results_page(assessment_id):
        assessment = db.session.get(Assessment, assessment_id)

        if assessment is None:
            return "Assessment not found.", 404

        business = db.session.get(Business, assessment.business_id)

        rows = (
            Recommendation.query
            .filter_by(assessment_id=assessment.id)
            .order_by(Recommendation.rank)
            .all()
        )

        recommendations = []
        for row in rows:
            tool = db.session.get(AITool, row.tool_id)
            if tool:
                recommendations.append({
                    "rank": row.rank,
                    "tool": tool,
                    "fit_score": row.fit_score,
                    "why_fit": row.why_fit,
                    "fit_note": row.fit_note
                })

        category_names = {
            "sales": "Sales",
            "customer_service": "Customer Service",
            "content_creation": "Content Creation",
            "operations": "Operations",
            "finance": "Finance"
        }

        priority_names = [
            category_names.get(item, item.replace("_", " ").title())
            for item in (assessment.priority_gaps or [])
        ]

        action_plan = [
            "Choose one recommended tool and visit its official website.",
            "Create an account and complete the basic setup.",
            "Use the tool for one real business task.",
            "Show anyone who helps run your business how to use it.",
            "Review the time saved and results after seven days."
        ]

        return render_template(
            "results.html",
            business=business,
            assessment=assessment,
            recommendations=recommendations,
            category_names=category_names,
            priority_names=priority_names,
            action_plan=action_plan
        )

    @app.route("/api/catalog")
    def catalog():
        tools = AITool.query.order_by(AITool.name).all()
        return jsonify([
            {
                "id": tool.id,
                "name": tool.name,
                "category": tool.category,
                "description": tool.description,
                "website": tool.website,
                "pricing": tool.pricing_info
            }
            for tool in tools
        ])

    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"})
        except Exception:
            app.logger.exception("Database health check failed")
            return jsonify({"status": "error", "database": "unavailable"}), 503

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
