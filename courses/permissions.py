"""
课程模块 - 自定义权限控制
定义教师、学生、课程所有者等权限验证
"""
from rest_framework import permissions
from courses.models import Course


class IsTeacher(permissions.BasePermission):
    """
    只允许教师角色访问
    用于创建课程等仅限教师的操作
    """
    message = "只有教师角色才能执行此操作"
    
    def has_permission(self, request, view):
        # 首先确保用户已认证
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户是否有 profile 且角色为教师
        return hasattr(request.user, 'profile') and request.user.profile.role == 'teacher'


class IsStudent(permissions.BasePermission):
    """
    只允许学生角色访问
    用于选课、退课等仅限学生的操作
    """
    message = "只有学生角色才能执行此操作"
    
    def has_permission(self, request, view):
        # 首先确保用户已认证
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户是否有 profile 且角色为学生
        return hasattr(request.user, 'profile') and request.user.profile.role == 'student'


class IsCourseOwnerOrReadOnly(permissions.BasePermission):
    """
    课程所有者（创建者）或只读权限
    - 教师可以创建课程
    - 只有课程创建者可以修改/删除课程
    - 其他人只能查看（只读）
    """
    message = "您没有权限修改或删除此课程"
    
    def has_permission(self, request, view):
        # 认证用户可以进行安全方法（GET, HEAD, OPTIONS）操作
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 非认证用户不能进行写操作
        if not request.user or not request.user.is_authenticated:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # 安全方法允许所有人访问
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写操作（PUT, PATCH, DELETE）只有课程创建者才能执行
        return obj.teacher == request.user


class IsEnrolledOrReadOnly(permissions.BasePermission):
    """
    已选课学生或只读权限
    用于课程资源访问控制，只有已选课的学生才能访问课程资源
    """
    message = "您还没有加入该课程"
    
    def has_object_permission(self, request, view, obj):
        # 安全方法允许访问
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写操作需要是已选课的学生
        if not request.user.is_authenticated:
            return False
        
        # 检查是否是课程教师
        if hasattr(obj, 'teacher') and obj.teacher == request.user:
            return True
        
        # 检查是否已选课
        return obj.enrollments.filter(student=request.user).exists()


class IsTeacherOrStudent(permissions.BasePermission):
    """
    允许教师或学生角色访问
    用于同时支持教师和学生的通用接口
    """
    message = "只有教师或学生角色才能访问"
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return request.user.profile.role in ['teacher', 'student']
