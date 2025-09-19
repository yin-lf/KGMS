const API_BASE = "http://localhost:5000/api/kg";  // 后端接口地址，根据需要修改

// 页面切换
function showSection(sectionId) {
  document.querySelectorAll(".page").forEach(sec => sec.classList.add("hidden"));
  document.getElementById(sectionId).classList.remove("hidden");
}

// 查询接口
async function search() {
  const query = document.getElementById("queryInput").value.trim();
  const resultBox = document.getElementById("queryResult");

  try {
    const res = await fetch(`${API_BASE}/authors/${encodeURIComponent(query)}`);
    const data = await res.json();
    resultBox.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultBox.textContent = "查询失败: " + err;
  }
}

// 动态添加作者输入框
function addAuthorField() {
  const div = document.getElementById('authorsList');
  const input = document.createElement('input');
  input.className = "paperAuthor";
  input.placeholder = "作者姓名";
  div.appendChild(input);
}

// 提交论文（包含多作者和分类）
async function submitPaper() {
  const paperId = document.getElementById("paperId").value.trim();
  const title = document.getElementById("paperTitle").value.trim();
  const abstract = document.getElementById("paperAbstract").value.trim();

  // 多作者
  const authors = Array.from(document.getElementsByClassName("paperAuthor"))
                       .map(input => input.value.trim())
                       .filter(name => name !== "");

  // 多分类（前端可以用逗号分隔）
  const categoriesInput = document.getElementById("paperCategory").value.trim();
  const categories = categoriesInput.split(",").map(s => s.trim()).filter(s => s !== "");

  const resultBox = document.getElementById("updateResult");

  if (!paperId || !title) {
    resultBox.textContent = "论文ID和标题不能为空！";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/papers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: paperId, title, abstract, authors, categories })
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "论文提交成功:\n" + JSON.stringify(data, null, 2)
      : "论文提交失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "提交论文失败: " + err;
  }
}
