# API文档

1. ### 用户注册文档

   **接口地址:	**POST /api/auth/register/

   **提交数据格式**：

   ```json
   {
       "username": "str",
       "password": "str",
       "password_confirm": "str",
       "real_name": "str",
       "role": "student/teacher",
       "email": "email" 
   }
   ```

   **字段**：

   - username`: 用户名（必填，3-150 字符，不能重复）
   - `password`: 密码（必填，至少 6 个字符）
   - `password_confirm`: 确认密码（必填，必须与 password 一致）
   - `real_name`: 真实姓名（必填,如果不严谨后面可改工号或者学号)
   - `role`: 角色（必填，可选值：`student` 或 `teacher`）
   - `email`: 邮箱（可选）

   **响应结果**

   - **成功**

     ```json
     {
         "id": 1,
         "username": "tesuser",
         "email": "tesuser@qq.com",
         "first_name": "",
         "last_name": "",
         "profile": {
             "role": "student",
             "real_name": "tesuser",
             "avatar": "",
             "phone": ""
         },
         "message": "注册成功"
     }
     ```

   - **失败**

     ```json
     {
         "username": ["该用户名已存在。"],
         "password_confirm": ["两次输入的密码不一致"]
     }
     ```

     > 测试用户名称:testuser 密码:testuser123

   ------

2. **用户登录API**

   **接口地址**:	POST /api/auth/login/

   **提交数据格式**:

   ```json
   {
       "username":"str",
       "passwrod":"str"
   }
   ```

   - **成功**

     ```json
     {
         "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcwMDAwMDAwMCwiaWF0IjoxNjk5MDAwMDAwLCJqdGkiOiJhYmNkMTIzNCIsInVzZXJfaWQiOjJ9.abc123",
         "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzAwMDAwMDAwLCJpYXQiOjE2OTkwMDAwMDAsImp0aSI6ImFiY2QxMjM0IiwidXNlcl9pZCI6Mn0.xyz789",
         "user": {
             "id": 1,
             "username": "tesuser",
             "email": "tesuser@qq.com",
             "real_name": "tesuser",
             "role": "student",
             "avatar": "",
             "phone": ""
         }
     }
     ```

   - **失败**

     ```json
     {
         "detail": "证书验证失败"
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

   ------

   

3. **Token刷新API**

   **接口地址:**	POST /api/auth/token/refresh/

   

   **请求数据**:

   ```json
   {
       "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   }
   ```

   **成功** :

   ```json
   {
       "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.new_access_token..."
   }
   ```

   **说明**: 当 Access Token 过期后，使用 Refresh Token 获取新的 Access Token。

   ---

4. **获取/更新个人信息**

   **接口地址**	GET/PUT /api/auth/profile/

   **此接口需要携带Token**

   

   **GET-获取个人信息**

   - **成功**

     ```json
     {
         "id": 1,
         "username": "tesuser",
         "email": "tesuser@qq.com",
         "profile": {
             "role": "student",
             "real_name": "tesueser",
             "avatar": "http://example.com/avatar.jpg",
             "phone": "13800138000"
         }
     }
     ```

   

   **PUT-更新个人信息**

   **提交数据格式**

   ```json
   {
       "real_name": "new_user",
       "avatar": "http://new-avatar.jpg",
       "phone": "13900139000"
   }
   ```

   - **成功**

     ```json
     {
         "message": "个人信息更新成功",
         "profile": {
             "role": "student",
             "real_name": "new_user",
             "avatar": "http://new-avatar.jpg",
             "phone": "13900139000"
         }
     }
     ```

     ------

     

5. **修改密码**

   **接口地址**：	PUT /api/auth/change-password/
   **此接口需要携带Token**

   **提交数据格式**

   ```json
   {
       "old_password": "password123",
       "new_password": "newpass456",
       "new_password_confirm": "newpass456"
   }
   ```

   - **成功**

     ```json
     {
         "message": "密码修改成功"
     }
     ```

   - **失败**

     ```json
     {
         "old_password": ["原密码错误"]
     }
     ```

6. **教师列表API**

   **接口地址:**	GET /api/auth/teachers/

   **查询参数**:

   - `search`: 搜索关键词（可选，支持用户名和真实姓名模糊搜索）

   - eg：

     ```json
     GET /api/auth/teachers/?search=王
     ```

   - **成功**

     ```json
     [
         {
             "id": 1,
             "username": "wanglaoshi",
             "email": "wang@qq.com",
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

   ------

7. **获取学生列表API**

   **接口地址:**	GET /api/auth/students/

   **查询参数**:

   - `search`: 搜索关键词（可选，支持用户名和真实姓名模糊搜索）

   - eg：

     ```json
     GET /api/auth/students/?search=张
     ```

   - **成功**

     ```json
     [
         {
             "id": 1,
             "username": "zhangtongxue",
             "email": "zhang@qq.com",
             "first_name": "",
             "last_name": "",
             "profile": {
                 "role": "student",
                 "real_name": "张同学",
                 "avatar": "",
                 "phone": ""
             }
         }
     ]
     ```

   

   ------

   ## Token说明

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