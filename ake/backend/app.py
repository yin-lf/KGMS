from flask import Flask
from flask_cors import CORS
from core import create_response
from api.authors import authors_bp
from api.papers import papers_bp
from api.categories import categories_bp
from api.relationships import relationships_bp
from api.data import data_bp
from api.auth import auth_bp
from api.recommendations import recommendations_bp
from akb.services.graph_service import GraphService

# 创建graph_service实例
graph_service = GraphService()
# 在应用启动前创建索引
try:
    print("正在创建全文索引...")
    graph_service.create_fulltext_index()
    print(f"全文索引创建状态: {graph_service.fulltext_index_exists}")
except Exception as e:
    print(f"创建索引时出错: {e}")
    import traceback
    traceback.print_exc()

app = Flask(__name__)
app.secret_key = "your-very-secret-key"  # Add a secret key for session management
CORS(app)
app.register_blueprint(authors_bp)
app.register_blueprint(papers_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(relationships_bp)
app.register_blueprint(data_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(recommendations_bp)
PORT = 5000


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


@app.route("/")
def index():
    return create_response(message="Welcome to the ArXiv Knowledge Base API!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
