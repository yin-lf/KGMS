from flask import request
from . import api_bp, create_response
from akb import GraphService
from marshmallow import Schema, fields, ValidationError


class PaperSchema(Schema):
    id = fields.Str(
        required=True, error_messages={"required": "paper id is required"}
    )
    title = fields.Str(
        required=True, error_messages={"required": "paper title is required"}
    )
    abstract = fields.Str(allow_none=True)
    authors = fields.List(fields.Str(), allow_none=True)     # 新增多作者
    categories = fields.List(fields.Str(), allow_none=True)  # 新增多分类


class PaperUpdateSchema(Schema):
    title = fields.Str(allow_none=True)
    abstract = fields.Str(allow_none=True)
    authors = fields.List(fields.Str(), allow_none=True)     # 更新时可改
    categories = fields.List(fields.Str(), allow_none=True)  # 更新时可改


graph_service = GraphService()
paper_schema = PaperSchema()
paper_update_schema = PaperUpdateSchema()


@api_bp.route("/papers", methods=["POST"])
def add_paper():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = paper_schema.load(json_data)
        pid = result["id"]
        title = result["title"]
        abstract = result.get("abstract")
        authors = result.get("authors", [])
        categories = result.get("categories", [])

        existing_paper = graph_service.find_paper_by_id(pid)
        if existing_paper:
            return (
                create_response(False, error=f"paper '{pid}' already exists"),
                409,
            )

        graph_service.add_paper(pid, title, abstract, authors, categories)

        return (
            create_response(
                True,
                data={
                    "id": pid,
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "categories": categories,
                },
                message=f"Paper '{pid}' added successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@api_bp.route("/papers/<string:id>", methods=["PUT"])
def update_paper(id: str):
    try:
        existing_paper = graph_service.find_paper_by_id(id)
        if not existing_paper:
            return create_response(False, error=f"paper '{id}' not found"), 404

        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = paper_update_schema.load(json_data)
        if not any(field in result for field in ("title", "abstract", "authors", "categories")):
            return (
                create_response(
                    False,
                    error="At least one field (title, abstract, authors, categories) must be provided for update",
                ),
                400,
            )

        graph_service.update_paper(
            id,
            maybe_new_title=result.get("title"),
            maybe_new_abstract=result.get("abstract"),
            maybe_new_authors=result.get("authors"),
            maybe_new_categories=result.get("categories"),
        )

        updated_paper = graph_service.find_paper_by_id(id)
        paper_data = {
            "id": updated_paper.pid,
            "title": updated_paper.title,
            "abstract": updated_paper.abstract,
            "authors": updated_paper.authors,
            "categories": updated_paper.categories,
        }

        return create_response(
            True, data=paper_data, message=f"Paper '{id}' updated successfully"
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500
