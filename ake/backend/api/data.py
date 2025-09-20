from flask import Blueprint, request
from marshmallow import Schema, fields, ValidationError
from ..core import create_response, graph_service

data_bp = Blueprint("data", __name__, url_prefix="/api/kg/data")


class JsonDataSchema(Schema):
    class Meta:
        unknown = "INCLUDE"  # 允许包含未定义的字段

    id = fields.Str(required=True, error_messages={"required": "ID is required"})
    title = fields.Str(required=True, error_messages={"required": "Title is required"})
    abstract = fields.Str(allow_none=True)
    authors = fields.Str(
        required=True, error_messages={"required": "Authors are required"}
    )
    categories = fields.Str(
        required=True, error_messages={"required": "Categories are required"}
    )


@data_bp.route("/info", methods=["GET"])
def get_overview_info():
    info = graph_service.get_overview_info()
    return create_response(data=info)


@data_bp.route("/load", methods=["POST"])
def load_data():
    json_data = request.get_json()
    try:
        graph_service.load_data_from_json(json_data)
        return create_response(message="Data loaded successfully"), 201
    except Exception as e:
        return create_response(False, error=str(e)), 409


@data_bp.route("/clear", methods=["DELETE"])
def clear_all_data():
    graph_service.clear_all_data()
    return create_response(message="All data cleared successfully")


@data_bp.route("/check_index", methods=["GET"])
def check_index():
    exists = graph_service.check_fulltext_index_exists()
    if exists:
        return create_response(True, data=True, message="Full-text index exists")
    else:
        return create_response(True, data=False, message="Full-text index does not exist")


@data_bp.route("/create_index", methods=["POST"])
def create_index():
    graph_service.create_fulltext_index()
    return create_response(True, message="Full-text index created successfully")


@data_bp.route("/drop_index", methods=["POST"])
def drop_index():
    graph_service.drop_fulltext_index()
    return create_response(True, message="Full-text index dropped successfully")

