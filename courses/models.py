"""
教学辅助系统 - 数据库模型设计
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    """
    用户资料扩展模型
    用于存储 Django 原生 User 模型的额外信息，如角色、真实姓名等
    """
    ROLE_CHOICES = [
        ('student', '学生'),
        ('teacher', '教师'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户',
        help_text='关联的 Django 原生用户'
    )
    role = models.CharField(
        verbose_name='角色',
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text='用户角色：学生或教师'
    )
    real_name = models.CharField(
        verbose_name='真实姓名',
        max_length=100,
        blank=True,
        help_text='用户的真实姓名'
    )
    avatar = models.URLField(
        verbose_name='头像 URL',
        blank=True,
        default='media/default/avatar/avatar.png',
        help_text='用户头像的图片链接'
    )
    phone = models.CharField(
        verbose_name='手机号',
        max_length=20,
        blank=True,
        help_text='用户的手机号码'
    )
    created_at = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True,
        db_index=True
    )

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        db_table = 'courses_userprofile'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['user', 'role']),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    用户信号 - 当创建或更新用户时自动创建/更新 UserProfile
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()


class TimeStampedModel(models.Model):
    """
    抽象基类 - 提供创建时间和更新时间字段
    所有模型都应继承此类以统一时间戳管理
    """
    created_at = models.DateTimeField(
        verbose_name='创建时间',
        default=timezone.now,
        editable=False,
        db_index=True
    )
    updated_at = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True,
        db_index=True
    )

    class Meta:
        abstract = True


class Course(TimeStampedModel):
    """
    课程模型
    教师创建课程，学生通过 CourseEnrollment 加入课程
    """
    title = models.CharField(
        verbose_name='课程名称',
        max_length=200,
        db_index=True,
        help_text='课程的标题，如 "Python 编程基础"'
    )
    description = models.TextField(
        verbose_name='课程描述',
        blank=True,
        help_text='课程的详细介绍和说明'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='taught_courses',
        verbose_name='授课教师',
        limit_choices_to={'groups__name': 'Teacher'},
        help_text='课程的创建者和授课教师'
    )
    max_students = models.PositiveIntegerField(
        verbose_name='最大学生数',
        default=50,
        help_text='课程允许的最大学生数量'
    )
    is_active = models.BooleanField(
        verbose_name='是否活跃',
        default=True,
        help_text='标记课程是否正在进行中'
    )

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.teacher.username})"

    def enrolled_count(self):
        """返回已选课的学生数量"""
        return self.enrollments.count()


class CourseEnrollment(TimeStampedModel):
    """
    课程选课表 - 学生与课程的多对多关系中间表
    记录学生加入课程的信息
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name='学生',
        limit_choices_to={'groups__name': 'Student'},
        help_text='选课的学生用户'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='课程',
        help_text='学生加入的课程'
    )
    joined_at = models.DateTimeField(
        verbose_name='加入时间',
        auto_now_add=True,
        help_text='学生加入课程的时间'
    )

    class Meta:
        verbose_name = '课程选课记录'
        verbose_name_plural = '课程选课记录'
        unique_together = ['student', 'course']  # 一个学生不能重复选同一门课
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['student', 'joined_at']),
            models.Index(fields=['course', 'joined_at']),
        ]

    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"


class Assignment(TimeStampedModel):
    """
    作业发布模型
    教师在特定课程下发布作业，包含作业说明和要求
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='所属课程',
        help_text='作业所属的课程'
    )
    title = models.CharField(
        verbose_name='作业标题',
        max_length=200,
        db_index=True,
        help_text='作业的标题，如 "第一次 Python 练习"'
    )
    description = models.TextField(
        verbose_name='作业说明',
        help_text='作业的详细要求、任务描述和提交要求'
    )
    requirements = models.TextField(
        verbose_name='具体要求',
        blank=True,
        help_text='作业的具体技术要求、评分标准等'
    )
    due_date = models.DateTimeField(
        verbose_name='截止时间',
        db_index=True,
        help_text='作业提交的截止时间'
    )
    max_score = models.PositiveIntegerField(
        verbose_name='满分分数',
        default=100,
        help_text='作业的满分分数'
    )
    allow_late_submission = models.BooleanField(
        verbose_name='允许迟交',
        default=False,
        help_text='是否允许学生在截止时间后提交'
    )
    is_published = models.BooleanField(
        verbose_name='已发布',
        default=True,
        help_text='标记作业是否已发布给学生可见'
    )

    class Meta:
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['course', 'is_published']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def submission_count(self):
        """返回已提交的学生数量"""
        return self.submissions.count()


class Submission(TimeStampedModel):
    """
    作业提交模型
    学生提交作业，支持代码片段或图片链接
    """
    STATUS_CHOICES = [
        ('pending', '待批改'),
        ('grading', '批改中'),
        ('completed', '已完成'),
        ('failed', '批改失败'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='作业',
        help_text='提交的作业'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        verbose_name='提交学生',
        limit_choices_to={'groups__name': 'Student'},
        help_text='提交作业的学生'
    )
    code_content = models.TextField(
        verbose_name='代码内容',
        blank=True,
        help_text='学生提交的代码片段（纯文本格式）'
    )
    image_urls = models.JSONField(
        verbose_name='图片链接列表',
        blank=True,
        default=list,
        help_text='学生提交的截图或作业图片的 URL 列表'
    )
    submission_text = models.TextField(
        verbose_name='文字说明',
        blank=True,
        help_text='学生对作业的额外说明或注释'
    )
    status = models.CharField(
        verbose_name='批改状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='作业批改的状态：待批改、批改中、已完成、批改失败'
    )
    submitted_at = models.DateTimeField(
        verbose_name='提交时间',
        auto_now_add=True,
        db_index=True,
        help_text='学生提交作业的时间'
    )
    is_late = models.BooleanField(
        verbose_name='是否迟交',
        default=False,
        help_text='标记是否在截止时间后提交'
    )

    class Meta:
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        unique_together = ['assignment', 'student']  # 一个学生只能提交一次作业
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['assignment', 'status']),
            models.Index(fields=['status', 'submitted_at']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} ({self.status})"


class AIResult(TimeStampedModel):
    """
    AI 批改结果模型
    存储大模型返回的批改结果，包括评分、评语和错误标签
    """
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='ai_result',
        verbose_name='作业提交',
        help_text='关联的作业提交记录'
    )
    is_correct = models.BooleanField(
        verbose_name='是否正确',
        default=False,
        help_text='AI 判断作业是否正确'
    )
    score = models.DecimalField(
        verbose_name='得分',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='AI 给出的分数（0-100）'
    )
    feedback = models.TextField(
        verbose_name='AI 评语',
        blank=True,
        help_text='AI 生成的详细评语和建议'
    )
    analysis = models.JSONField(
        verbose_name='详细分析',
        blank=True,
        default=dict,
        help_text='AI 返回的详细分析结果（结构化数据）'
    )
    graded_at = models.DateTimeField(
        verbose_name='批改时间',
        auto_now_add=True,
        db_index=True,
        help_text='AI 完成批改的时间'
    )
    model_version = models.CharField(
        verbose_name='模型版本',
        max_length=50,
        blank=True,
        help_text='用于批改的大模型版本号'
    )
    raw_response = models.JSONField(
        verbose_name='原始响应',
        blank=True,
        default=dict,
        help_text='大模型返回的原始 JSON 响应数据'
    )

    class Meta:
        verbose_name = 'AI 批改结果'
        verbose_name_plural = 'AI 批改结果'
        ordering = ['-graded_at']
        indexes = [
            models.Index(fields=['is_correct']),
            models.Index(fields=['graded_at']),
        ]

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.submission.student.username} - 得分：{self.score}"


class ErrorTag(TimeStampedModel):
    """
    错误知识点标签模型
    存储 AI 批改识别出的错误知识点或错误类型
    用于统计分析学生易错点
    """
    SEVERITY_CHOICES = [
        ('low', '轻微'),
        ('medium', '中等'),
        ('high', '严重'),
        ('critical', '致命'),
    ]

    ai_result = models.ForeignKey(
        AIResult,
        on_delete=models.CASCADE,
        related_name='error_tags',
        verbose_name='AI 批改结果',
        help_text='关联的 AI 批改结果'
    )
    tag_name = models.CharField(
        verbose_name='知识点标签',
        max_length=100,
        db_index=True,
        help_text='错误涉及的知识点名称，如 "循环语法"、"变量作用域"'
    )
    error_type = models.CharField(
        verbose_name='错误类型',
        max_length=100,
        db_index=True,
        help_text='错误的具体类型，如 "语法错误"、"逻辑错误"、"性能问题"'
    )
    description = models.TextField(
        verbose_name='错误描述',
        blank=True,
        help_text='对该错误的具体描述和说明'
    )
    severity = models.CharField(
        verbose_name='严重程度',
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text='错误的严重程度分级'
    )
    suggestion = models.TextField(
        verbose_name='改进建议',
        blank=True,
        help_text='AI 给出的针对该错误的改进建议'
    )
    code_snippet = models.TextField(
        verbose_name='错误代码片段',
        blank=True,
        help_text='出错的代码片段（用于定位问题）'
    )
    line_number = models.PositiveIntegerField(
        verbose_name='行号',
        blank=True,
        null=True,
        help_text='错误所在的代码行号（如果可定位）'
    )

    class Meta:
        verbose_name = '错误知识点标签'
        verbose_name_plural = '错误知识点标签'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tag_name']),
            models.Index(fields=['error_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['ai_result', 'tag_name']),
            # 复合索引用于高频查询场景
            models.Index(fields=['tag_name', 'error_type']),
        ]

    def __str__(self):
        return f"{self.tag_name} ({self.error_type}) - {self.severity}"
