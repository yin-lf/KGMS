import pytest
import requests

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/kg"


def api_request(method, endpoint, data=None, params=None, session=None):
    """Make HTTP request to the API."""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    requester = session or requests

    try:
        if method.upper() == "GET":
            response = requester.get(url, params=params, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requester.post(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "PUT":
            response = requester.put(url, json=data, headers=headers, timeout=30)
        elif method.upper() == "DELETE":
            response = requester.delete(url, json=data, headers=headers, timeout=30)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        return response
    except requests.exceptions.RequestException as e:
        pytest.fail(f"请求失败: {e}")


@pytest.fixture(scope="session", autouse=True)
def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            pytest.skip("API 服务器未运行或不健康")
    except requests.exceptions.RequestException:
        pytest.skip("无法连接到 API 服务器")


def test_create_index():
    """测试创建全文索引"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    response = api_request("POST", "/api/kg/data/create_index")
    assert response.status_code == 200


def test_drop_index():
    """测试删除全文索引"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    response = api_request("POST", "/api/kg/data/drop_index")
    assert response.status_code == 200


def test_add_category():
    """测试添加分类"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    category_data = {"name": "人工智能"}
    response = api_request("POST", "/api/kg/categories", data=category_data)
    assert response.status_code == 201


def test_add_author():
    """测试添加作者"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    author_data = {"name": "张三"}
    response = api_request("POST", "/api/kg/authors", data=author_data)
    assert response.status_code == 201


def test_add_paper():
    """测试添加论文"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }
    response = api_request("POST", "/api/kg/papers", data=paper_data)
    assert response.status_code == 201


def test_create_author_paper_relationship():
    """测试建立作者-论文关系"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    author_data = {"name": "张三"}
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }

    api_request("POST", "/api/kg/authors", data=author_data)
    api_request("POST", "/api/kg/papers", data=paper_data)

    relationship_data = {"name": "张三", "id": "paper001"}
    response = api_request(
        "POST", "/api/kg/relationships/author-paper", data=relationship_data
    )
    assert response.status_code == 201, response.text


def test_create_paper_category_relationship():
    """测试建立论文-分类关系"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }
    category_data = {"name": "人工智能"}

    api_request("POST", "/api/kg/papers", data=paper_data)
    api_request("POST", "/api/kg/categories", data=category_data)

    relationship_data = {"id": "paper001", "name": "人工智能"}
    response = api_request(
        "POST", "/api/kg/relationships/paper-category", data=relationship_data
    )
    assert response.status_code == 201


def test_delete_author_paper_relationship():
    """测试删除作者-论文关系"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    author_data = {"name": "张三"}
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }

    api_request("POST", "/api/kg/authors", data=author_data)
    api_request("POST", "/api/kg/papers", data=paper_data)

    relationship_data = {"name": "张三", "id": "paper001"}
    api_request("POST", "/api/kg/relationships/author-paper", data=relationship_data)

    response = api_request(
        "DELETE", "/api/kg/relationships/author-paper", data=relationship_data
    )
    assert response.status_code == 200


def test_delete_paper_category_relationship():
    """测试删除论文-分类关系"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }
    category_data = {"name": "人工智能"}

    api_request("POST", "/api/kg/papers", data=paper_data)
    api_request("POST", "/api/kg/categories", data=category_data)

    relationship_data = {"id": "paper001", "name": "人工智能"}
    api_request("POST", "/api/kg/relationships/paper-category", data=relationship_data)

    response = api_request(
        "DELETE", "/api/kg/relationships/paper-category", data=relationship_data
    )
    assert response.status_code == 200


def test_get_author():
    """测试查询作者信息"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    author_data = {"name": "张三"}
    api_request("POST", "/api/kg/authors", data=author_data)

    response = api_request("GET", "/api/kg/authors/张三")
    assert response.status_code == 200
    data = response.json()
    assert data["data"].get("name") == "张三"


def test_get_paper():
    """测试查询论文信息"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }
    api_request("POST", "/api/kg/papers", data=paper_data)

    response = api_request("GET", "/api/kg/papers/paper001")
    assert response.status_code == 200
    data = response.json()
    assert data["data"].get("id") == "paper001"


def test_get_category():
    """测试查询分类信息"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    category_data = {"name": "人工智能"}
    api_request("POST", "/api/kg/categories", data=category_data)

    response = api_request("GET", "/api/kg/categories/人工智能")
    assert response.status_code == 200
    data = response.json()
    assert data["data"].get("name") == "人工智能"


def test_search_papers():
    """测试搜索论文"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    paper_data = {
        "id": "paper001",
        "title": "机器学习基础",
        "abstract": "本文探讨了机器学习的基本概念和算法, 并粗浅的提到了深度学习.",
    }
    paper_data2 = {
        "id": "paper002",
        "title": "知识工程基础",
        "abstract": "本文探讨了知识工程的基本概念和算法.",
    }
    paper_data3 = {
        "id": "paper003",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }
    api_request("POST", "/api/kg/papers", data=paper_data)
    api_request("POST", "/api/kg/papers", data=paper_data2)
    api_request("POST", "/api/kg/papers", data=paper_data3)
    api_request("POST", "/api/kg/data/create_index")  # 确保索引存在

    response = api_request("GET", "/api/kg/papers/search", params={"q": "深度学习"})
    assert response.status_code == 200
    data = response.json()
    search_results = data["data"]
    assert isinstance(search_results, list) and len(search_results) == 2
    assert (
        search_results[0]["id"] == "paper003" and search_results[1]["id"] == "paper001"
    )


def test_update_paper():
    """测试更新论文"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "TBA",
    }
    api_request("POST", "/api/kg/papers", data=paper_data)

    update_data = {"abstract": "更新后的摘要: 本文深入探讨了深度学习在NLP中的创新应用."}
    response = api_request("PUT", "/api/kg/papers/paper001", data=update_data)
    assert response.status_code == 200
    data = response.json()
    assert "更新后的摘要" in data["data"]["abstract"]


def test_get_graph_info():
    """测试获取图谱概览信息"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    response = api_request("GET", "/api/kg/data/info")
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, dict)
    assert "total_authors" in data and data["total_authors"] == 0
    assert "total_papers" in data and data["total_papers"] == 0
    assert "total_categories" in data and data["total_categories"] == 0
    assert (
        "num_papers_per_category" in data
        and isinstance(data["num_papers_per_category"], dict)
        and len(data["num_papers_per_category"]) == 0
    )


def test_load_json_data():
    """测试从JSON加载数据"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    json_data = {
        "id": "paper002",
        "title": "机器学习基础",
        "abstract": "介绍机器学习的基本概念和算法.",
        "authors": "李四, 王五",
        "categories": "cs.AI cs.LG",
        "doi": "10.1000/xyz123",
    }
    response = api_request("POST", "/api/kg/data/load", data=json_data)
    assert response.status_code == 201


def test_complete_workflow():
    """测试完整的工作流程"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    # 1. 创建基础数据
    category_data = {"name": "人工智能"}
    author_data = {"name": "张三"}
    paper_data = {
        "id": "paper001",
        "title": "深度学习在自然语言处理中的应用",
        "abstract": "本文探讨了深度学习技术在自然语言处理领域的最新进展和应用.",
    }
    api_request("POST", "/api/kg/categories", data=category_data)
    api_request("POST", "/api/kg/authors", data=author_data)
    api_request("POST", "/api/kg/papers", data=paper_data)

    # 2. 建立关系
    author_paper_link = {"name": "张三", "id": "paper001"}
    paper_category_link = {"id": "paper001", "name": "人工智能"}
    api_request("POST", "/api/kg/relationships/author-paper", data=author_paper_link)
    api_request(
        "POST", "/api/kg/relationships/paper-category", data=paper_category_link
    )

    # 3. 验证查询
    author_response = api_request("GET", "/api/kg/authors/张三")
    assert author_response.status_code == 200

    paper_response = api_request("GET", "/api/kg/papers/paper001")
    assert paper_response.status_code == 200

    category_response = api_request("GET", "/api/kg/categories/人工智能")
    assert category_response.status_code == 200

    # 4. 搜索测试
    api_request("POST", "/api/kg/data/create_index")  # 确保索引存在
    search_response = api_request("GET", "/api/kg/papers/search", params={"q": "深度学习"})
    assert search_response.status_code == 200

    # 5. 更新测试
    update_data = {"abstract": "更新后的摘要: 本文深入探讨了深度学习在NLP中的创新应用."}
    update_response = api_request("PUT", "/api/kg/papers/paper001", data=update_data)
    assert update_response.status_code == 200

    # 6. 获取图谱信息
    info_response = api_request("GET", "/api/kg/data/info")
    assert info_response.status_code == 200
    assert info_response.json()["data"]["total_authors"] == 1
    assert info_response.json()["data"]["total_papers"] == 1
    assert info_response.json()["data"]["total_categories"] == 1
    assert len(info_response.json()["data"]["num_papers_per_category"]) == 1
    assert "人工智能" in info_response.json()["data"]["num_papers_per_category"]
    assert info_response.json()["data"]["num_papers_per_category"]["人工智能"] == 1


def test_register_user():
    """测试用户注册"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    user_data = {"username": "testuser", "password": "password123"}
    response = api_request("POST", "/api/auth/register", data=user_data)
    assert response.status_code == 201
    # 测试重复注册
    response = api_request("POST", "/api/auth/register", data=user_data)
    assert response.status_code == 409


def test_login_user():
    """测试用户登录"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    user_data = {"username": "testuser", "password": "password123"}
    api_request("POST", "/api/auth/register", data=user_data)

    # 测试成功登录
    response = api_request("POST", "/api/auth/login", data=user_data)
    assert response.status_code == 200

    # 测试密码错误
    invalid_data = {"username": "testuser", "password": "wrongpassword"}
    response = api_request("POST", "/api/auth/login", data=invalid_data)
    assert response.status_code == 401


def test_record_feedback_and_get_liked():
    """测试记录反馈和获取喜欢的文章"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    with requests.Session() as session:
        # 注册并登录
        user_data = {"username": "feedbackuser", "password": "password123"}
        api_request("POST", "/api/auth/register", data=user_data, session=session)
        login_response = api_request(
            "POST", "/api/auth/login", data=user_data, session=session
        )
        assert login_response.status_code == 200

        # 创建论文
        paper_data = {"id": "feedbackpaper", "title": "Feedback Test Paper"}
        api_request("POST", "/api/kg/papers", data=paper_data, session=session)

        # 记录喜欢
        feedback_data = {"paper_id": "feedbackpaper", "liked": True}
        response = api_request(
            "POST", "/api/feedback", data=feedback_data, session=session
        )
        assert response.status_code == 200

        # 获取喜欢的列表
        response = api_request("GET", "/api/liked", session=session)
        assert response.status_code == 200
        liked_papers = response.json()["data"]
        assert len(liked_papers) == 1
        assert liked_papers[0]["id"] == "feedbackpaper"

        # 取消喜欢
        feedback_data_unlike = {"paper_id": "feedbackpaper", "liked": False}
        response = api_request(
            "POST", "/api/feedback", data=feedback_data_unlike, session=session
        )
        assert response.status_code == 200

        # 再次获取喜欢的列表
        response = api_request("GET", "/api/liked", session=session)
        assert response.status_code == 200
        assert len(response.json()["data"]) == 0


def test_get_recommendations():
    """测试获取推荐"""
    api_request("DELETE", "/api/kg/data/clear")  # 清理
    # 创建论文
    api_request("POST", "/api/kg/papers", data={"id": "p1", "title": "Paper 1"})
    api_request("POST", "/api/kg/papers", data={"id": "p2", "title": "Paper 2"})
    api_request("POST", "/api/kg/papers", data={"id": "p3", "title": "Paper 3"})

    # 用户1
    with requests.Session() as session1:
        user1 = {"username": "user1", "password": "password"}
        api_request("POST", "/api/auth/register", data=user1, session=session1)
        api_request("POST", "/api/auth/login", data=user1, session=session1)
        # 用户1喜欢p1, p2
        api_request(
            "POST", "/api/feedback", data={"paper_id": "p1", "liked": True}, session=session1
        )
        api_request(
            "POST", "/api/feedback", data={"paper_id": "p2", "liked": True}, session=session1
        )

    # 用户2
    with requests.Session() as session2:
        user2 = {"username": "user2", "password": "password"}
        api_request("POST", "/api/auth/register", data=user2, session=session2)
        api_request("POST", "/api/auth/login", data=user2, session=session2)
        # 用户2喜欢p2, p3
        api_request(
            "POST", "/api/feedback", data={"paper_id": "p2", "liked": True}, session=session2
        )
        api_request(
            "POST", "/api/feedback", data={"paper_id": "p3", "liked": True}, session=session2
        )

    # 切换回用户1
    with requests.Session() as session1:
        user1 = {"username": "user1", "password": "password"}
        api_request("POST", "/api/auth/login", data=user1, session=session1)
        # 获取推荐, 应该推荐p3
        response = api_request("GET", "/api/recommendations", session=session1)
        assert response.status_code == 200
        recommendations = response.json()["data"]
        assert len(recommendations) > 0
        assert recommendations[0]["id"] == "p3"
