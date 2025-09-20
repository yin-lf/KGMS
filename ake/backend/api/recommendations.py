from flask import Blueprint, request, session
from ..akb.services.recommendation_service import RecommendationService
from ..core import create_response
from .utils import login_required

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api")


@recommendations_bp.route("/recommendations", methods=["GET"])
@login_required
def get_recommendations():
    username = session["username"]
    recommendation_service = RecommendationService()
    papers = recommendation_service.get_recommendations(username)
    return create_response(data=[paper.to_dict() for paper in papers])


@recommendations_bp.route("/feedback", methods=["POST"])
@login_required
def feedback():
    username = session["username"]
    data = request.get_json()
    paper_id = data.get("paper_id")
    liked = data.get("liked")

    if not paper_id or liked is None:
        return create_response(False, message="Missing paper_id or liked status"), 400

    recommendation_service = RecommendationService()
    recommendation_service.record_feedback(username, paper_id, liked)
    return create_response(message="Feedback recorded")


@recommendations_bp.route("/liked", methods=["GET"])
@login_required
def get_liked_papers():
    username = session["username"]
    recommendation_service = RecommendationService()
    papers = recommendation_service.get_liked_papers(username)
    return create_response(data=[paper.to_dict() for paper in papers])
