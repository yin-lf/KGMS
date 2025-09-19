from flask import Flask, jsonify
from flask_cors import CORS
from typing import Any
from akb import GraphService
from api import api_bp


app = Flask(__name__)
CORS(app)
app.register_blueprint(api_bp)
graph_service = GraphService()
PORT = 5000


def create_response(
    success: bool = True, data: Any = None, message: str = "", error: str = ""
):
    return jsonify(
        {"success": success, "data": data, "message": message, "error": error}
    )


@app.errorhandler(404)
def not_found(error):
    return (
        create_response(
            False, error="Resources not found", message="Please check your request path"
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed(error):
    return (
        create_response(
            False, error="Method is not allowed", message="Please check HTTP method"
        ),
        405,
    )


@app.errorhandler(500)
def internal_error(error):
    return (
        create_response(
            False, error="Internal server error", message="Please try again later"
        ),
        500,
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        return create_response(data={"status": "healthy"}, message="Check passed")
    except Exception as e:
        return create_response(False, error=str(e), message="Health check failed"), 500


if __name__ == "__main__":
    print("Starting Knowledge Graph API Server...")
    print(f"Health check: http://localhost:{PORT}/health")
    print(f"API Base URL: http://localhost:{PORT}/api/v1")
    app.run(debug=True, host="0.0.0.0", port=PORT)
