from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models import Decision, Option, Criterion, Score

decisions_bp = Blueprint('decisions', __name__, url_prefix='/api/decisions')

# 1. Create a new Decision
@decisions_bp.route('', methods=['POST'])
@jwt_required()
def create_decision():
    current_user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get('title')
    description = data.get('description', '')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_decision = Decision(title=title, description=description, user_id=current_user_id)
    db.session.add(new_decision)
    db.session.commit()

    return jsonify({"message": "Decision created successfully", "id": new_decision.id}), 201


# 2. Get all Decisions for the current user
@decisions_bp.route('', methods=['GET'])
@jwt_required()
def get_decisions():
    current_user_id = int(get_jwt_identity())
    decisions = Decision.query.filter_by(user_id=current_user_id).all()

    result = [{
        "id": d.id,
        "title": d.title,
        "description": d.description,
        "created_at": d.created_at.isoformat()
    } for d in decisions]

    return jsonify(result), 200


# 3. Add Options & Criteria to a Decision
@decisions_bp.route('/<int:decision_id>/setup', methods=['POST'])
@jwt_required()
def setup_decision_matrix(decision_id):
    current_user_id = int(get_jwt_identity())
    decision = Decision.query.filter_by(id=decision_id, user_id=current_user_id).first_or_404()

    data = request.get_json() or {}
    options_data = data.get('options', [])      # List of strings e.g., ["Option A", "Option B"]
    criteria_data = data.get('criteria', [])    # List of dicts e.g., [{"name": "Cost", "weight": 8.0}]

    # Save Options
    for opt_name in options_data:
        db.session.add(Option(name=opt_name, decision_id=decision.id))

    # Save Criteria
    for crit in criteria_data:
        db.session.add(Criterion(
            name=crit.get('name'),
            weight=crit.get('weight', 1.0),
            decision_id=decision.id
        ))

    db.session.commit()
    return jsonify({"message": "Options and criteria saved successfully!"}), 200


# 4. Compute Decision Matrix Results (Weighted Evaluation)
@decisions_bp.route('/<int:decision_id>/evaluate', methods=['GET'])
@jwt_required()
def evaluate_decision(decision_id):
    current_user_id = int(get_jwt_identity())
    decision = Decision.query.filter_by(id=decision_id, user_id=current_user_id).first_or_404()

    options = Option.query.filter_by(decision_id=decision.id).all()
    criteria = Criterion.query.filter_by(decision_id=decision.id).all()

    rankings = []

    for option in options:
        total_weighted_score = 0.0
        total_weight = 0.0

        for criterion in criteria:
            score_entry = Score.query.filter_by(option_id=option.id, criterion_id=criterion.id).first()
            val = score_entry.value if score_entry else 0.0

            total_weighted_score += (val * criterion.weight)
            total_weight += criterion.weight

        final_score = round(total_weighted_score / total_weight, 2) if total_weight > 0 else 0.0
        
        rankings.append({
            "option_id": option.id,
            "option_name": option.name,
            "weighted_score": final_score
        })

    # Sort options by highest score first
    rankings.sort(key=lambda x: x['weighted_score'], reverse=True)

    return jsonify({
        "decision_id": decision.id,
        "title": decision.title,
        "rankings": rankings
    }), 200