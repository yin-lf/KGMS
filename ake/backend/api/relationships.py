from flask import Blueprint, request
from marshmallow import Schema, fields, ValidationError
from core import create_response, graph_service


class AuthorPaperLinkSchema(Schema):
    name = fields.Str(
        required=True, error_messages={"required": "Author name is required"}
    )
    id = fields.Str(
        required=True, error_messages={"required": "Paper ID is required"}
    )


class PaperCategoryLinkSchema(Schema):
    id = fields.Str(
        required=True, error_messages={"required": "Paper ID is required"}
    )
    name = fields.Str(
        required=True, error_messages={"required": "Category is required"}
    )


relationships_bp = Blueprint(
    "relationships", __name__, url_prefix="/api/kg/relationships"
)
author_paper_link_schema = AuthorPaperLinkSchema()
paper_category_link_schema = PaperCategoryLinkSchema()


@relationships_bp.route("/author-paper", methods=["POST"])
def link_author_to_paper():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = author_paper_link_schema.load(json_data)
        name = result["name"]
        id = result["id"]

        author = graph_service.find_author_info(name)
        if not author:
            return (
                create_response(False, error=f"Author '{name}' not found"),
                404,
            )

        paper = graph_service.find_paper_by_id(id)
        if not paper:
            return create_response(False, error=f"Paper ID '{id}' not found"), 404

        graph_service.link_author_to_paper(name, id)

        return (
            create_response(
                True,
                data={"author": name, "id": id},
                message="Author-Paper relationship created successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@relationships_bp.route("/author-paper", methods=["DELETE"])
def unlink_author_from_paper():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = author_paper_link_schema.load(json_data)
        name = result["name"]
        id = result["id"]

        author = graph_service.find_author_info(name)
        if not author:
            return (
                create_response(False, error=f"Author '{name}' not found"),
                404,
            )

        paper = graph_service.find_paper_by_id(id)
        if not paper:
            return create_response(False, error=f"Paper ID '{id}' not found"), 404

        graph_service.unlink_author_from_paper(name, id)

        return create_response(
            True,
            data={"author": name, "id": id},
            message="Author-Paper relationship deleted successfully",
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@relationships_bp.route("/paper-category", methods=["POST"])
def link_paper_to_category():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = paper_category_link_schema.load(json_data)
        id = result["id"]
        name = result["name"]

        paper = graph_service.find_paper_by_id(id)
        if not paper:
            return create_response(False, error=f"Paper '{id}' not found"), 404

        category = graph_service.find_category(name)
        if not category:
            return (
                create_response(False, error=f"Category '{name}' not found"),
                404,
            )

        graph_service.link_paper_to_category(id, name)

        return (
            create_response(
                True,
                data={"id": id, "name": name},
                message="Paper-Category relationship created successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@relationships_bp.route("/paper-category", methods=["DELETE"])
def unlink_paper_from_category():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = paper_category_link_schema.load(json_data)
        id = result["id"]
        name = result["name"]

        paper = graph_service.find_paper_by_id(id)
        if not paper:
            return create_response(False, error=f"Paper '{id}' not found"), 404

        category = graph_service.find_category(name)
        if not category:
            return (
                create_response(False, error=f"Category '{name}' not found"),
                404,
            )

        graph_service.unlink_paper_from_category(id, name)

        return create_response(
            True,
            data={"id": id, "name": name},
            message="Paper-Category relationship deleted successfully",
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500
