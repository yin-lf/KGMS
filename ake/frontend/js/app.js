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
function formatPaper(paper) {
  if (!paper) return "未找到论文信息。";
  let result = "";
  result += `<strong>--- 论文信息 ---</strong><br>`;
  result += `ID: ${paper.id || 'N/A'}<br>`;
  result += `标题: ${paper.title || 'N/A'}<br>`;
  // 处理作者信息
  if (paper.authors && paper.authors.length > 0) {
    const authorNames = paper.authors.map(author => 
      author.name || (typeof author === 'string' ? author : '未知作者')
    );
    result += `作者: ${authorNames.join(', ')}<br>`;
  } else {
    result += `作者: N/A<br>`;
  }
  // 分类信息
  if (paper.category) {
    // 如果分类信息直接包含在paper对象中
    result += `分类: ${paper.category.name || paper.category}<br>`;
  } else if (paper.categories && paper.categories.length > 0) {
    // 如果有多个分类
    const categoryNames = paper.categories.map(cat => cat.name || cat);
    result += `分类: ${categoryNames.join(', ')}<br>`;
  } else {
    result += `分类: N/A<br>`;
  }
  if (paper.abstract) {
    // 截断摘要以保持简洁
    const abstractPreview = paper.abstract.length > 500 ? 
      paper.abstract.substring(0, 500) + '...' : paper.abstract;
    result += `摘要: ${abstractPreview}<br>`;
  }
  // 添加arXiv预览链接（可点击的超链接）
  if (paper.id && paper.id.includes('.')) {
    result += `【arXiv论文预览：<a href="https://arxiv.org/abs/${paper.id}" target="_blank" style="color: #0066cc; text-decoration: none;">https://arxiv.org/abs/${paper.id}</a>】`;
  }
  return result;
}
function formatAuthor(author) {
  if (!author) return "未找到作者信息。";

  let result = `<strong>--- 作者信息 ---</strong><br>`;
  result += `姓名: ${author.name || 'N/A'}<br>`;
  if (author.id) {
    result += `ID: ${author.id}<br>`;
  }
  if (author.papers && author.papers.length > 0) {
    result += `相关论文 (${author.papers.length}篇):<br>`;
    author.papers.slice(0, 20).forEach((paper, index) => {
      let paperLine = `  ${index + 1}. [ID:${paper.id || 'N/A'}] ${paper.title || '无标题'}`;
      if (paper.id && paper.id.includes('.')) {
        paperLine += ` <br>&nbsp;&nbsp;&nbsp;&nbsp;【点击预览：<a href="https://arxiv.org/abs/${paper.id}" target="_blank" style="color: #0066cc; text-decoration: none;">https://arxiv.org/abs/${paper.id}</a>】`;
      }
      result += paperLine + '<br>';
    });
    if (author.papers.length > 20) {
      result += `  ...等${author.papers.length - 20}篇更多论文<br>`;
    }
  } else {
    result += `相关论文: 无<br>`;
  }
  return result;
}
function formatCategory(category) {
  if (!category) return "未找到分类信息。";
  
  let result = `<strong>--- 分类信息 ---</strong><br>`;
  result += `分类名称: ${category.name || 'N/A'}<br>`;
  
  if (category.papers && category.papers.length > 0) {
    result += `包含论文 (${category.papers.length}篇):<br>`;
    category.papers.slice(0, 20).forEach((paper, index) => {
      let paperLine = `  ${index + 1}. [ID:${paper.id || 'N/A'}] ${paper.title || '无标题'}`;
      if (paper.id && paper.id.includes('.')) {
        paperLine += ` <br>&nbsp;&nbsp;&nbsp;&nbsp;【点击预览：<a href="https://arxiv.org/abs/${paper.id}" target="_blank" style="color: #0066cc; text-decoration: none;">https://arxiv.org/abs/${paper.id}</a>】`;
      }
      result += paperLine + '<br>';
    });
    if (category.papers.length > 20) {
      result += `  ...等${category.papers.length - 20}篇更多论文<br>`;
    }
  } else {
    result += `包含论文: 无<br>`;
  }
  
  return result;
}
// 在 searchKeyword 函数中添加调试
function searchKeyword(query, page = 1, pageSize = 20) {
  const url = `${API_BASE}/papers/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`;
  
  console.log('搜索URL:', url);
  
  fetch(url)
      .then(response => {
          console.log('响应状态:', response.status);
          return response.json();
      })
      .then(data => {
          console.log('完整响应:', data); // 查看完整响应结构
          console.log('data.data:', data.data);
          console.log('data.data.papers:', data.data?.papers);
          console.log('data.data.pagination:', data.data?.pagination);
          
          if (data.success) {
              const resultBox = document.getElementById('queryResult');
              displayKeywordResults(data, query, resultBox);
          } else {
              alert('搜索失败: ' + (data.error || '未知错误'));
          }
      })
      .catch(error => {
          console.error('Error:', error);
          alert('搜索失败');
      });
}
function displayKeywordResults(data, query, resultBox) {
  // 确保数据结构正确
  if (!data || !data.data) {
      resultBox.innerHTML = "响应数据格式错误";
      return;
  }
  
  const papers = data.data.papers || data.data; // 兼容两种可能的结构
  const pagination = data.data.pagination;
  
  console.log('papers数组:', papers);
  console.log('pagination:', pagination);
  
  if (papers && papers.length > 0) {
      let result = `<strong>关键词"${query}"搜索到 ${papers.length} 篇相关论文`;
      
      // 如果有分页信息，显示分页详情
      if (pagination) {
          const totalPages = Math.ceil(pagination.total / pagination.page_size);
          result += ` (第${pagination.page}页，共${totalPages}页)`;
      }
      
      result += `:</strong><br><br>`;
      
      papers.forEach((paper, index) => {
          console.log('处理论文:', paper); // 调试每个论文对象
          
          const highlightedPaper = {
              ...paper,
              title: highlightKeywords(paper.title || '', query),
              abstract: highlightKeywords(paper.abstract || '', query)
          };
          result += `${index + 1}. ${formatPaper(highlightedPaper)}<br>`;
      });
      
      // 添加分页导航（如果有分页信息）
      if (pagination) {
          const totalPages = Math.ceil(pagination.total / pagination.page_size);
          result += `<br><div style="margin-top: 15px;">`;
          if (pagination.page > 1) {
              result += `<button onclick="searchKeyword('${query}', ${pagination.page - 1}, ${pagination.page_size})" style="margin-right: 10px; padding: 5px 10px;">上一页</button>`;
          }
          if (pagination.page < totalPages) {
              result += `<button onclick="searchKeyword('${query}', ${pagination.page + 1}, ${pagination.page_size})" style="padding: 5px 10px;">下一页</button>`;
          }
          result += `</div>`;
      }
      
      resultBox.innerHTML = result;
  } else {
      resultBox.innerHTML = "未找到相关论文";
  }
}
// 高亮显示匹配的关键词（修复版）
// 加粗显示匹配的关键词
function highlightKeywords(text, keyword) {
  if (!text || !keyword) return text;
  
  // 转义正则表达式特殊字符
  const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escapedKeyword})`, 'gi');
  
  return text.replace(regex, '<strong>$1</strong>');
}
//查询主函数
async function search() {
  const searchType = document.getElementById("searchType").value;
  const query = document.getElementById("queryInput").value.trim();
  const resultBox = document.getElementById("queryResult");

  if (!query) {
    resultBox.innerHTML = "查询内容不能为空！";
    return;
  }

  try {
    let url;
    switch (searchType) {
      case "paper_id":
        url = `${API_BASE}/papers/${encodeURIComponent(query)}`;
        break;
      case "author":
        url = `${API_BASE}/authors/${encodeURIComponent(query)}`;
        break;
      case "category":
        url = `${API_BASE}/categories/${encodeURIComponent(query)}`;
        break;
      case "keyword":
        // 使用带分页参数的搜索函数
        searchKeyword(query);
        return; // 直接返回，因为 searchKeyword 会异步处理
      default:
        resultBox.innerHTML = "请选择有效的搜索类型！";
        return;
    }

    console.log(`搜索类型: ${searchType}, URL: ${url}`);
    let res = await fetch(url);
    
    if (res.ok) {
      let data = await res.json();
      if (data.success) {
        switch (searchType) {
          case "paper_id":
            resultBox.innerHTML = formatPaper(data.data);
            break;
          case "author":
            resultBox.innerHTML = formatAuthor(data.data);
            break;
          case "category":
            resultBox.innerHTML = formatCategory(data.data);
            break;
        }
        return;
      }
    }

    // 如果请求不成功
    const errorText = await res.text();
    resultBox.innerHTML = `查询失败: ${res.status} ${res.statusText}<br>错误信息: ${errorText}`;
    
  } catch (err) {
    resultBox.innerHTML = "查询失败: " + err.message;
    console.error("查询错误:", err);
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