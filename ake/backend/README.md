# arxiv 知识图谱数据库后端

基于Flask的arxiv论文知识图谱API服务, 使用Neo4j图数据库存储和管理学术论文, 作者, 分类及其关系数据. 

## 功能特性

- 论文数据管理(标题, 摘要, 作者, 分类等)
- 作者信息管理和关系追踪
- 论文分类体系管理
- 复杂关系查询(作者-论文, 论文-分类等)
- 全文搜索支持
- RESTful API接口
- 跨域支持(CORS)
- 用户认证与授权
- 个性化推荐
- 数据导入与管理

## 技术栈

- **Web框架**: Flask 3.1.2
- **数据库**: Neo4j 图数据库
- **Python版本**: >= 3.12.3
- **依赖管理**: uv

## 项目结构

```
ake/backend/
├── app.py              # Flask应用入口
├── akb/                # 核心业务逻辑
│   ├── services/       # 图数据库服务层
│   │   ├── graph_service.py
│   │   ├── user_service.py
│   │   └── recommendation_service.py
│   ├── db/             # 数据库连接和模型
│   └── const.py        # 常量定义
├── api/                # API路由定义
│   ├── auth.py         # 用户认证API
│   ├── authors.py      # 作者相关API
│   ├── papers.py       # 论文相关API
│   ├── categories.py   # 分类相关API
│   ├── relationships.py # 关系查询API
│   ├── recommendations.py # 推荐相关API
│   └── data.py         # 数据管理API
├── test/               # 测试文件
└── utils/              # 工具函数
```

## 快速开始

### 环境要求

- Python >= 3.12.3
- Neo4j 数据库
- uv 包管理器

### 安装依赖

#### 安装 uv

- Linux & Mac
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
- Windows
```ps
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 同步依赖

```bash
uv sync
```

### 配置数据库

确保Neo4j数据库已启动, 并配置相应的连接参数(在 `ake/backend/akb/config.py` 中). 

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "yourusername"
NEO4J_PASSWORD = "yourpassword"
```

### 启动服务

```bash
cd ake
python -m backend.app
```

服务将在 `http://localhost:5000` 启动. 

### 健康检查

```bash
curl http://localhost:5000/health
```

## API 文档

详细的API接口文档请参考 [API_README.md](API_README.md). 

主要API端点: 
- `/api/auth` - 用户认证
- `/api/kg/authors` - 作者管理
- `/api/kg/papers` - 论文管理  
- `/api/kg/categories` - 分类管理
- `/api/kg/relationships` - 关系查询
- `/api/kg/recommendations` - 推荐服务
- `/api/kg/data` - 数据管理
- `/api/kg/data` - 数据管理

## 测试

- 后端测试

```bash
uv run pytest backend/akb/test/
```
- 前后端交接部分测试
```bash
uv run pytest backend/api/test/
```
