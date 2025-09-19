from flask import request
from marshmallow import Schema, fields, ValidationError
from . import api_bp, create_response
from akb import GraphService


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


graph_service = GraphService()
json_data_schema = JsonDataSchema()


@api_bp.route("/data/info", methods=["GET"])
def get_graph_overview_info():
    try:
        overview_info = graph_service.get_overview_info()
        overview_data = {
            "total_authors": overview_info.total_authors,
            "total_papers": overview_info.total_papers,
            "total_categories": overview_info.total_categories,
            "num_papers_per_category": overview_info.num_papers_per_category,
        }

        return create_response(
            True, data=overview_data, message="Get graph overview successfully"
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/data/load", methods=["POST"])
def load_data_from_json():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = json_data_schema.load(json_data)
        id = result["id"]
        title = result["title"]
        abstract = result.get("abstract")
        authors = [a.strip() for a in result["authors"].split(",") if a.strip()]
        categories = [c.strip() for c in result["categories"].split(",") if c.strip()]

        existing_paper = graph_service.find_paper_by_id(id)
        if existing_paper:
            return (
                create_response(False, error=f"paper '{id}' already exists"),
                409,
            )

        graph_service.load_data_from_json(result)

        return (
            create_response(
                True,
                data={
                    "id": id,
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "categories": categories,
                },
                message=f"Data for paper '{id}' loaded successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/data/clear", methods=["DELETE"])
def clear_all_data():
    try:
        graph_service.clear_all_data()
        return create_response(True, message="All data cleared successfully"), 200
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/data/check_index", methods=["GET"])
def check_fulltext_index():
    try:
        exists = graph_service.check_fulltext_index_exists()
        message = (
            "Full-text index exists" if exists else "Full-text index does not exist"
        )
        return create_response(True, data={"exists": exists}, message=message), 200
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/data/create_index", methods=["POST"])
def create_fulltext_index():
    try:
        graph_service.create_fulltext_index()
        return (
            create_response(True, message="Full-text index created successfully"),
            200,
        )
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/data/drop_index", methods=["POST"])
def drop_fulltext_index():
    try:
        graph_service.drop_fulltext_index()
        return (
            create_response(True, message="Full-text index dropped successfully"),
            200,
        )
    except Exception as e:
        return create_response(False, error=str(e)), 500
