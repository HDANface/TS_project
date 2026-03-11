"""
课程应用 - URL 路由配置
包含认证模块和课程模块的所有路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    ChangePasswordView,
    TeacherListView,
    StudentListView,
)
from .views_course import CourseViewSet

# 创建路由器并注册 ViewSet
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

app_name = 'courses'

urlpatterns = [
    # ========== 认证模块路由 ==========
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/teachers/', TeacherListView.as_view(), name='teacher_list'),
    path('auth/students/', StudentListView.as_view(), name='student_list'),
    
    # ========== 课程模块路由（由 router 自动生成） ==========
    # GET    /api/courses/              - 课程列表
    # POST   /api/courses/              - 创建课程（仅教师）
    # GET    /api/courses/{id}/         - 课程详情
    # PUT    /api/courses/{id}/         - 更新课程（仅创建者）
    # DELETE /api/courses/{id}/         - 删除课程（仅创建者）
    # POST   /api/courses/{id}/enroll/  - 选课（仅学生）
    # POST   /api/courses/{id}/drop/    - 退课（仅学生）
    # GET    /api/courses/{id}/students/ - 查看学生列表（仅教师）
    # GET    /api/courses/taught_courses/ - 教师创建的课程
    # GET    /api/courses/my_enrollments/ - 学生已选课程
    # GET    /api/courses/available_courses/ - 可选课程
    path('', include(router.urls)),
]
