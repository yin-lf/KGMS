# 知识图谱管理系统前端

基于Flask的arxiv论文知识图谱前端页面

## 功能特性

- 知识图谱管理系统的增删改查（页面设计+统一前后端api）

## 技术栈

- **Web框架**: Flask 3.1.2
- **数据库**: Neo4j 图数据库
- **Python版本**: >= 3.12.3
- **依赖管理**: uv

## 项目结构

```
ake/frontend/           # 前端应用根目录
├── index.html          # 主入口文件（重命名）
├── css/               # 样式文件目录
│   ├── style.css      # 主样式文件
│   |── auth.css       # 登录相关样式
|   └── recommendations.css  # 推荐相关样式
├── js/                # JavaScript文件目录
|   ├── app.js         # 主应用逻辑
|   ├── auth.js        # 认证相关功能
|   └── recommendations.js  # 推荐相关功能
└── test_neo4j.py      # 测试是否导入数据
```

## 快速开始

直接在浏览器中打开 `ake/frontend/index.html` 文件即可访问前端页面。前端应用将自动连接到本地运行的后端服务。
