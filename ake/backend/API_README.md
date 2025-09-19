# 知识图谱 API 接口文档

## 概述

这是一个基于Flask的知识图谱API系统, 提供了作者, 论文, 分类和关系管理的完整功能. 所有API接口都使用 `/api/kg` 作为基础路径. 

## 通用响应格式

所有API接口返回统一的JSON格式: 

```json
{
    "success": true/false,
    "data": {},
    "message": "成功或错误信息",
    "error": "错误详情(仅在失败时)"
}
```

## 作者管理 API

### 1. 添加作者

**请求**
- **URL**: `POST /api/kg/authors`
- **请求体**:
```json
{
    "name": "作者姓名"
}
```

**响应**
- **成功** (201): 作者添加成功
- **错误** (400): 请求数据无效
- **错误** (409): 作者已存在

### 2. 获取作者信息

**请求**
- **URL**: `GET /api/kg/authors/{name}`

**响应**
- **成功** (200):
```json
{
    "success": true,
    "data": {
        "name": "作者姓名",
        "papers": [
            {"id": "论文ID", "title": "论文标题"},
            {"id": "论文ID", "title": "论文标题"}
        ]
    },
    "message": "作者信息获取成功"
}
```
- **错误** (404): 作者未找到

### 3. 获取所有作者列表

**请求**
- **URL**: `GET /api/kg/authors`

**响应**
- **成功** (200): 返回所有作者及其发表论文信息

### 4. 删除作者

**请求**
- **URL**: `DELETE /api/kg/authors/{name}`

**响应**
- **成功** (200): 作者删除成功
- **错误** (404): 作者未找到

## 论文管理 API

### 1. 添加论文

**请求**
- **URL**: `POST /api/kg/papers`
- **请求体**:
```json
{
    "id": "论文ID",
    "title": "论文标题",
    "abstract": "论文摘要(可选)"
}
```

**响应**
- **成功** (201): 论文添加成功
- **错误** (409): 论文已存在

### 2. 获取论文信息

**请求**
- **URL**: `GET /api/kg/papers/{id}`

**响应**
- **成功** (200):
```json
{
    "success": true,
    "data": {
        "id": "论文ID",
        "title": "论文标题",
        "abstract": "论文摘要",
        "authors": ["作者列表"],
        "categories": ["分类列表"]
    },
    "message": "论文信息获取成功"
}
```

### 3. 更新论文信息

**请求**
- **URL**: `PUT /api/kg/papers/{id}`
- **请求体**:
```json
{
    "title": "新标题(可选)",
    "abstract": "新摘要(可选)"
}
```

**响应**
- **成功** (200): 论文更新成功
- **错误** (400): 至少需要提供一个字段进行更新

### 4. 删除论文

**请求**
- **URL**: `DELETE /api/kg/papers/{id}`

**响应**
- **成功** (200): 论文删除成功
- **错误** (404): 论文未找到

### 5. 搜索论文

**请求**
- **URL**: `GET /api/kg/papers/search?q={搜索关键词}`

**响应**
- **成功** (200): 返回匹配的论文列表
- **错误** (400): 搜索关键词不能为空
- **错误** (500): 内部服务器错误, 大概率是由未建立论文标题与摘要索引导致

### 6. 获取所有论文列表

**请求**
- **URL**: `GET /api/kg/papers`

**响应**
- **成功** (200): 返回所有论文的详细信息

## 分类管理 API

### 1. 添加分类

**请求**
- **URL**: `POST /api/kg/categories`
- **请求体**:
```json
{
    "name": "分类名称"
}
```

**响应**
- **成功** (201): 分类添加成功
- **错误** (409): 分类已存在

### 2. 获取分类信息

**请求**
- **URL**: `GET /api/kg/categories/{name}`

**响应**
- **成功** (200):
```json
{
    "success": true,
    "data": {
        "name": "分类名称",
        "papers": [
            {"id": "论文ID", "title": "论文标题"},
            {"id": "论文ID", "title": "论文标题"}
        ]
    },
    "message": "分类信息获取成功"
}
```

### 3. 更新分类名称

**请求**
- **URL**: `PUT /api/kg/categories/{old_name}`
- **请求体**:
```json
{
    "name": "新分类名称"
}
```

**响应**
- **成功** (200): 分类更新成功
- **错误** (409): 新分类名称已存在

### 4. 删除分类

**请求**
- **URL**: `DELETE /api/kg/categories/{name}`

**响应**
- **成功** (200): 分类删除成功
- **错误** (404): 分类未找到

### 5. 获取所有分类列表

**请求**
- **URL**: `GET /api/kg/categories`

**响应**
- **成功** (200): 返回所有分类及其相关论文信息

## 关系管理 API

### 1. 创建作者-论文关联

**请求**
- **URL**: `POST /api/kg/relationships/author-paper`
- **请求体**:
```json
{
    "name": "作者姓名",
    "id": "论文ID"
}
```

**响应**
- **成功** (201): 关联创建成功
- **错误** (404): 作者或论文未找到

### 2. 删除作者-论文关联

**请求**
- **URL**: `DELETE /api/kg/relationships/author-paper`
- **请求体**:
```json
{
    "name": "作者姓名",
    "id": "论文ID"
}
```

**响应**
- **成功** (200): 关联删除成功

### 3. 创建论文-分类关联

**请求**
- **URL**: `POST /api/kg/relationships/paper-category`
- **请求体**:
```json
{
    "id": "论文ID",
    "name": "分类名称"
}
```

**响应**
- **成功** (201): 关联创建成功
- **错误** (404): 论文或分类未找到

### 4. 删除论文-分类关联

**请求**
- **URL**: `DELETE /api/kg/relationships/paper-category`
- **请求体**:
```json
{
    "id": "论文ID",
    "name": "分类名称"
}
```

**响应**
- **成功** (200): 关联删除成功

## 数据管理 API

### 1. 获取图谱概览信息

**请求**
- **URL**: `GET /api/kg/data/info`

**响应**
- **成功** (200):
```json
{
    "success": true,
    "data": {
        "total_authors": 100,
        "total_papers": 500,
        "total_categories": 20,
        "num_papers_per_category": {
            "分类1": 50,
            "分类2": 30
        }
    },
    "message": "图谱概览获取成功"
}
```

### 2. 批量加载数据

**请求**
- **URL**: `POST /api/kg/data/load`
- **请求体**:
```json
{
    "id": "论文ID",
    "title": "论文标题",
    "abstract": "论文摘要(可选)",
    "authors": "作者1,作者2,作者3",
    "categories": "分类1 分类2"
}
```

**响应**
- **成功** (201): 数据加载成功
- **错误** (409): 论文已存在

### 3. 清空所有数据

**请求**
- **URL**: `DELETE /api/kg/data/clear`

**响应**
- **成功** (200): 所有数据清空成功

### 4. 检查论文索引是否建立

**请求**
- **URL**: `GET /api/kg/data/check_index`

**响应**
- **成功** (200):
```json
{
    "sucess": true,
    "data": true,
    "message": "Full-text index exists",
}
```
```json
{
    "sucess": true,
    "data": false,
    "message": "Full-text index does not exist",
}
```

### 5. 建立论文索引

**请求**
- **URL**: `POST /api/kg/data/create_index`

**响应**
- **成功** (200):
```json
{
    "sucess": true,
    "message": "Full-text index created successfully"
}
```

### 6. 删除论文索引

**请求**
- **URL**: `POST /api/kg/data/drop_index`

**相应**
- **成功** (200):
```json
{
    "sucess": true,
    "message": "Full-text index dropped successfully"
}
```

## 错误处理

API使用标准HTTP状态码: 

- **200**: 请求成功
- **201**: 资源创建成功
- **400**: 请求参数错误
- **404**: 资源未找到
- **409**: 资源冲突(如重复创建)
- **500**: 服务器内部错误

## 使用示例

### 创建完整的知识图谱数据流程

1. 添加作者: 
```bash
curl -X POST http://localhost:5000/api/kg/authors \
  -H "Content-Type: application/json" \
  -d '{"name": "张三"}'
```

2. 添加论文: 
```bash
curl -X POST http://localhost:5000/api/kg/papers \
  -H "Content-Type: application/json" \
  -d '{"id": "P001", "title": "深度学习研究", "abstract": "这是一篇关于深度学习的论文"}'
```

3. 添加分类: 
```bash
curl -X POST http://localhost:5000/api/kg/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "人工智能"}'
```

4. 建立关联关系: 
```bash
curl -X POST http://localhost:5000/api/kg/relationships/author-paper \
  -H "Content-Type: application/json" \
  -d '{"author": "张三", "id": "P001"}'

curl -X POST http://localhost:5000/api/kg/relationships/paper-category \
  -H "Content-Type: application/json" \
  -d '{"id": "P001", "category_name": "人工智能"}'
```

## 注意事项

1. 所有POST和PUT请求都需要设置`Content-Type: application/json`
2. 数据验证使用Marshmallow schema, 会返回详细的验证错误信息
3. 所有字符串参数都会进行空格清理
4. 删除操作会同时清理相关的关联关系
5. 搜索功能支持模糊匹配
6. 批量数据加载会自动创建相关的作者, 分类和关联关系
