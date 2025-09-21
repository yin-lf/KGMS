import requests
import json
import time
import uuid

# API基础地址
API_BASE = "http://localhost:5000/api/kg"

# 生成唯一ID用于测试
TEST_ID = f"test_{uuid.uuid4().hex[:8]}"
TEST_AUTHOR_1 = f"测试作者_{TEST_ID}"
TEST_AUTHOR_2 = f"更新后的测试作者_{TEST_ID}"
TEST_PAPER_ID = f"paper_{TEST_ID}"
TEST_CATEGORY_1 = f"测试分类_{TEST_ID}"
TEST_CATEGORY_2 = f"更新后的测试分类_{TEST_ID}"

print(f"\n===== 开始API测试 - ID: {TEST_ID} =====\n")


class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_response(self, operation, response):
        """打印API响应信息"""
        status = "✅ 成功" if response.status_code // 100 == 2 else "❌ 失败"
        print(f"{operation} - 状态码: {response.status_code} - {status}")
        try:
            data = response.json()
            print(f"  响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"  响应内容: {response.text}")
        print()
        return response

    def wait(self, seconds=1):
        """等待一段时间，避免请求过于频繁"""
        time.sleep(seconds)


# 初始化测试器
tester = APITester(API_BASE)

# ===== 测试作者相关功能 =====
print("\n========== 测试作者相关功能 ==========")

# 1. 添加作者
print(f"1. 添加作者: {TEST_AUTHOR_1}")
response = tester.print_response(
    "添加作者",
    tester.session.post(
        f"{API_BASE}/authors",
        headers={"Content-Type": "application/json"},
        json={"name": TEST_AUTHOR_1}
    )
)
assert response.status_code == 201, "添加作者失败"

tester.wait()

# 2. 查询作者
print(f"2. 查询作者: {TEST_AUTHOR_1}")
response = tester.print_response(
    "查询作者",
    tester.session.get(f"{API_BASE}/authors/{TEST_AUTHOR_1}")
)
assert response.status_code == 200, "查询作者失败"

tester.wait()

# 3. 更新作者
print(f"3. 更新作者: {TEST_AUTHOR_1} -> {TEST_AUTHOR_2}")
response = tester.print_response(
    "更新作者",
    tester.session.put(
        f"{API_BASE}/authors/{TEST_AUTHOR_1}",
        headers={"Content-Type": "application/json"},
        json={"name": TEST_AUTHOR_2}
    )
)
assert response.status_code == 200, "更新作者失败"

tester.wait()

# 4. 验证更新后的作者
print(f"4. 验证更新后的作者: {TEST_AUTHOR_2}")
response = tester.print_response(
    "验证更新后的作者",
    tester.session.get(f"{API_BASE}/authors/{TEST_AUTHOR_2}")
)
assert response.status_code == 200, "验证更新后的作者失败"

tester.wait()

# 5. 删除作者
print(f"5. 删除作者: {TEST_AUTHOR_2}")
response = tester.print_response(
    "删除作者",
    tester.session.delete(f"{API_BASE}/authors/{TEST_AUTHOR_2}")
)
assert response.status_code == 200, "删除作者失败"

tester.wait()

# 6. 验证删除
print(f"6. 验证删除后的作者: {TEST_AUTHOR_2}")
response = tester.print_response(
    "验证删除后的作者",
    tester.session.get(f"{API_BASE}/authors/{TEST_AUTHOR_2}")
)
assert response.status_code == 404, "验证删除失败，作者仍存在"

tester.wait()


# ===== 测试分类相关功能 =====
print("\n========== 测试分类相关功能 ==========")

# 1. 添加分类
print(f"1. 添加分类: {TEST_CATEGORY_1}")
response = tester.print_response(
    "添加分类",
    tester.session.post(
        f"{API_BASE}/categories",
        headers={"Content-Type": "application/json"},
        json={"name": TEST_CATEGORY_1}
    )
)
assert response.status_code == 201, "添加分类失败"

tester.wait()

# 2. 查询分类
print(f"2. 查询分类: {TEST_CATEGORY_1}")
response = tester.print_response(
    "查询分类",
    tester.session.get(f"{API_BASE}/categories/{TEST_CATEGORY_1}")
)
assert response.status_code == 200, "查询分类失败"

tester.wait()

# 3. 更新分类
print(f"3. 更新分类: {TEST_CATEGORY_1} -> {TEST_CATEGORY_2}")
response = tester.print_response(
    "更新分类",
    tester.session.put(
        f"{API_BASE}/categories/{TEST_CATEGORY_1}",
        headers={"Content-Type": "application/json"},
        json={"name": TEST_CATEGORY_2}
    )
)
assert response.status_code == 200, "更新分类失败"

tester.wait()

# 4. 验证更新后的分类
print(f"4. 验证更新后的分类: {TEST_CATEGORY_2}")
response = tester.print_response(
    "验证更新后的分类",
    tester.session.get(f"{API_BASE}/categories/{TEST_CATEGORY_2}")
)
assert response.status_code == 200, "验证更新后的分类失败"

tester.wait()


# ===== 测试论文相关功能 =====
print("\n========== 测试论文相关功能 ==========")

# 重新添加作者用于论文测试
print(f"重新添加作者: {TEST_AUTHOR_1}")
tester.session.post(
    f"{API_BASE}/authors",
    headers={"Content-Type": "application/json"},
    json={"name": TEST_AUTHOR_1}
)

tester.wait()

# 1. 添加论文
print(f"1. 添加论文: {TEST_PAPER_ID}")
response = tester.print_response(
    "添加论文",
    tester.session.post(
        f"{API_BASE}/papers",
        headers={"Content-Type": "application/json"},
        json={
            "id": TEST_PAPER_ID,
            "title": "测试论文标题",
            "abstract": "这是一篇测试论文的摘要"
        }
    )
)
assert response.status_code == 201, "添加论文失败"

tester.wait()

# 2. 将作者与论文关联
print(f"2. 将作者 {TEST_AUTHOR_1} 与论文 {TEST_PAPER_ID} 关联")
response = tester.print_response(
    "关联作者与论文",
    tester.session.post(
        f"{API_BASE}/relationships/author-paper",
        headers={"Content-Type": "application/json"},
        json={
            "name": TEST_AUTHOR_1,
            "id": TEST_PAPER_ID
        }
    )
)
assert response.status_code == 201, "关联作者与论文失败"

tester.wait()

# 3. 将分类与论文关联
print(f"3. 将分类 {TEST_CATEGORY_2} 与论文 {TEST_PAPER_ID} 关联")
response = tester.print_response(
    "关联分类与论文",
    tester.session.post(
        f"{API_BASE}/relationships/paper-category",
        headers={"Content-Type": "application/json"},
        json={
            "id": TEST_PAPER_ID,
            "name": TEST_CATEGORY_2
        }
    )
)
assert response.status_code == 201, "关联分类与论文失败"

tester.wait()

# 2. 查询论文
print(f"2. 查询论文: {TEST_PAPER_ID}")
response = tester.print_response(
    "查询论文",
    tester.session.get(f"{API_BASE}/papers/{TEST_PAPER_ID}")
)
assert response.status_code == 200, "查询论文失败"

tester.wait()

# 3. 更新论文
print(f"3. 更新论文: {TEST_PAPER_ID}")
response = tester.print_response(
    "更新论文",
    tester.session.put(
        f"{API_BASE}/papers/{TEST_PAPER_ID}",
        headers={"Content-Type": "application/json"},
        json={
            "title": "更新后的测试论文标题",
            "abstract": "这是更新后的测试论文摘要"
        }
    )
)
assert response.status_code == 200, "更新论文失败"

tester.wait()

# 4. 验证更新后的论文
print(f"4. 验证更新后的论文: {TEST_PAPER_ID}")
response = tester.print_response(
    "验证更新后的论文",
    tester.session.get(f"{API_BASE}/papers/{TEST_PAPER_ID}")
)
assert response.status_code == 200, "验证更新后的论文失败"
# 检查标题是否已更新
paper_data = response.json()
assert paper_data['data']['title'] == "更新后的测试论文标题", "论文标题未更新"

tester.wait()

# 5. 删除论文
print(f"5. 删除论文: {TEST_PAPER_ID}")
response = tester.print_response(
    "删除论文",
    tester.session.delete(f"{API_BASE}/papers/{TEST_PAPER_ID}")
)
assert response.status_code == 200, "删除论文失败"

tester.wait()

# 6. 验证删除
print(f"6. 验证删除后的论文: {TEST_PAPER_ID}")
response = tester.print_response(
    "验证删除后的论文",
    tester.session.get(f"{API_BASE}/papers/{TEST_PAPER_ID}")
)
assert response.status_code == 404, "验证删除失败，论文仍存在"

tester.wait()


# ===== 清理测试数据 =====
print("\n========== 清理测试数据 ==========")

# 删除测试作者
tester.session.delete(f"{API_BASE}/authors/{TEST_AUTHOR_1}")

# 删除测试分类
tester.session.delete(f"{API_BASE}/categories/{TEST_CATEGORY_2}")

print("测试数据清理完成")
print(f"\n===== 测试完成 - ID: {TEST_ID} =====")