// recommendations.js

// 获取推荐论文（个性化推荐）
async function getRecommendations() {
    if (!Auth.currentUser) {
        alert('请先登录以获取个性化推荐');
        return;
    }

    try {
        // 显示加载状态
        const container = document.getElementById('recommendationList');
        if (container) {
            container.innerHTML = '<div class="loading">正在生成个性化推荐...</div>';
        }

        console.log('开始获取推荐论文，用户:', Auth.currentUser);
        container.innerHTML = '<div class="loading">开始获取推荐论文，用户:</div>';
        const response = await fetch(`${API_BASE}/recommendations?username=${encodeURIComponent(Auth.currentUser)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log('推荐API响应状态:', response.status);

        if (!response.ok) {
            let errorMessage = `HTTP错误! 状态: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                // 忽略JSON解析错误
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        console.log('获取到推荐论文:', data);

        if (data.success) {
            renderRecommendations(data.data);
            
            // 更新标题
            const titleElement = document.getElementById('recommendationTitle');
            if (titleElement) {
                titleElement.textContent = '为您推荐的论文';
            }
            
            // 隐藏推荐按钮，显示刷新按钮
            const recommendBtn = document.getElementById('getRecommendationsBtn');
            const refreshBtn = document.getElementById('refreshRecommendationsBtn');
            if (recommendBtn) recommendBtn.style.display = 'none';
            if (refreshBtn) refreshBtn.style.display = 'block';
        } else {
            alert('获取推荐失败: ' + (data.message || '请稍后重试'));
            getRandomPapers();
        }
        
    } catch (error) {
        console.error('获取推荐论文失败:', error);
        alert('获取推荐失败，请检查网络连接');
        getRandomPapers();
    }
}

// 获取随机论文（用于未登录用户或推荐失败时）
async function getRandomPapers() {
    try {
        console.log('开始获取随机论文');
        
        const response = await fetch(`${API_BASE}/papers/random?limit=3`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('随机论文API响应状态:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                renderRecommendations(data.data);
                
                // 更新标题（如果是未登录状态）
                if (!Auth.currentUser) {
                    const titleElement = document.getElementById('recommendationTitle');
                    if (titleElement) {
                        titleElement.textContent = '热门论文';
                    }
                }
                return;
            }
        }
        
        // 如果API调用失败，显示模拟数据
        showMockPapers();
        
    } catch (error) {
        console.error('获取随机论文失败:', error);
        showMockPapers();
    }
}

// 显示模拟的假论文数据
function showMockPapers() {
    console.log('显示模拟论文数据');
    
    const mockPapers = [
        {
            id: 'mock-001',
            title: '深度学习在自然语言处理中的应用',
            authors: ['张明', '李华', '王强'],
            category: '人工智能',
            abstract: '本文探讨了深度学习技术在自然语言处理领域的应用，包括文本分类、情感分析和机器翻译等任务。'
        },
        {
            id: 'mock-002',
            title: '基于区块链的数据安全存储方案',
            authors: ['刘伟', '赵芳'],
            category: '区块链',
            abstract: '提出了一种基于区块链技术的数据安全存储方案，利用分布式账本和智能合约确保数据的不可篡改性和可追溯性。'
        },
        {
            id: 'mock-003',
            title: '云计算环境下的资源调度优化算法',
            authors: ['陈晓', '杨光', '黄磊'],
            category: '云计算',
            abstract: '针对云计算环境中的资源调度问题，提出了一种基于深度强化学习的优化算法。'
        }
    ];
    
    // 更新标题（如果是未登录状态）
    if (!Auth.currentUser) {
        const titleElement = document.getElementById('recommendationTitle');
        if (titleElement) {
            titleElement.textContent = '热门论文';
        }
    }
    
    renderRecommendations(mockPapers);
}

// 获取"大家在看"的热门论文
async function getTrendingPapers() {
    try {
        console.log('开始获取热门论文');
        
        const response = await fetch(`${API_BASE}/papers/trending?limit=5`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('热门论文API响应状态:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                renderTrendingPapers(data.data);
                return;
            }
        }
        
        // 如果API调用失败，显示模拟数据
        showMockTrendingPapers();
        
    } catch (error) {
        console.error('获取热门论文失败:', error);
        showMockTrendingPapers();
    }
}

// 显示模拟的热门论文
function showMockTrendingPapers() {
    console.log('显示模拟热门论文数据');
    
    const mockTrendingPapers = [
        { id: 'mock-trend-001', title: '人工智能在医疗诊断中的应用进展', authors: ['吴医生', '郑教授'] },
        { id: 'mock-trend-002', title: '5G通信技术的安全挑战与对策', authors: ['钱工程师', '周博士'] },
        { id: 'mock-trend-003', title: '量子计算的最新突破与前景', authors: ['林教授', '朱研究员'] },
        { id: 'mock-trend-004', title: '自动驾驶系统的感知与决策算法', authors: ['赵工程师', '孙博士'] },
        { id: 'mock-trend-005', title: '边缘计算在物联网中的应用研究', authors: ['刘教授', '陈博士'] }
    ];
    
    renderTrendingPapers(mockTrendingPapers);
}

// 渲染推荐论文列表
function renderRecommendations(papers) {
    const container = document.getElementById('recommendationList');
    if (!container) return;

    container.innerHTML = '';

    if (!papers || papers.length === 0) {
        container.innerHTML = '<p>暂无推荐论文，请尝试浏览更多内容</p>';
        return;
    }

    papers.forEach(paper => {
        const paperElement = document.createElement('div');
        paperElement.className = 'paper-card';
        paperElement.innerHTML = `
            <h4>${paper.title || '无标题'}</h4>
            <p><strong>作者:</strong> ${paper.authors ? paper.authors.join(', ') : '未知作者'}</p>
            <p><strong>分类:</strong> ${paper.category || '未分类'}</p>
            <p>${paper.abstract ? paper.abstract.substring(0, 100) + '...' : '暂无摘要'}</p>
            <div class="paper-actions">
                <button onclick="likePaper('${paper.id}')" class="like-btn">👍 点赞</button>
                <button onclick="viewPaperDetails('${paper.id}')" class="view-btn">查看详情</button>
            </div>
        `;
        container.appendChild(paperElement);
    });
}

// 渲染"大家在看"的热门论文
function renderTrendingPapers(papers) {
    const container = document.getElementById('trendingList');
    const section = document.getElementById('trendingSection');

    if (!container || !section) return;

    container.innerHTML = '';

    if (!papers || papers.length === 0) {
        container.innerHTML = '<p>暂无热门论文</p>';
        return;
    }

    papers.forEach((paper, index) => {
        const paperElement = document.createElement('div');
        paperElement.className = 'trending-paper-item';
        paperElement.innerHTML = `
            <span class="trending-rank">${index + 1}</span>
            <div class="trending-info">
                <h5>${paper.title || '无标题'}</h5>
                <p>${paper.authors ? paper.authors.slice(0, 2).join(', ') : '未知作者'}</p>
            </div>
            <button onclick="viewPaperDetails('${paper.id}')" class="trending-view-btn">查看</button>
        `;
        container.appendChild(paperElement);
    });
}

// 点赞论文
async function likePaper(paperId) {
    if (!Auth.currentUser) {
        alert('请先登录');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/recommendations/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: Auth.currentUser,
                paper_id: paperId,
                liked: true
            })
        });
        
        if (response.ok) {
            console.log('已点赞论文:', paperId);
            alert('点赞成功！');
        } else {
            throw new Error(`点赞失败: ${response.status}`);
        }
    } catch (error) {
        console.error('点赞失败:', error);
        alert('点赞失败，请稍后重试');
    }
}

// 查看论文详情
function viewPaperDetails(paperId) {
    console.log('查看论文详情:', paperId);
    // 这里可以跳转到详情页面或显示模态框
    alert(`查看论文详情: ${paperId}\n实际应用中这里会跳转到详情页面`);
}

// 刷新推荐
async function refreshRecommendations() {
    if (!Auth.currentUser) {
        alert('请先登录');
        return;
    }
    getRecommendations();
}

// 更新推荐按钮显示状态
function updateRecommendationButton() {
    const recommendBtn = document.getElementById('getRecommendationsBtn');
    const refreshBtn = document.getElementById('refreshRecommendationsBtn');
    
    if (recommendBtn) {
        recommendBtn.style.display = Auth.currentUser ? 'block' : 'none';
    }
    
    if (refreshBtn) {
        refreshBtn.style.display = 'none';
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('推荐系统初始化');
    
    // 获取推荐论文
    if (document.getElementById('recommendationList')) {
        if (Auth.currentUser) {
            getRecommendations();
        } else {
            getRandomPapers();
        }
    }
    
    // 获取热门论文
    if (document.getElementById('trendingList')) {
        getTrendingPapers();
    }
    
    updateRecommendationButton();
});

// 监听登录事件
document.addEventListener('userLoggedIn', function() {
    console.log('用户登录，刷新推荐');
    if (document.getElementById('recommendationList')) {
        getRecommendations();
    }
    if (document.getElementById('trendingList')) {
        getTrendingPapers();
    }
    updateRecommendationButton();
});

// 监听登出事件
document.addEventListener('userLoggedOut', function() {
    console.log('用户登出，显示随机论文');
    if (document.getElementById('recommendationList')) {
        getRandomPapers();
    }
    updateRecommendationButton();
    
    // 隐藏刷新按钮
    const refreshBtn = document.getElementById('refreshRecommendationsBtn');
    if (refreshBtn) {
        refreshBtn.style.display = 'none';
    }
});