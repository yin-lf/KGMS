from flask import jsonify
from typing import Any
from akb import GraphService

graph_service = GraphService()


def create_response(
    success: bool = True, data: Any = None, message: str = "", error: str = ""
):
    return jsonify(
        {"success": success, "data": data, "message": message, "error": error}
    )
