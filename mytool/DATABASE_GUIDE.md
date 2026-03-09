# 教学辅助系统 - 数据库模型使用指南

## 📋 目录
- [项目结构](#项目结构)
- [模型概览](#模型概览)
- [快速开始](#快速开始)
- [易错点统计功能](#易错点统计功能)
- [常用查询示例](#常用查询示例)

## 📁 项目结构

```
courses/
├── models.py          # 数据库模型定义
├── admin.py           # Django Admin 配置
├── analytics.py       # 统计分析工具类
└── migrations/        # 数据库迁移文件
```

## 🗂️ 模型概览

### 核心模型（6 个）

1. **Course** - 课程表
   - 教师创建课程
   - 包含课程名称、描述、最大学生数等
   - 索引：teacher + is_active

2. **CourseEnrollment** - 课程选课表
   - 学生与课程的多对多关系中间表
   - 唯一约束：student + course

3. **Assignment** - 作业表
   - 教师在课程下发布作业
   - 包含截止时间、满分、是否允许迟交等
   - 索引：course + is_published, due_date

4. **Submission** - 作业提交表
   - 学生提交作业
   - 支持代码内容、图片链接
   - 状态：pending, grading, completed, failed
   - 索引：student + status, assignment + status

5. **AIResult** - AI 批改结果表
   - 与 Submission 一对一关联
   - 存储评分、评语、AI 分析结果
   - 支持存储大模型原始响应

6. **ErrorTag** - 错误知识点标签表 ⭐
   - 存储 AI 识别的错误知识点
   - 包含错误类型、严重程度、改进建议
   - 多个索引优化查询性能
   - **核心功能：支持易错点统计分析**

## 🚀 快速开始

### 1. 配置 MySQL 数据库

参考 `myproject/db_config_example.py` 配置数据库连接

```python
# myproject/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'teaching_assistant',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### 2. 安装依赖

```bash
pip install mysqlclient
# 或
pip install pymysql
```

### 3. 创建数据库

```sql
CREATE DATABASE teaching_assistant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 执行迁移

```bash
python manage.py migrate
```

### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

### 6. 启动开发服务器

```bash
python manage.py runserver
```

访问 `http://127.0.0.1:8000/admin/` 进入管理后台

## 📊 易错点统计功能

### 设计思路

采用**独立 ErrorTag 表**而非 JSON 字段的原因：

1. ✅ **查询效率高** - 直接使用 SQL GROUP BY 聚合
2. ✅ **数据规范化** - 避免数据冗余
3. ✅ **索引优化** - 支持多字段索引加速
4. ✅ **灵活分析** - 支持复杂的多表关联查询

### 统计场景示例

#### 1. 统计某课程 Top 10 易错点

```python
from courses.analytics import CourseAnalytics

errors = CourseAnalytics.get_course_error_statistics(course_id=1, limit=10)
for error in errors:
    print(f"知识点：{error['tag_name']}")
    print(f"错误数：{error['error_count']}")
    print(f"影响学生数：{error['student_count']}")
```

#### 2. 统计学生个人薄弱点

```python
from courses.analytics import StudentAnalytics

weak_points = StudentAnalytics.get_student_weak_points(student_id=1, limit=5)
for point in weak_points:
    print(f"知识点：{point['tag_name']}")
    print(f"错误次数：{point['error_count']}")
```

#### 3. 获取作业常见错误

```python
from courses.analytics import AssignmentAnalytics

common_errors = AssignmentAnalytics.get_common_errors(assignment_id=1, limit=5)
for error in common_errors:
    print(f"{error['tag_name']} - {error['error_type']}: {error['count']}次")
```

#### 4. 错误趋势分析

```python
from courses.analytics import ErrorTagAnalytics

# 获取最近 30 天的错误趋势
trend = ErrorTagAnalytics.get_error_trend(course_id=1, days=30)
for day in trend:
    print(f"{day['date']}: {day['error_count']}个错误")
```

## 🔍 常用查询示例

### 基础查询

```python
from courses.models import Course, Assignment, Submission, AIResult, ErrorTag

# 获取某教师的所有课程
teacher_courses = Course.objects.filter(teacher=user)

# 获取某课程的所有作业
course_assignments = Assignment.objects.filter(course=course)

# 获取某学生的所有提交
student_submissions = Submission.objects.filter(student=student)

# 获取某作业的批改统计
assignment_stats = Submission.objects.filter(
    assignment=assignment
).values('status').annotate(count=Count('id'))
```

### 高级查询

```python
from django.db.models import Count, Avg, Q, F
from django.utils import timezone

# 1. 查询某课程下错误率最高的学生
from django.db.models import Count, F

error_ranking = ErrorTag.objects.filter(
    ai_result__submission__assignment__course=course
).values(
    'ai_result__submission__student'
).annotate(
    error_count=Count('id')
).order_by('-error_count')

# 2. 查询某知识点影响的所有学生
affected_students = ErrorTag.objects.filter(
    tag_name='循环语法',
    ai_result__submission__assignment__course=course
).values(
    'ai_result__submission__student__username'
).distinct()

# 3. 统计各严重程度的错误分布
severity_dist = ErrorTag.objects.filter(
    ai_result__submission__assignment__course=course
).values('severity').annotate(count=Count('id'))

# 4. 查询待批改的作业
pending_submissions = Submission.objects.filter(
    status='pending'
).select_related('student', 'assignment')

# 5. 查询平均分低于 60 的作业
low_score_assignments = Assignment.objects.annotate(
    avg_score=Avg('submissions__ai_result__score')
).filter(avg_score__lt=60)
```

### 性能优化查询

```python
# 使用 select_related 优化外键查询（一对一、多对一）
submissions = Submission.objects.select_related(
    'student',
    'assignment',
    'assignment__course'
).filter(status='completed')

# 使用 prefetch_related 优化反向查询（一对多、多对多）
courses = Course.objects.prefetch_related(
    'assignments',
    'enrollments__student'
).filter(is_active=True)

# 只查询需要的字段
error_tags = ErrorTag.objects.values(
    'tag_name',
    'error_type'
).annotate(
    count=Count('id')
)
```

## 📝 数据录入示例

### 创建课程和作业

```python
from django.contrib.auth.models import User
from courses.models import Course, Assignment

# 创建课程
teacher = User.objects.get(username='teacher1')
course = Course.objects.create(
    title='Python 编程基础',
    description='学习 Python 基础语法',
    teacher=teacher,
    max_students=50
)

# 创建作业
assignment = Assignment.objects.create(
    course=course,
    title='第一次 Python 练习',
    description='完成以下编程任务...',
    requirements='1. 使用循环\n2. 使用条件判断',
    due_date='2024-12-31 23:59:59',
    max_score=100
)
```

### 提交作业

```python
from courses.models import Submission

student = User.objects.get(username='student1')
submission = Submission.objects.create(
    assignment=assignment,
    student=student,
    code_content='for i in range(10):\n    print(i)',
    submission_text='这是我的作业',
    status='pending'
)
```

### 添加 AI 批改结果

```python
from courses.models import AIResult, ErrorTag

ai_result = AIResult.objects.create(
    submission=submission,
    is_correct=True,
    score=85.5,
    feedback='整体不错，但有一些小问题',
    analysis={
        'strengths': ['语法正确', '逻辑清晰'],
        'weaknesses': ['可以优化性能']
    },
    model_version='gpt-4-0613'
)

# 添加错误标签
ErrorTag.objects.create(
    ai_result=ai_result,
    tag_name='循环优化',
    error_type='性能问题',
    description='可以使用列表推导式优化',
    severity='low',
    suggestion='尝试使用列表推导式',
    code_snippet='for i in range(10): result.append(i*2)',
    line_number=1
)
```

## 🎯 API 接口设计建议

### RESTful API 路由

```python
# urls.py
urlpatterns = [
    path('api/courses/', CourseListCreateView.as_view()),
    path('api/courses/<int:pk>/', CourseDetailView.as_view()),
    path('api/courses/<int:course_id>/assignments/', AssignmentListView.as_view()),
    path('api/assignments/<int:assignment_id>/submissions/', SubmissionListView.as_view()),
    path('api/submissions/<int:submission_id>/ai-result/', AIResultView.as_view()),
    
    # 统计分析 API
    path('api/courses/<int:course_id>/analytics/errors/', CourseErrorStatsView.as_view()),
    path('api/students/<int:student_id>/analytics/', StudentAnalyticsView.as_view()),
]
```

### 序列化器示例

```python
from rest_framework import serializers
from courses.models import Course, Assignment, Submission, AIResult, ErrorTag

class ErrorTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorTag
        fields = ['tag_name', 'error_type', 'severity', 'description', 'suggestion']

class AIResultSerializer(serializers.ModelSerializer):
    error_tags = ErrorTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = AIResult
        fields = ['score', 'is_correct', 'feedback', 'error_tags']

class SubmissionSerializer(serializers.ModelSerializer):
    ai_result = AIResultSerializer(read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'code_content', 'status', 'submitted_at', 'ai_result']
```

## 🔧 管理命令

创建一些常用的管理命令来辅助数据分析：

```python
# courses/management/commands/analyze_course_errors.py
from django.core.management.base import BaseCommand
from courses.analytics import CourseAnalytics

class Command(BaseCommand):
    help = '分析课程易错点'

    def add_arguments(self, parser):
        parser.add_argument('course_id', type=int)
        parser.add_argument('--limit', type=int, default=10)

    def handle(self, *args, **options):
        course_id = options['course_id']
        limit = options['limit']
        
        errors = CourseAnalytics.get_course_error_statistics(course_id, limit)
        
        self.stdout.write(f'\n课程 {course_id} Top {limit} 易错点:\n')
        for i, error in enumerate(errors, 1):
            self.stdout.write(
                f"{i}. {error['tag_name']} - "
                f"错误数：{error['error_count']}, "
                f"学生数：{error['student_count']}"
            )
```

使用：
```bash
python manage.py analyze_course_errors 1 --limit 10
```

## 📚 最佳实践

1. **批量创建 ErrorTag**
   ```python
   # 使用 bulk_create 提高性能
   ErrorTag.objects.bulk_create([
       ErrorTag(ai_result=result, tag_name='...', ...),
       ErrorTag(ai_result=result, tag_name='...', ...),
   ])
   ```

2. **定期清理旧数据**
   ```python
   # 创建定时任务清理一年前的数据
   from django.utils import timezone
   
   old_date = timezone.now() - timezone.timedelta(days=365)
   Submission.objects.filter(submitted_at__lt=old_date).delete()
   ```

3. **使用数据库视图优化复杂查询**
   ```sql
   CREATE VIEW course_error_stats AS
   SELECT 
       c.id as course_id,
       et.tag_name,
       COUNT(et.id) as error_count,
       COUNT(DISTINCT s.student_id) as student_count
   FROM courses_errortag et
   JOIN courses_airesult ar ON et.ai_result_id = ar.id
   JOIN courses_submission s ON ar.submission_id = s.id
   JOIN courses_assignment a ON s.assignment_id = a.id
   JOIN courses_course c ON a.course_id = c.id
   GROUP BY c.id, et.tag_name;
   ```

## 🎓 总结

本设计通过独立的 `ErrorTag` 表实现了灵活的易错点统计功能，支持：
- ✅ 按课程统计高频错误
- ✅ 按学生分析薄弱知识点
- ✅ 按时间追踪错误趋势
- ✅ 多维度数据聚合分析

配合 Django ORM 和 DRF，可以快速构建功能完善的教学辅助系统 API。
