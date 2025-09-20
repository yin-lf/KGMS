from flask import Blueprint, request
from marshmallow import Schema, fields, ValidationError
from ..core import create_response, graph_service


class AuthorSchema(Schema):
    name = fields.Str(
        required=True, error_messages={"required": "Author name is required"}
    )


authors_bp = Blueprint("authors", __name__, url_prefix="/api/kg/authors")
author_schema = AuthorSchema()


@authors_bp.route("", methods=["POST"])
def add_author():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = author_schema.load(json_data)
        name = result["name"]

        existing_author = graph_service.find_author_info(name)
        if existing_author:
            return create_response(False, error=f"Author '{name}' already exists"), 409

        graph_service.add_author(name)

        return (
            create_response(
                True,
                message="Author added successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@authors_bp.route("/<string:name>", methods=["GET"])
def get_author(name: str):
    try:
        author = graph_service.find_author_info(name)
        if not author:
            return create_response(False, error=f"Author '{name}' not found"), 404

        author_data = {
            "name": author.name,
            "papers": [{"id": paper[0], "title": paper[1]} for paper in author.papers],
        }

        return create_response(
            True,
            data=author_data,
            message=f"Author '{name}' information retrieved successfully",
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500


@authors_bp.route("", methods=["GET"])
def list_authors():
    try:
        authors = graph_service.get_all_authors()
        all_authors = [
            {"name": author.name, "publications": author.papers} for author in authors
        ]
        return create_response(
            True, data=all_authors, message="Get authors list successfully"
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500


@authors_bp.route("/<string:name>", methods=["DELETE"])
def delete_author(name: str):
    try:
        existing_author = graph_service.find_author_info(name)
        if not existing_author:
            return create_response(False, error=f"Author '{name}' not found"), 404

        graph_service.delete_author(name)

        return create_response(True, message=f"Author '{name}' deleted successfully")

    except Exception as e:
        return create_response(False, error=str(e)), 500
