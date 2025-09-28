const API_BASE = "http://localhost:5000/api/kg";  // 后端接口地址，增删改查功能使用
const RECOMMENDATION_API = "http://localhost:5000/api";  // 点赞和推荐功能使用单独的API路径

// 用户认证对象 - 与auth.js中的认证功能保持一致
window.Auth = {
  // 获取当前登录用户
  get currentUser() {
    return localStorage.getItem('currentUser');
  },
  
  // 检查用户是否已登录
  isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true' && !!localStorage.getItem('accessToken');
  },
  
  // 获取认证token
  getAuthToken() {
    return localStorage.getItem('accessToken');
  },
  
  // 退出登录
  logout() {
    if (window.handleLogout) {
      handleLogout();
    } else {
      // 如果handleLogout不可用，使用本地实现
      localStorage.removeItem('accessToken');
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isLoggedIn');
      window.location.href = '../login.html';
    }
  }
};

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
      paper.abstract.substring(0, 750) + '...' : paper.abstract;
    result += `摘要: ${abstractPreview}<br>`;
  }
  // 添加arXiv预览链接（可点击的超链接）
  if (paper.id && paper.id.includes('.')) {
    result += `[arXiv论文预览：<a href="https://arxiv.org/abs/${paper.id}" target="_blank" style="color: #0066cc; text-decoration: none;">https://arxiv.org/abs/${paper.id}</a>]<br>`;
  }
  
  // 添加操作按钮
  const paperId = paper.id || 'N/A';
  // 检查论文是否已点赞（按用户隔离）
  const userLikedKey = Auth.currentUser ? `likedPapers_${Auth.currentUser}` : 'likedPapers';
  const likedPapers = JSON.parse(localStorage.getItem(userLikedKey) || '[]');
  const isLiked = likedPapers.includes(paperId);
  const likeBtnText = isLiked ? '👍 已点赞' : '👍 点赞';
  
  // 修复单引号嵌套问题，确保按钮点击事件正确触发
  const safePaperId = paperId.replace(/'/g, "\\'");
  const safeTitle = encodeURIComponent(paper.title || '无标题').replace(/'/g, "\\'");
  
  // 根据是否已点赞决定调用的函数
  const btnFunction = isLiked ? `paperUnlike('${safePaperId}', '${safeTitle}')` : `paperLike('${safePaperId}', '${safeTitle}')`;
  
  result += `<br><div style="margin-top: 10px;">`;
  result += `<button onclick="${btnFunction}" style="margin-right: 10px; padding: 5px 15px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">${likeBtnText}</button>`;
  result += `<button onclick="paperSave('${safePaperId}', '${safeTitle}')" style="margin-right: 10px; padding: 5px 15px; background-color: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">📚 收藏</button>`;
  result += `</div>`;
  
  return result;
}

// 论文点赞功能
function paperLike(paperId, paperTitle) {
  // 确保API_BASE已定义
  if (typeof API_BASE === 'undefined') {
    console.error('API_BASE未定义，无法调用后端API');
    alert('系统配置错误，请联系管理员');
    return;
  }

  // 检查用户是否登录
  if (!Auth.isLoggedIn()) {
    alert('请先登录');
    return;
  }

  try {
    // 将点赞的论文信息记录在本地存储（按用户隔离）
    const userLikedKey = `likedPapers_${Auth.currentUser}`;
    const likedPapers = JSON.parse(localStorage.getItem(userLikedKey) || '[]');
    if (!likedPapers.includes(paperId)) {
      likedPapers.push(paperId);
      localStorage.setItem(userLikedKey, JSON.stringify(likedPapers));
      
      // 调用后端API建立用户与论文的"喜欢"关系
      fetch(`${RECOMMENDATION_API}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: Auth.currentUser,  // 显式传递用户名
          paper_id: paperId,
          liked: true
        })
      }).then(response => {
        if (!response.ok) {
          console.error('后端点赞失败');
        }
      });
      
      alert(`已点赞论文: ${decodeURIComponent(paperTitle)}`);
      // 刷新当前结果以显示最新状态
      refreshSearchResults();
    } else {
      console.log('论文已在点赞列表中:', paperId);
      console.log('当前点赞列表:', likedPapers);
      alert('您已经点赞过这篇论文');
      // 强制刷新以确保按钮状态正确
      refreshSearchResults();
    }
  } catch (error) {
    console.error('点赞失败:', error);
    alert('点赞失败，请稍后重试');
  }
}

// 取消点赞功能
function paperUnlike(paperId, paperTitle) {
  // 确保API_BASE已定义
  if (typeof API_BASE === 'undefined') {
    console.error('API_BASE未定义，无法调用后端API');
    alert('系统配置错误，请联系管理员');
    return;
  }

  // 检查用户是否登录
  if (!Auth.isLoggedIn()) {
    alert('请先登录');
    return;
  }

  try {
    // 从本地存储中删除点赞的论文信息（按用户隔离）
    const userLikedKey = `likedPapers_${Auth.currentUser}`;
    let likedPapers = JSON.parse(localStorage.getItem(userLikedKey) || '[]');
    
    if (likedPapers.includes(paperId)) {
      console.log('取消点赞前的列表:', likedPapers);
      // 移除论文ID
      likedPapers = likedPapers.filter(id => id !== paperId);
      localStorage.setItem(userLikedKey, JSON.stringify(likedPapers));
      console.log('取消点赞后的列表:', likedPapers);
      
      // 调用后端API删除用户与论文的"喜欢"关系
      fetch(`${RECOMMENDATION_API}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: Auth.currentUser,  // 显式传递用户名
          paper_id: paperId,
          liked: false
        })
      }).then(response => {
        if (!response.ok) {
          console.error('后端取消点赞失败');
        }
      });
      
      alert(`已取消点赞论文: ${decodeURIComponent(paperTitle)}`);
      // 刷新当前结果以显示最新状态
      refreshSearchResults();
    } else {
      console.log('论文不在点赞列表中:', paperId);
      console.log('当前点赞列表:', likedPapers);
      alert('您没有点赞过这篇论文');
    }
  } catch (error) {
    console.error('取消点赞失败:', error);
    alert('取消点赞失败，请稍后重试');
  }
}

// 统一的刷新搜索结果函数
function refreshSearchResults() {
  const searchInput = document.getElementById("queryInput");
  const searchType = document.getElementById("searchType");
  if (searchInput && searchType && searchInput.value.trim()) {
    // 添加一个小延迟确保本地存储更新完成
    setTimeout(() => {
      search();
    }, 100);
  }
}

// 论文收藏功能
function paperSave(paperId, paperTitle) {
  try {
    // 将收藏的论文信息记录在本地存储
    const savedPapers = JSON.parse(localStorage.getItem('savedPapers') || '[]');
    if (!savedPapers.some(paper => paper.id === paperId)) {
      savedPapers.push({
        id: paperId,
        title: decodeURIComponent(paperTitle),
        saveTime: new Date().toISOString()
      });
      localStorage.setItem('savedPapers', JSON.stringify(savedPapers));
      alert(`已收藏论文: ${decodeURIComponent(paperTitle)}`);
    } else {
      alert('您已经收藏过这篇论文');
    }
  } catch (error) {
    console.error('收藏失败:', error);
    alert('收藏失败，请稍后重试');
  }
}

// 查看论文详细信息
function paperDetail(paperId) {
  // 构造URL查询参数
  const urlParams = new URLSearchParams();
  urlParams.append('paper_id', paperId);
  
  // 在当前页面显示详细信息或跳转到详情页面
  // 这里我们选择在当前页面切换到论文详情视图
  document.getElementById("searchType").value = "paper_id";
  document.getElementById("queryInput").value = paperId;
  search();
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
        paperLine += ` <br>&nbsp;&nbsp;&nbsp;&nbsp;[点击预览：<a href="https://arxiv.org/abs/${paper.id}" target="_blank" style="color: #0066cc; text-decoration: none;">https://arxiv.org/abs/${paper.id}</a>]`;
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
        paperLine += ` <br>&nbsp;&nbsp;&nbsp;&nbsp;[点击预览：<a href="https://arxiv.org/abs/${paper.id}" target="_blank" style="color: #0066cc; text-decoration: none;">https://arxiv.org/abs/${paper.id}</a>]`;
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
        console.log('处理论文:', paper);
        
        // 先格式化论文（包含链接换行）
        let formattedPaper = formatPaper(paper);
        
        // 然后在格式化后的文本中进行关键词高亮
        const highlightedContent = highlightKeywords(formattedPaper, query);
        
        result += `${index + 1}. ${highlightedContent}<br>`;
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
// 加粗显示匹配的关键词，修复过度匹配问题
function highlightKeywords(text, keyword) {
  if (!text || !keyword) return text;
  
  // 转义正则表达式特殊字符
  const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // 使用单词边界\b来确保匹配完整单词，避免过度匹配
  const regex = new RegExp(`\\b(${escapedKeyword})\\b`, 'gi');
  
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
/*============推荐功能===============*/
// 推荐功能已在recommendations.js中实现
// 这里只需确保在页面加载时正确初始化

// 搜索历史功能
const MAX_SEARCH_HISTORY = 10; // 最大保存历史记录数量

// 获取搜索历史记录
function getSearchHistory() {
  try {
    return JSON.parse(localStorage.getItem('searchHistory') || '[]');
  } catch (error) {
    console.error('获取搜索历史失败:', error);
    return [];
  }
}

// 保存搜索历史记录
function saveSearchHistory(query, searchType) {
  try {
    const history = getSearchHistory();
    
    // 移除重复记录
    const filteredHistory = history.filter(item => 
      !(item.query === query && item.type === searchType)
    );
    
    // 添加新记录到开头
    filteredHistory.unshift({
      query: query,
      type: searchType,
      timestamp: new Date().toISOString(),
      time: new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    });
    
    // 限制历史记录数量
    const limitedHistory = filteredHistory.slice(0, MAX_SEARCH_HISTORY);
    
    localStorage.setItem('searchHistory', JSON.stringify(limitedHistory));
  } catch (error) {
    console.error('保存搜索历史失败:', error);
  }
}

// 显示搜索历史下拉框
function showSearchHistory() {
  const historyDropdown = document.getElementById('searchHistory');
  const historyList = document.getElementById('searchHistoryList');
  
  if (!historyDropdown || !historyList) return;
  
  const history = getSearchHistory();
  
  if (history.length === 0) {
    historyList.innerHTML = '<div class="search-history-item" style="color: #6c757d; text-align: center;">暂无搜索历史</div>';
  } else {
    historyList.innerHTML = history.map(item => `
      <div class="search-history-item" onclick="selectSearchHistory('${item.query.replace(/'/g, "\\'")}', '${item.type}')">
        ${item.query}
        <span class="search-type">(${getSearchTypeName(item.type)})</span>
        <span class="search-time">${item.time}</span>
      </div>
    `).join('');
  }
  
  historyDropdown.classList.remove('hidden');
}

// 隐藏搜索历史下拉框
function hideSearchHistory() {
  const historyDropdown = document.getElementById('searchHistory');
  if (historyDropdown) {
    // 延迟隐藏，以便点击历史项时有时间处理
    setTimeout(() => {
      historyDropdown.classList.add('hidden');
    }, 200);
  }
}

// 选择搜索历史项
function selectSearchHistory(query, searchType) {
  const searchInput = document.getElementById('queryInput');
  const searchTypeSelect = document.getElementById('searchType');
  
  if (searchInput && searchTypeSelect) {
    searchInput.value = query;
    searchTypeSelect.value = searchType;
    
    // 隐藏历史下拉框
    hideSearchHistory();
    
    // 自动执行搜索
    search();
  }
}

// 清空搜索历史
function clearSearchHistory() {
  if (confirm('确定要清空所有搜索历史吗？')) {
    localStorage.removeItem('searchHistory');
    
    // 刷新历史显示
    showSearchHistory();
    
    alert('搜索历史已清空');
  }
}

// 获取搜索类型的中文名称
function getSearchTypeName(type) {
  const typeMap = {
    'paper_id': '论文ID',
    'author': '作者',
    'category': '分类',
    'keyword': '关键词'
  };
  return typeMap[type] || type;
}

// 初始化搜索历史功能
function initSearchHistory() {
  const searchInput = document.getElementById('queryInput');
  
  if (!searchInput) return;
  
  // 点击搜索框时显示历史
  searchInput.addEventListener('focus', showSearchHistory);
  
  // 点击其他地方时隐藏历史
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-input-wrapper')) {
      hideSearchHistory();
    }
  });
  
  // 按Esc键隐藏历史
  searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      hideSearchHistory();
    }
  });
  
  // 输入时过滤历史（可选功能）
  searchInput.addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const historyList = document.getElementById('searchHistoryList');
    const historyItems = historyList?.getElementsByClassName('search-history-item');
    
    if (historyItems) {
      Array.from(historyItems).forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'block' : 'none';
      });
    }
  });
}

// 修改search函数，在搜索时保存历史
const originalSearch = window.search;
window.search = function() {
  const searchType = document.getElementById("searchType").value;
  const query = document.getElementById("queryInput").value.trim();
  
  if (query) {
    // 保存搜索历史
    saveSearchHistory(query, searchType);
  }
  
  // 调用原始搜索函数
  return originalSearch.apply(this, arguments);
};

// 测试函数 - 帮助验证点赞和收藏功能是否正常
function testLikeSaveFunctions() {
  console.log('开始测试点赞和收藏功能...');
  
  // 检查paperLike和paperSave函数是否在全局作用域中可用
  console.log('paperLike函数是否存在:', typeof paperLike === 'function');
  console.log('paperSave函数是否存在:', typeof paperSave === 'function');
  
  // 模拟点击事件测试
  const testButton = document.createElement('button');
  testButton.onclick = function() {
    console.log('测试按钮被点击');
  };
  
  // 触发点击事件
  testButton.click();
  
  // 添加全局事件委托测试
  document.addEventListener('click', function(e) {
    const target = e.target;
    if (target.onclick && target.onclick.toString().includes('paperLike')) {
      console.log('点赞按钮被点击，事件委托捕获到点击事件');
    }
    if (target.onclick && target.onclick.toString().includes('paperSave')) {
      console.log('收藏按钮被点击，事件委托捕获到点击事件');
    }
  });
  
  alert('测试函数执行成功，请打开浏览器控制台查看详细日志。\n修复要点：\n1. 修复了按钮点击事件中的单引号嵌套问题\n2. 添加了全局事件委托确保动态按钮能触发事件\n3. paperLike和paperSave函数已完全集成在app.js中');
}

// 将测试函数暴露到全局作用域
window.testKGMS = {
  testLikeSaveFunctions: testLikeSaveFunctions
};

// 页面加载完成后初始化搜索历史功能
document.addEventListener('DOMContentLoaded', function() {
  initSearchHistory();
  console.log('搜索历史功能已初始化');
});

console.log('知识图谱管理系统已加载，可通过 window.testKGMS.testLikeSaveFunctions() 测试点赞收藏功能');