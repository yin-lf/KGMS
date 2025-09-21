from flask import Blueprint, request
from core import create_response, graph_service
from marshmallow import Schema, fields, ValidationError


class PaperSchema(Schema):
    id = fields.Str(
        required=True, error_messages={"required": "paper id is required"}
    )
    title = fields.Str(
        required=True, error_messages={"required": "paper title is required"}
    )
    abstract = fields.Str(allow_none=True)


class PaperUpdateSchema(Schema):
    title = fields.Str(allow_none=True)
    abstract = fields.Str(allow_none=True)


papers_bp = Blueprint("papers", __name__, url_prefix="/api/kg/papers")
paper_schema = PaperSchema()
paper_update_schema = PaperUpdateSchema()


@papers_bp.route("", methods=["POST"])
def add_paper():
    try:
        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = paper_schema.load(json_data)
        id = result["id"]
        title = result["title"]
        abstract = result.get("abstract")

        existing_paper = graph_service.find_paper_by_id(id)
        if existing_paper:
            return (
                create_response(False, error=f"paper '{id}' already exists"),
                409,
            )

        graph_service.add_paper(id, title, abstract)

        return (
            create_response(
                True,
                data={
                    "id": id,
                    "title": title,
                    "abstract": abstract,
                },
                message=f"Paper '{id}' added successfully",
            ),
            201,
        )

    except ValidationError as err:
        return create_response(False, error=str(err.messages)), 400
    except Exception as e:
        return create_response(False, error=str(e)), 500


@papers_bp.route("/<string:id>", methods=["GET"])
def get_paper(id: str):
    try:
        paper = graph_service.find_paper_by_id(id)
        if not paper:
            return create_response(False, error=f"paper '{id}' not found"), 404

        paper_data = {
            "id": paper.pid,
            "title": paper.title,
            "abstract": paper.abstract,
            "authors": paper.authors,
            "categories": paper.categories,
        }

        return create_response(
            True,
            data=paper_data,
            message=f"Paper '{id}' info retrieved successfully",
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500


@papers_bp.route("/<string:id>", methods=["PUT"])
def update_paper(id: str):
    try:
        existing_paper = graph_service.find_paper_by_id(id)
        if not existing_paper:
            return create_response(False, error=f"paper '{id}' not found"), 404

        json_data = request.get_json()
        if not json_data:
            return create_response(False, error="Empty Request Data"), 400

        result = paper_update_schema.load(json_data)
        if "title" not in result and "abstract" not in result:
            return (
                create_response(
                    False,
                    error="At least one field (title or abstract) must be provided for update",
                ),
                400,
            )

        maybe_new_title = result.get("title")
        maybe_new_abstract = result.get("abstract")
        graph_service.update_paper(id, maybe_new_title, maybe_new_abstract)

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


@papers_bp.route("/<string:id>", methods=["DELETE"])
def delete_paper(id):
    try:
        existing_paper = graph_service.find_paper_by_id(id)
        if not existing_paper:
            return create_response(False, error=f"Paper '{id}' not found"), 404

        graph_service.delete_paper(id)

        return create_response(True, message=f"Paper '{id}' deleted successfully")

    except Exception as e:
        return create_response(False, error=str(e)), 500


@papers_bp.route("/search", methods=["GET"])
def search_papers():
    """搜索论文（支持分页）"""
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return create_response(False, error="Search query cannot be empty"), 400

        # 获取分页参数，设置默认值
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 20, type=int)
        
        # 验证分页参数
        if page < 1:
            return create_response(False, error="Page must be at least 1"), 400
        if page_size < 1 or page_size > 100:
            return create_response(False, error="Page size must be between 1 and 100"), 400

        # 调用支持分页的搜索方法
        papers = graph_service.search_papers(query, page, page_size)

        papers_data = [
            {
                "id": paper.pid,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "categories": paper.categories,
            }
            for paper in papers
        ]

        return create_response(
            True, 
            data={
                "papers": papers_data,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": len(papers_data)
                }
            }, 
            message=f"Found {len(papers_data)} related papers"
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500


@papers_bp.route("", methods=["GET"])
def list_papers():
    """获取所有论文列表"""
    try:
        papers = graph_service.get_all_papers()
        all_papers = [
            {
                "id": paper.pid,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "categories": paper.categories,
            }
            for paper in papers
        ]
        return create_response(
            True, data=all_papers, message="Get papers list successfully"
        )

    except Exception as e:
        return create_response(False, error=str(e)), 500
