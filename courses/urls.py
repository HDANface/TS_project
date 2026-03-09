"""
用户认证模块 - URL 路由配置
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    ChangePasswordView,
    TeacherListView,
    StudentListView,
)

app_name = 'courses'

urlpatterns = [
    # 认证相关
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 用户信息相关
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # 用户列表
    path('auth/teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('auth/students/', StudentListView.as_view(), name='student_list'),
]
