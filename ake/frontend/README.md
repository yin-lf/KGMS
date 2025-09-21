# 知识图谱管理系统前端

基于Flask的arxiv论文知识图谱前端页面

## 功能特性

* **用户注册与登录** - 安全的用户名密码认证系统，保障用户数据隐私
* **查询功能** - 支持按论文ID、作者、分类和关键词多种方式检索学术资源
* **添加功能** - 可向系统添加新的论文、作者和分类信息
* **修改功能** - 支持对现有论文、作者和分类信息进行编辑更新
* **删除功能** - 提供安全的内容移除机制，维护数据质量
* **推荐功能** - 基于用户行为和内容特征提供个性化论文推荐

## 技术栈

* **Web框架** : Flask 3.1.2
* **数据库** : Neo4j 图数据库
* **前端技术** : HTML, CSS, JavaScript
* **密码安全** : bcrypt哈希加密
* **Python版本** : >= 3.12.3
* **依赖管理** : uv

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

后端——

1. .\bin\neo4j.bat console启动neo4并登录
2. 终端运行python app.py连接neo4j

前端——直接在浏览器中打开 `ake/frontend/login.html` 文件即可访问登录界面，登录成功后自动跳转至main.html主页面。前端应用将自动连接到本地运行的后端服务。
