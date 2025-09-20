# KGMS
knowledge-graph--management-system. 知识工程综合实践——开发具有后台知识图谱数据库和前台用户界面的知识图谱管理信息系统。

后端说明文档：`ake\backend\README.md`，确保环境具有所需的包。

后端API文档：`ake\backend\API_README.md`

后端启动及测试：首先修改`ake\backend\akb\config.py`中`NEO4J_PASSWORD`等常量，启动本地Neo4j数据库，随后执行：
```sh
cd ake
python -m backend.app
pytest
```