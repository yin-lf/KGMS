from flask import request
from marshmallow import Schema, fields, ValidationError
from . import api_bp, create_response
from akb import GraphService


class CategorySchema(Schema):
    name = fields.Str(
        required=True, error_messages={"required": "Category name is required"}
    )


class CategoryUpdateSchema(Schema):
    name = fields.Str(
        required=True, error_messages={"required": "New category name is required"}
    )


graph_service = GraphService()
category_schema = CategorySchema()
category_update_schema = CategoryUpdateSchema()


@api_bp.route("/categories", methods=["POST"])
def add_category():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = category_schema.load(json_data)
        name = result["name"]

        existing_category = graph_service.find_category(name)
        if existing_category:
            return (
                create_response(False, error=f"Category '{name}' is already exists"),
                409,
            )

        graph_service.add_category(name)

        return (
            create_response(
                True,
                message=f"Category '{name}' added successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/categories/<string:name>", methods=["GET"])
def get_category(name: str):
    try:
        category = graph_service.find_category(name)
        if not category:
            return create_response(False, error=f"Category '{name}' not found"), 404

        category_data = {
            "name": category.name,
            "papers": [
                {"id": paper[0], "title": paper[1]} for paper in category.papers
            ],
        }

        return create_response(
            True,
            data=category_data,
            message=f"Category '{name}' info retrieved successfully",
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/categories/<string:old_name>", methods=["PUT"])
def update_category(old_name: str):
    try:
        existing_category = graph_service.find_category(old_name)
        if not existing_category:
            return create_response(False, error=f"Category '{old_name}' not found"), 404

        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = category_update_schema.load(json_data)
        new_name = result["name"]

        if old_name != new_name:
            existing_new_category = graph_service.find_category(new_name)
            if existing_new_category:
                return (
                    create_response(
                        False, error=f"Category '{new_name}' already exists"
                    ),
                    409,
                )

        graph_service.update_category(old_name, new_name)

        updated_category = graph_service.find_category(new_name)
        category_data = {
            "name": updated_category.name,
            "papers": [
                {"pid": paper[0], "title": paper[1]}
                for paper in updated_category.papers
            ],
        }

        return create_response(
            True, data=category_data, message="Category updated successfully"
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/categories/<string:name>", methods=["DELETE"])
def delete_category(name: str):
    try:
        existing_category = graph_service.find_category(name)
        if not existing_category:
            return create_response(False, error=f"Category '{name}' not found"), 404

        graph_service.delete_category(name)

        return create_response(True, message=f"Category '{name}' deleted successfully")

    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/categories", methods=["GET"])
def list_categories():
    """获取所有分类列表"""
    try:
        categories = graph_service.get_all_categories()
        all_categories = [
            {
                "name": category.name,
                "papers": [
                    {"id": paper[0], "title": paper[1]} for paper in category.papers
                ],
            }
            for category in categories
        ]
        return create_response(
            True, data=all_categories, message="Get categories list successfully"
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500
