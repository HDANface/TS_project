"""
用户认证模块 - 视图
包含用户注册、登录、个人信息管理等视图
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    用户注册格式响应-(后期记得删响应格式)
    POST /api/auth/register/
    
    请求数据：
    {
        "username": "test",
        "password": "password",
        "password_confirm": "password",
        "real_name": "test",
        "role": "student",  // 或 "teacher"
        "email": "test@example.com"  // 可选
    }
    
    响应数据：
    {
        "id": 1,
        "username": "test",
        "email": "test@example.com",
        "profile": {
            "role": "student",
            "real_name": "test",
            "avatar": "", //登录修改
            "phone": ""   //登录修改
        }
    }
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 返回用户信息
        response_data = UserSerializer(user).data
        response_data['message'] = '注册成功'
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    用户登录视图（JWT）-(后期记得删响应格式)
    POST /api/auth/login/
    
    请求数据：
    {
        "username": "zhangsan",
        "password": "password123"
    }
    
    响应数据：
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {
            "id": 1,
            "username": "test",
            "email": "test@example.com",
            "real_name": "test",
            "role": "student",
            "avatar": "",
            "phone": ""
        }
    }
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 返回 token 和用户信息
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshView(TokenRefreshView):
    """
    刷新 Token 视图-(后期记得删响应格式)
    POST /api/auth/token/refresh/
    
    请求数据：
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    
    响应数据：
    {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户个人信息视图-(后期记得删响应格式)
    GET/PUT /api/auth/profile/
    
    需要认证：是
    
    GET 响应数据：
    {
        "id": 1,
        "username": "test",
        "email": "test@example.com",
        "profile": {
            "role": "student",
            "real_name": "test",
            "avatar": "http://...",
            "phone": "13800138000"
        }
    }
    
    PUT 请求数据：
    {
        "real_name": "newuser",
        "avatar": "http://new-avatar.jpg",
        "phone": "13900139000"
    }
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        获取当前登录用户的 profile
        """
        return self.request.user.profile
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # 返回完整的用户信息
        response_data = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'profile': serializer.data
        }
        
        return Response(response_data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': '个人信息更新成功',
            'profile': serializer.data
        })


class ChangePasswordView(generics.UpdateAPIView):
    """
    修改密码视图-(后期记得删响应格式)
    PUT /api/auth/change-password/
    
    需要认证：是
    
    请求数据：
    {
        "old_password": "oldpass123",
        "new_password": "newpass456",
        "new_password_confirm": "newpass456"
    }
    
    响应数据：
    {
        "message": "密码修改成功"
    }
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # 保存新密码
        user = serializer.save()
        
        # 保持登录状态
        update_session_auth_hash(request, user)
        
        return Response({
            'message': '密码修改成功'
        }, status=status.HTTP_200_OK)


class TeacherListView(generics.ListAPIView):
    """
    教师列表视图-(后期记得删响应格式)
    GET /api/auth/teachers/
    
    查询参数：
    - search: 搜索教师姓名或用户名
    
    响应数据：
    [
        {
            "id": 1,
            "username": "teacher1",
            "email": "teacher1@example.com",
            "profile": {
                "role": "teacher",
                "real_name": "王老师",
                "avatar": "",
                "phone": ""
            }
        }
    ]
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = User.objects.filter(profile__role='teacher')
        
        # 搜索功能
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(profile__real_name__icontains=search)
            )
        
        return queryset


class StudentListView(generics.ListAPIView):
    """
    学生列表视图-(后期记得删响应格式)
    GET /api/auth/students/
    
    查询参数：
    - search: 搜索学生姓名或用户名
    
    响应数据：
    [
        {
            "id": 1,
            "username": "student1",
            "email": "student1@example.com",
            "profile": {
                "role": "student",
                "real_name": "小明",
                "avatar": "",
                "phone": ""
            }
        }
    ]
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = User.objects.filter(profile__role='student')
        
        # 搜索功能
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(profile__real_name__icontains=search)
            )
        
        return queryset


# 导入 Q 对象
from django.db.models import Q
