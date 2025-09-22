# KGMS: 知识图谱管理系统

KGMS (Knowledge Graph Management System) 是一个功能完备的知识图谱管理与展示平台。项目旨在将 [arXiv](https://arxiv.org/) 上的学术论文数据构建成知识图谱，并通过Web界面进行交互式地展示和管理。

该项目为一个全栈应用，包含独立的后端服务和前端应用：
- **后端**：基于 Python、Flask 和 Neo4j 图数据库，提供数据管理、用户认证、个性化推荐等功能的 RESTful API。
- **前端**：使用原生 HTML, CSS, 和 JavaScript 构建，负责与用户交互，并可视化后端提供的知识图谱数据。

## 主要功能

- **知识图谱构建**：将论文、作者、研究领域等实体及其关系存储在 Neo4j 数据库中。
- **数据管理**：通过 API 对论文、作者、分类等数据进行增、删、改、查。
- **关系查询**：支持复杂的关联查询，如查找作者的所有论文、探索不同研究领域之间的联系等。
- **用户系统**：提供用户注册、登录和认证功能。
- **个性化推荐**：基于图算法为用户推荐可能感兴趣的论文或学者。
- **前端可视化**：以图形化的方式展示知识网络，支持用户进行交互式探索。

## 技术栈

| 类别   | 技术                               |
| :----- | :--------------------------------- |
| **后端** | Python, Flask, Neo4j, uv         |
| **前端** | HTML, CSS, JavaScript              |
| **数据库** | Neo4j Graph Database               |

## 项目结构

```
.
├── README.md               # 项目主文档
└── ake/
    ├── backend/            # 后端应用
    │   ├── app.py          # Flask 应用入口
    │   ├── api/            # API 路由定义
    │   │   ├── auth.py          # 用户认证API
    │   │   ├── authors.py       # 作者相关API
    │   │   ├── papers.py        # 论文相关API
    │   │   ├── categories.py    # 分类相关API
    │   │   ├── relationships.py # 关系查询API
    │   │   ├── recommendations.py # 推荐相关API
    │   │   └── data.py          # 数据管理API
    │   ├── akb/            # 核心业务与数据库服务
    │   │   ├── services/        # 图数据库服务层
    │   │   │   ├── graph_service.py
    │   │   │   ├── user_service.py
    │   │   │   └── recommendation_service.py
    │   │   ├── db/              # 数据库连接和模型
    │   │   └── const.py         # 常量定义
    │   ├── test/               # 测试文件
    │   ├── utils/              # 工具函数
    │   └── README.md          # 后端详细说明
    └── frontend/           # 前端应用
        ├── login.html          # 登录入口文件
        ├── login/              # 登录相关资源
        │   ├── main.js         # login逻辑
        │   ├── defalut.css     # 样式表
        │   └── login.jpg       # 配图
        ├── main/               # 主应用目录
        │   ├── css/            # 样式文件
        │   │   ├── style.css      # 主样式文件
        │   │   └── recommendations.css  # 推荐相关样式
        │   ├── js/             # JavaScript文件
        │   │   ├── app.js         # 主应用逻辑
        │   │   ├── auth.js        # 密码判断以及跳转主页面逻辑
        │   │   └── recommendations.js  # 推荐相关功能
        │   └── main.html       # 主页面入口文件
        └── test_neo4j.py      # 测试neo4j导入数据
```

## 快速开始

### 1. 环境准备

- **Python** (>= 3.12)
- **Neo4j 数据库**：确保已安装并正在运行。
- **uv**：Python 包管理器。如果未安装，请参考[官方文档](https://github.com/astral-sh/uv)进行安装。
- 现代浏览器（如 Chrome, Firefox）。

### 2. 后端设置与启动

1.  **安装依赖**：
    进入后端目录，使用 `uv` 同步依赖。
    ```sh
    cd ake/backend
    uv sync
    ```

2.  **配置数据库连接**：
    创建或修改 `ake/backend/akb/config.py` 文件，填入你的 Neo4j 数据库凭据。
    ```python
    # ake/backend/akb/config.py
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "your_password" # 修改为你的密码
    ```

3.  **启动后端服务**：
    在 `ake` 目录下运行应用。
    ```sh
    cd ake
    python -m backend.app
    ```
    服务默认在 `http://127.0.0.1:5000` 启动。

### 3. 前端访问

直接在浏览器中打开 `ake/frontend/pages.html` 文件即可访问前端页面。前端应用将自动连接到本地运行的后端服务。

## 详细文档

- **后端架构与部署**：请参考 [后端说明文档](ake/backend/README.md)。
- **API 接口详情**：请参考 [API 文档](ake/backend/API_README.md)。
