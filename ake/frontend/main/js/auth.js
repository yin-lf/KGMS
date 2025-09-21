// API基础URL - 根据实际后端地址修改
const API_BASE_URL = 'http://localhost:5000/api';

// 登录验证函数 - 现在使用真实API
async function validateLogin(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            // 存储token和用户信息
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('currentUser', username);
            localStorage.setItem('isLoggedIn', 'true');
            return true;
        } else {
            const errorData = await response.json();
            console.error('登录失败:', errorData.message);
            return false;
        }
    } catch (error) {
        console.error('登录请求错误:', error);
        return false;
    }
}

// 注册函数
async function registerUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            const data = await response.json();
            return { success: true, message: '注册成功' };
        } else {
            const errorData = await response.json();
            return { success: false, message: errorData.message || '注册失败' };
        }
    } catch (error) {
        console.error('注册请求错误:', error);
        return { success: false, message: '网络错误，请稍后重试' };
    }
}

// 显示主应用界面 - 保持页面跳转
function showMainApp() {
    // 跳转到主页面
    window.location.href = 'main/main.html';
}

// 处理登录表单提交
async function handleLoginSubmit(event) {
    event.preventDefault();
    
    const username = document.getElementById('usernameIn').value;
    const password = document.getElementById('passwordIn').value;
    
    // 显示加载状态
    const loginBtn = document.querySelector('#loginForm button[type="submit"]');
    const originalText = loginBtn.textContent;
    loginBtn.textContent = '登录中...';
    loginBtn.disabled = true;
    
    const isValid = await validateLogin(username, password);
    
    // 恢复按钮状态
    loginBtn.textContent = originalText;
    loginBtn.disabled = false;
    
    if (isValid) {
        // 切换到主应用
        showMainApp();
    } else {
        alert('用户名或密码错误！');
    }
}

// 处理注册表单提交
async function handleSignupSubmit(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const fullname = document.getElementById('truename').value;
    
    // 显示加载状态
    const signupBtn = document.querySelector('#signupForm button[type="submit"]');
    const originalText = signupBtn.textContent;
    signupBtn.textContent = '注册中...';
    signupBtn.disabled = true;
    
    const result = await registerUser({ username, password, fullname });
    
    // 恢复按钮状态
    signupBtn.textContent = originalText;
    signupBtn.disabled = false;
    
    if (result.success) {
        alert(result.message);
        // 自动填充登录表单并切换到登录
        document.getElementById('usernameIn').value = username;
        document.getElementById('passwordIn').value = password;
        toggleForm();
    } else {
        alert(result.message);
    }
}

// 切换登录/注册表单
function toggleForm() {
    const forms = document.querySelectorAll('.panel_content');
    forms.forEach(form => {
        form.classList.toggle('panel_content-overlay');
    });
}

// 退出登录
function handleLogout() {
    // 清除本地存储的认证信息
    localStorage.removeItem('accessToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('isLoggedIn');
    
    // 跳转回登录页面
    window.location.href = '../login.html';
}

// 获取认证token
function getAuthToken() {
    return localStorage.getItem('accessToken');
}

// 检查请求是否需要认证
function checkAuth() {
    const token = getAuthToken();
    if (!token) {
        handleLogout();
        return false;
    }
    return true;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查当前页面是否是主应用页面
    const isMainPage = window.location.pathname.includes('main.html');
    
    if (isMainPage) {
        // 在主应用页面，检查登录状态
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        const token = getAuthToken();
        
        if (!isLoggedIn || !token) {
            // 未登录，跳转回登录页面
            window.location.href = 'login.html';
        } else {
            // 已登录，更新用户信息显示
            const currentUser = localStorage.getItem('currentUser');
            const userInfoElement = document.getElementById('userInfo');
            if (userInfoElement) {
                userInfoElement.textContent = `欢迎, ${currentUser}`;
            }
            
            // 添加退出按钮事件监听
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', handleLogout);
            }
        }
    } else {
        // 在登录页面，添加事件监听器
        const signupForm = document.getElementById('signupForm');
        const loginForm = document.getElementById('loginForm');
        
        if (signupForm) {
            signupForm.addEventListener('submit', handleSignupSubmit);
        }
        if (loginForm) {
            loginForm.addEventListener('submit', handleLoginSubmit);
        }
        
        document.querySelectorAll('.js-formToggle').forEach(button => {
            button.addEventListener('click', toggleForm);
        });
        
        // 检查是否已登录，如果已登录则直接跳转到主应用
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        const token = getAuthToken();
        if (isLoggedIn && token) {
            showMainApp();
        }
    }
});