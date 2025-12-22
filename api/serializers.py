"""
API Serializers for LearnOnline
Converts Django models to JSON and validates input data.
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import Profile
from courses.models import (
    Category,
    Course,
    Module,
    Lesson,
    Quiz,
    Question,
    Answer,
    Enrollment,
    Progress,
    Certificate,
    QuizAttempt,
    UserAnswer,
)


# ============================================
# Account Serializers
# ============================================


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (read-only)"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""

    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "bio",
            "location",
            "birth_date",
            "profile_picture",
            "website",
            "role",
            "role_display",
        ]
        read_only_fields = ["id", "user"]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        # Profile is created automatically via signal
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


# ============================================
# Course Serializers
# ============================================


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "course_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_course_count(self, obj):
        return obj.courses.count()


class InstructorSerializer(serializers.ModelSerializer):
    """Simple serializer for instructor info"""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list view (minimal data)"""

    instructor = InstructorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "thumbnail",
            "price",
            "is_free",
            "instructor",
            "category",
            "enrollment_count",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def get_is_free(self, obj):
        """Course is free if price is 0."""
        return obj.price == 0


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "slug",
            "lesson_type",
            "content",
            "video_url",
            "video_duration",
            "order",
        ]
        read_only_fields = ["id", "slug"]


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model"""

    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            "id",
            "title",
            "description",
            "order",
            "duration_days",
            "lessons",
            "lesson_count",
        ]
        read_only_fields = ["id"]

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail view (full data)"""

    instructor = InstructorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    is_free = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "thumbnail",
            "price",
            "is_free",
            "certificate_price",
            "instructor",
            "category",
            "modules",
            "enrollment_count",
            "is_enrolled",
            "opening_date",
            "closing_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

    def get_is_free(self, obj):
        """Course is free if price is 0."""
        return obj.price == 0


# ============================================
# Enrollment & Progress Serializers
# ============================================


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""

    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_id", "enrolled_at", "is_completed"]
        read_only_fields = ["id", "enrolled_at", "is_completed"]


class ProgressSerializer(serializers.ModelSerializer):
    """Serializer for Progress model"""

    lesson = LessonSerializer(read_only=True)
    lesson_id = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(), source="lesson", write_only=True
    )

    class Meta:
        model = Progress
        fields = ["id", "lesson", "lesson_id", "completed", "completed_at"]
        read_only_fields = ["id", "completed_at"]


# ============================================
# Quiz Serializers
# ============================================


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""

    class Meta:
        model = Answer
        fields = ["id", "text", "order"]
        # Note: is_correct is hidden from students


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""

    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "question_type", "order", "points", "answers"]


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "questions", "created_at"]


class QuizSubmitSerializer(serializers.Serializer):
    """Serializer for quiz submission"""

    answers = serializers.DictField(
        child=serializers.ListField(child=serializers.IntegerField()),
        help_text="Format: {question_id: [answer_ids]}",
    )


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt model"""

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "lesson",
            "attempt_number",
            "score",
            "started_at",
            "completed_at",
        ]
        read_only_fields = ["id", "attempt_number", "started_at"]


# ============================================
# Certificate Serializers
# ============================================


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for Certificate model"""

    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = ["id", "course", "certificate_number", "issued_at"]
        read_only_fields = ["id", "certificate_number", "issued_at"]
