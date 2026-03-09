# 用户认证 API 使用文档

## 📋 API 列表

### 1. 用户注册

**接口地址**: `POST /api/auth/register/`

**请求数据**:
```json
{
    "username": "zhangsan",
    "password": "password123",
    "password_confirm": "password123",
    "real_name": "张三",
    "role": "student",
    "email": "zhangsan@example.com"
}
```

**字段说明**:
- `username`: 用户名（必填，3-150 字符，不能重复）
- `password`: 密码（必填，至少 6 个字符）
- `password_confirm`: 确认密码（必填，必须与 password 一致）
- `real_name`: 真实姓名（必填）
- `role`: 角色（必填，可选值：`student` 或 `teacher`）
- `email`: 邮箱（可选）

**成功响应** (201 Created):
```json
{
    "id": 2,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "first_name": "",
    "last_name": "",
    "profile": {
        "role": "student",
        "real_name": "张三",
        "avatar": "",
        "phone": ""
    },
    "message": "注册成功"
}
```

**失败响应** (400 Bad Request):
```json
{
    "username": ["该用户名已存在。"],
    "password_confirm": ["两次输入的密码不一致"]
}
```

---

### 2. 用户登录

**接口地址**: `POST /api/auth/login/`

**请求数据**:
```json
{
    "username": "zhangsan",
    "password": "password123"
}
```

**成功响应** (200 OK):
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwMDAwMDAwMCwiaWF0IjoxNjk5MDAwMDAwLCJqdGkiOiJhYmNkMTIzNCIsInVzZXJfaWQiOjJ9.abc123",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzAwMDAwMDAwLCJpYXQiOjE2OTkwMDAwMDAsImp0aSI6ImFiY2QxMjM0IiwidXNlcl9pZCI6Mn0.xyz789",
    "user": {
        "id": 2,
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "real_name": "张三",
        "role": "student",
        "avatar": "",
        "phone": ""
    }
}
```

**字段说明**:
- `refresh`: Refresh Token（用于刷新 Access Token，有效期 7 天）
- `access`: Access Token（用于访问受保护的 API，有效期 2 小时）
- `user`: 用户信息对象
  - `id`: 用户 ID
  - `username`: 用户名
  - `email`: 邮箱
  - `real_name`: 真实姓名
  - `role`: 角色（student/teacher）
  - `avatar`: 头像 URL
  - `phone`: 手机号

**失败响应** (401 Unauthorized):
```json
{
    "detail": "没有活动的账户有这样的证书。"
}
```

---

### 3. 刷新 Token

**接口地址**: `POST /api/auth/token/refresh/`

**请求数据**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**成功响应** (200 OK):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.new_access_token..."
}
```

**说明**: 当 Access Token 过期后，使用 Refresh Token 获取新的 Access Token。

---

### 4. 获取/更新个人信息

**接口地址**: `GET/PUT /api/auth/profile/`

**认证方式**: 需要在请求头中携带 Access Token
```
Authorization: Bearer <access_token>
```

#### GET - 获取个人信息

**成功响应** (200 OK):
```json
{
    "id": 2,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "profile": {
        "role": "student",
        "real_name": "张三",
        "avatar": "http://example.com/avatar.jpg",
        "phone": "13800138000"
    }
}
```

#### PUT - 更新个人信息

**请求数据**:
```json
{
    "real_name": "张三三",
    "avatar": "http://new-avatar.jpg",
    "phone": "13900139000"
}
```

**成功响应** (200 OK):
```json
{
    "message": "个人信息更新成功",
    "profile": {
        "role": "student",
        "real_name": "张三三",
        "avatar": "http://new-avatar.jpg",
        "phone": "13900139000"
    }
}
```

**注意**: `role` 字段不可修改。

---

### 5. 修改密码

**接口地址**: `PUT /api/auth/change-password/`

**认证方式**: 需要在请求头中携带 Access Token
```
Authorization: Bearer <access_token>
```

**请求数据**:
```json
{
    "old_password": "password123",
    "new_password": "newpass456",
    "new_password_confirm": "newpass456"
}
```

**成功响应** (200 OK):
```json
{
    "message": "密码修改成功"
}
```

**失败响应** (400 Bad Request):
```json
{
    "old_password": ["原密码错误"]
}
```

---

### 6. 获取教师列表

**接口地址**: `GET /api/auth/teachers/`

**查询参数**:
- `search`: 搜索关键词（可选，支持用户名和真实姓名模糊搜索）

**示例**:
```
GET /api/auth/teachers/?search=王
```

**成功响应** (200 OK):
```json
[
    {
        "id": 1,
        "username": "wanglaoshi",
        "email": "wang@example.com",
        "first_name": "",
        "last_name": "",
        "profile": {
            "role": "teacher",
            "real_name": "王老师",
            "avatar": "",
            "phone": ""
        }
    }
]
```

---

### 7. 获取学生列表

**接口地址**: `GET /api/auth/students/`

**查询参数**:
- `search`: 搜索关键词（可选）

**示例**:
```
GET /api/auth/students/?search=张
```

**响应格式**: 同教师列表

---

## 🔐 认证说明

### JWT Token 使用方式

1. **登录**获取 Access Token 和 Refresh Token
2. **访问受保护的 API**时，在请求头中携带 Access Token：
   ```
   Authorization: Bearer <access_token>
   ```
3. **Token 过期后**，使用 Refresh Token 获取新的 Access Token
4. **Refresh Token 过期后**，需要重新登录

### Token 有效期

- **Access Token**: 2 小时
- **Refresh Token**: 7 天

---

## 💻 前端使用示例

### JavaScript (Axios)

```javascript
import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// 登录
async function login(username, password) {
    const response = await api.post('/auth/login/', {
        username,
        password
    });
    
    // 保存 token
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('user_info', JSON.stringify(response.data.user));
    
    return response.data;
}

// 设置请求拦截器（自动添加 token）
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// 设置响应拦截器（自动刷新 token）
api.interceptors.response.use(
    response => response,
    async error => {
        if (error.response?.status === 401) {
            // Token 过期，尝试刷新
            const refreshToken = localStorage.getItem('refresh_token');
            try {
                const response = await api.post('/auth/token/refresh/', {
                    refresh: refreshToken
                });
                
                // 保存新 token
                localStorage.setItem('access_token', response.data.access);
                
                // 重试原请求
                error.config.headers.Authorization = `Bearer ${response.data.access}`;
                return api.request(error.config);
            } catch (refreshError) {
                // 刷新失败，跳转到登录页
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

// 注册
async function register(userData) {
    const response = await api.post('/auth/register/', userData);
    return response.data;
}

// 获取个人信息
async function getProfile() {
    const response = await api.get('/auth/profile/');
    return response.data;
}

// 更新个人信息
async function updateProfile(profileData) {
    const response = await api.put('/auth/profile/', profileData);
    return response.data;
}

// 修改密码
async function changePassword(passwordData) {
    const response = await api.put('/auth/change-password/', passwordData);
    return response.data;
}

// 导出 API 方法
export {
    login,
    register,
    getProfile,
    updateProfile,
    changePassword
};
```

### 使用示例

```javascript
// 用户注册
const userData = {
    username: 'zhangsan',
    password: 'password123',
    password_confirm: 'password123',
    real_name: '张三',
    role: 'student',
    email: 'zhangsan@example.com'
};

try {
    const result = await register(userData);
    console.log('注册成功:', result);
} catch (error) {
    console.error('注册失败:', error.response.data);
}

// 用户登录
try {
    const result = await login('zhangsan', 'password123');
    console.log('登录成功:', result.user);
    console.log('角色:', result.user.role); // 'student' 或 'teacher'
    
    // 根据角色跳转页面
    if (result.user.role === 'teacher') {
        window.location.href = '/teacher/dashboard';
    } else {
        window.location.href = '/student/dashboard';
    }
} catch (error) {
    console.error('登录失败:', error.response.data);
}
```

---

## 🧪 使用 Postman 测试

### 1. 注册新用户

- **Method**: POST
- **URL**: `http://127.0.0.1:8000/api/auth/register/`
- **Body** (JSON):
  ```json
  {
      "username": "testuser",
      "password": "testpass123",
      "password_confirm": "testpass123",
      "real_name": "测试用户",
      "role": "student"
  }
  ```

### 2. 登录

- **Method**: POST
- **URL**: `http://127.0.0.1:8000/api/auth/login/`
- **Body** (JSON):
  ```json
  {
      "username": "testuser",
      "password": "testpass123"
  }
  ```
- **保存响应中的 `access` token**

### 3. 访问受保护的 API

- **Method**: GET
- **URL**: `http://127.0.0.1:8000/api/auth/profile/`
- **Headers**:
  ```
  Authorization: Bearer <your_access_token>
  ```

---

## 📝 注意事项

1. **密码安全**: 密码会使用 Django 的 `make_password` 函数进行哈希加密存储
2. **Token 安全**: Access Token 有效期较短（2 小时），建议前端实现自动刷新机制
3. **角色权限**: 可以根据 `role` 字段在前端实现不同的页面路由和权限控制
4. **CORS 配置**: 如果前后端分离，需要在 Django 中配置 `django-cors-headers`
5. **生产环境**: 生产环境中请修改 `SECRET_KEY`，并使用 HTTPS 协议

---

## 🚀 快速测试

运行以下命令启动服务器，然后访问 API 文档界面：

```bash
python manage.py runserver
```

访问：`http://127.0.0.1:8000/api/auth/register/` 可以看到 DRF 的可视化界面进行测试。
