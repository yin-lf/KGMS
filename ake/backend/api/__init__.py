from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api/kg") # 所有后端路由都挂载在/api/kg

# 创建统一的 API 响应格式
def create_response(
    success: bool = True, data=None, message: str = "", error: str = ""
):
    return jsonify(
        {"success": success, "data": data, "message": message, "error": error}
    )

# 导入所有路由
from .authors import *
from .papers import *
from .categories import *
from .relationships import *
from .data import *
