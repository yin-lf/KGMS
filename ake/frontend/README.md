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
├── login.html          # 入口文件
|—— login/
|   ├── main.js         # login逻辑
|   ├── defalut.css        # 样式表
|   └── login.jpg       # 配图
├── main/               # 主文件目录
│   ├── css/               # 样式文件目录
│   |    ├── style.css      # 主样式文件
|   |    └── recommendations.css  # 推荐相关样式
|   ├── js/                # JavaScript文件目录
|   |    ├── app.js         # 主应用逻辑
|   |    ├── auth.js         # 密码判断以及跳转主页面逻辑
|   |    └── recommendations.js  # 推荐相关功能
|   └── main.html      # 主页面入口文件
└── test_neo4j.py      # 测试是否导入数据
```

## 快速开始

直接在浏览器中打开 `ake/frontend/index.html` 文件即可访问前端页面。前端应用将自动连接到本地运行的后端服务。
