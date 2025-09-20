const Auth = {
    currentUser: null,
    
    // 初始化函数
    init: function() {
        // 检查本地存储中是否有已登录用户
        const savedUser = localStorage.getItem('username');
        if (savedUser) {
            this.currentUser = savedUser;
            this.updateUI();
        }
        
        // 添加事件监听器
        document.querySelector('#authBar button[onclick="Auth.showLoginModal()"]')
            .addEventListener('click', () => this.showLoginModal());
        document.querySelector('#authBar button[onclick="Auth.logout()"]')
            .addEventListener('click', () => this.logout());
        
        // 添加模态框事件监听
        const modal = document.getElementById('loginModal');
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideLoginModal();
            }
        });
        
        // 添加回车键登录支持
        document.getElementById('usernameInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.login();
            }
        });
    },
    
    // 显示登录模态框
    showLoginModal: function() {
        document.getElementById('loginModal').style.display = 'flex';
        document.getElementById('usernameInput').focus();
    },
    
    // 隐藏登录模态框
    hideLoginModal: function() {
        document.getElementById('loginModal').style.display = 'none';
        document.getElementById('usernameInput').value = '';
    },
    
    // 登录功能
    login: function() {
        const usernameInput = document.getElementById('usernameInput');
        const username = usernameInput.value.trim();
        
        if (!username) {
            alert('请输入用户名');
            return;
        }
        
        // 模拟后端验证成功
        this.currentUser = username;
        localStorage.setItem('username', username);
        
        this.hideLoginModal();
        this.updateUI();
        
        // 触发登录成功事件，让其他模块响应
        this.triggerLoginEvent();
    },
    
    // 退出登录
    logout: function() {
        this.currentUser = null;
        localStorage.removeItem('username');
        this.updateUI();
        
        // 触发退出事件
        this.triggerLogoutEvent();
    },
    
    // 更新UI状态
    updateUI: function() {
        const userInfo = document.getElementById('userInfo');
        const loginBtn = document.querySelector('#authBar button[onclick="Auth.showLoginModal()"]');
        const logoutBtn = document.querySelector('#authBar button[onclick="Auth.logout()"]');
        const viewLikedBtn = document.querySelector('.view-liked-btn');
        
        if (this.currentUser) {
            userInfo.textContent = `欢迎，${this.currentUser}`;
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'inline-block';
            // 关键修复：登录后显示"我的喜欢"按钮
            if (viewLikedBtn) {
                viewLikedBtn.style.display = 'inline-block';
            }
        } else {
            userInfo.textContent = '未登录';
            loginBtn.style.display = 'inline-block';
            logoutBtn.style.display = 'none';
            // 退出登录后隐藏"我的喜欢"按钮
            if (viewLikedBtn) {
                viewLikedBtn.style.display = 'none';
            }
        }
    },
    
    // 触发登录事件（供其他模块使用）
    triggerLoginEvent: function() {
        const event = new CustomEvent('userLoggedIn', {
            detail: { username: this.currentUser }
        });
        document.dispatchEvent(event);
    },
    
    // 触发退出事件（供其他模块使用）
    triggerLogoutEvent: function() {
        const event = new Event('userLoggedOut');
        document.dispatchEvent(event);
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    Auth.init();
});