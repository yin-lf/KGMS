const API_BASE = "http://localhost:5000/api/kg";  // 后端接口地址，根据需要修改
const RECOMMENDATION_API = `${API_BASE}/recommendations`;

// 页面切换功能
function showSection(sectionId) {
  // 隐藏所有页面
  document.querySelectorAll('.page').forEach(page => {
      page.classList.add('hidden');
  });

  // 显示选中的页面
  document.getElementById(sectionId).classList.remove('hidden');
}
// 导航新增视觉提示
document.addEventListener('DOMContentLoaded', function() {
  // 默认显示查询页面
  showSection('query');

  const navButtons = document.querySelectorAll('nav button');
  navButtons.forEach(button => {
      button.addEventListener('click', function() {
          // 移除所有按钮的active类
          navButtons.forEach(btn => btn.classList.remove('active'));
          // 给当前点击的按钮添加active类
          this.classList.add('active');
      });
  });

  // 初始化第一个导航按钮为active状态
  if (navButtons.length > 0) {
      navButtons[0].classList.add('active');
  }
});

// 动态添加作者输入框
function addAuthorField() {
  const div = document.getElementById('authorsList');
  const input = document.createElement('input');
  input.className = "paperAuthor";
  input.placeholder = "作者姓名";
  div.appendChild(input);
}

/*============增===============*/
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

  const resultBox = document.getElementById("addResult");

  if (!paperId || !title) {
    resultBox.textContent = "论文ID和标题不能为空！";
    return;
  }

  try {
    // 1. 先提交论文基本信息（不含关系）
    const res = await fetch(`${API_BASE}/papers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: paperId, title, abstract })
    });

    const data = await res.json();
    
    if (data.success) {
      let relationshipResults = [];
      
      // 辅助函数：检查并创建作者（如果不存在）
      async function ensureAuthorExists(authorName) {
        try {
          // 先检查作者是否存在
          const checkRes = await fetch(`${API_BASE}/authors/${authorName}`);
          if (checkRes.status === 404) {
            // 作者不存在，创建作者
            const createRes = await fetch(`${API_BASE}/authors`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ name: authorName })
            });
            const createData = await createRes.json();
            return createData.success;
          }
          return true; // 作者已存在
        } catch (err) {
          console.error(`检查/创建作者 ${authorName} 失败:`, err);
          return false;
        }
      }
      
      // 辅助函数：检查并创建分类（如果不存在）
      async function ensureCategoryExists(categoryName) {
        try {
          // 先检查分类是否存在
          const checkRes = await fetch(`${API_BASE}/categories/${categoryName}`);
          if (checkRes.status === 404) {
            // 分类不存在，创建分类
            const createRes = await fetch(`${API_BASE}/categories`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ name: categoryName })
            });
            const createData = await createRes.json();
            return createData.success;
          }
          return true; // 分类已存在
        } catch (err) {
          console.error(`检查/创建分类 ${categoryName} 失败:`, err);
          return false;
        }
      }
      
      // 2. 关联作者
      if (authors.length > 0) {
        for (const author of authors) {
          // 确保作者存在
          const authorExists = await ensureAuthorExists(author);
          if (!authorExists) {
            relationshipResults.push(`作者 ${author} 不存在且创建失败，无法关联`);
            continue;
          }
          
          // 关联作者和论文
          const authorRes = await fetch(`${API_BASE}/relationships/author-paper`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: author, id: paperId })
          });
          const authorData = await authorRes.json();
          relationshipResults.push(
            `作者 ${author} 关联${authorData.success ? "成功" : "失败"}`
          );
        }
      }
      
      // 3. 关联分类
      if (categories.length > 0) {
        for (const category of categories) {
          // 确保分类存在
          const categoryExists = await ensureCategoryExists(category);
          if (!categoryExists) {
            relationshipResults.push(`分类 ${category} 不存在且创建失败，无法关联`);
            continue;
          }
          
          // 关联分类和论文
          const categoryRes = await fetch(`${API_BASE}/relationships/paper-category`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: paperId, name: category })
          });
          const categoryData = await categoryRes.json();
          relationshipResults.push(
            `分类 ${category} 关联${categoryData.success ? "成功" : "失败"}`
          );
        }
      }
      
      resultBox.textContent = "论文提交成功:\n" + 
        JSON.stringify(data, null, 2) + 
        (relationshipResults.length > 0 ? "\n\n关系关联结果:\n" + relationshipResults.join("\n") : "");
    } else {
      resultBox.textContent = "论文提交失败:\n" + JSON.stringify(data, null, 2);
    }

  } catch (err) {
    resultBox.textContent = "提交论文失败: " + err;
  }
}

/*============删===============*/
// 删除作者
async function deleteAuthor() {
  const name = document.getElementById("deleteAuthorName").value.trim();
  const resultBox = document.getElementById("deleteResult");

  if (!name) {
    resultBox.textContent = "作者名不能为空！";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/authors/${encodeURIComponent(name)}`, {
      method: "DELETE"
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "作者删除成功:\n" + JSON.stringify(data, null, 2)
      : "作者删除失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "删除作者失败: " + err;
  }
}
// 删除论文
async function deletePaper() {
  const paperId = document.getElementById("deletePaperId").value.trim();
  const resultBox = document.getElementById("deleteResult");

  if (!paperId) {
    resultBox.textContent = "论文ID不能为空！";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/papers/${encodeURIComponent(paperId)}`, {
      method: "DELETE"
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "论文删除成功:\n" + JSON.stringify(data, null, 2)
      : "论文删除失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "删除论文失败: " + err;
  }
}
// 删除分类
async function deleteCategory() {
  const name = document.getElementById("deleteCategoryName").value.trim();
  const resultBox = document.getElementById("deleteResult");

  if (!name) {
    resultBox.textContent = "分类名不能为空！";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/categories/${encodeURIComponent(name)}`, {
      method: "DELETE"
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "分类删除成功:\n" + JSON.stringify(data, null, 2)
      : "分类删除失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "删除分类失败: " + err;
  }
}

/*============改===============*/
// 更新作者
async function updateAuthor() {
  const oldName = document.getElementById("oldAuthorName").value.trim();
  const newName = document.getElementById("newAuthorName").value.trim();
  const resultBox = document.getElementById("modifyResult");

  if (!oldName || !newName) {
    resultBox.textContent = "原作者名和新作者名不能为空！";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/authors/${encodeURIComponent(oldName)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName })
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "作者更新成功:\n" + JSON.stringify(data, null, 2)
      : "作者更新失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "更新作者失败: " + err;
  }
}
// 更新论文
async function updatePaper() {
  const paperId = document.getElementById("updatePaperId").value.trim();
  const newTitle = document.getElementById("updatePaperTitle").value.trim();
  const newAbstract = document.getElementById("updatePaperAbstract").value.trim();
  const resultBox = document.getElementById("modifyResult");

  if (!paperId) {
    resultBox.textContent = "论文ID不能为空！";
    return;
  }

  if (!newTitle && !newAbstract) {
    resultBox.textContent = "至少需要填写标题或摘要中的一项！";
    return;
  }

  try {
    const updateData = {};
    if (newTitle) updateData.title = newTitle;
    if (newAbstract) updateData.abstract = newAbstract;

    const res = await fetch(`${API_BASE}/papers/${encodeURIComponent(paperId)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData)
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "论文更新成功:\n" + JSON.stringify(data, null, 2)
      : "论文更新失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "更新论文失败: " + err;
  }
}
// 更新分类
async function updateCategory() {
  const oldName = document.getElementById("oldCategoryName").value.trim();
  const newName = document.getElementById("newCategoryName").value.trim();
  const resultBox = document.getElementById("modifyResult");

  if (!oldName || !newName) {
    resultBox.textContent = "原分类名和新分类名不能为空！";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/categories/${encodeURIComponent(oldName)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newName })
    });

    const data = await res.json();
    resultBox.textContent = data.success
      ? "分类更新成功:\n" + JSON.stringify(data, null, 2)
      : "分类更新失败:\n" + JSON.stringify(data, null, 2);

  } catch (err) {
    resultBox.textContent = "更新分类失败: " + err;
  }
}

/*============查===============*/
async function search() {
  const query = document.getElementById("queryInput").value.trim();
  const resultBox = document.getElementById("queryResult");

  if (!query) {
    resultBox.textContent = "查询内容不能为空！";
    return;
  }

  try {
    // 首先尝试按论文ID查询
    let res = await fetch(`${API_BASE}/papers/${encodeURIComponent(query)}`);
    let data = await res.json();
    
    if (data.success) {
      resultBox.textContent = "找到论文信息:\n" + JSON.stringify(data, null, 2);
      return;
    }
    
    // 然后尝试按作者名查询
    res = await fetch(`${API_BASE}/authors/${encodeURIComponent(query)}`);
    data = await res.json();
    
    if (data.success) {
      resultBox.textContent = "找到作者信息:\n" + JSON.stringify(data, null, 2);
      return;
    }
    
    // 接着尝试按分类名查询
    res = await fetch(`${API_BASE}/categories/${encodeURIComponent(query)}`);
    data = await res.json();
    
    if (data.success) {
      resultBox.textContent = "找到分类信息:\n" + JSON.stringify(data, null, 2);
      return;
    }
    
    // 最后尝试全文搜索论文
    res = await fetch(`${API_BASE}/papers/search?q=${encodeURIComponent(query)}`);
    data = await res.json();
    
    if (data.success && data.data && data.data.length > 0) {
      resultBox.textContent = "搜索到相关论文:\n" + JSON.stringify(data, null, 2);
      return;
    }
    
    resultBox.textContent = "未找到相关信息";
  } catch (err) {
    resultBox.textContent = "查询失败: " + err;
  }
}

/*============推荐===============*/
document.addEventListener('DOMContentLoaded', function() {
  // 初始化推荐模块
  Recommendations.init();
  
  // 如果当前在推荐页面且用户已登录，自动获取推荐
  if (!document.getElementById('recommend').classList.contains('hidden') && Auth.isLoggedIn()) {
    Recommendations.getRecommendations();
  }
});