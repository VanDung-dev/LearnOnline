"""
Search serializers for LearnOnline API.
Handles serialization of search results with relevance highlighting.
"""

from rest_framework import serializers

from courses.models import Course, Lesson


class SearchCourseSerializer(serializers.ModelSerializer):
    """Serializer for course search results."""

    instructor_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    is_free = serializers.SerializerMethodField()
    relevance_score = serializers.FloatField(read_only=True, required=False)

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
            "instructor_name",
            "category_name",
            "enrollment_count",
            "created_at",
            "relevance_score",
        ]

    def get_instructor_name(self, obj):
        return f"{obj.instructor.first_name} {obj.instructor.last_name}".strip() or obj.instructor.username

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def get_is_free(self, obj):
        return obj.price == 0


class SearchLessonSerializer(serializers.ModelSerializer):
    """Serializer for lesson search results."""

    course_title = serializers.CharField(source="module.course.title", read_only=True)
    course_slug = serializers.CharField(source="module.course.slug", read_only=True)
    module_title = serializers.CharField(source="module.title", read_only=True)
    relevance_score = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "slug",
            "lesson_type",
            "course_title",
            "course_slug",
            "module_title",
            "order",
            "relevance_score",
        ]


class SearchQuerySerializer(serializers.Serializer):
    """Serializer for validating search query parameters."""

    q = serializers.CharField(
        required=True,
        min_length=2,
        max_length=100,
        help_text="Search query (min 2 characters)"
    )
    category = serializers.IntegerField(
        required=False,
        help_text="Filter by category ID"
    )
    is_free = serializers.BooleanField(
        required=False,
        help_text="Filter free courses only"
    )
    min_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        help_text="Minimum price filter"
    )
    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        help_text="Maximum price filter"
    )
    instructor = serializers.IntegerField(
        required=False,
        help_text="Filter by instructor ID"
    )
    ordering = serializers.ChoiceField(
        required=False,
        choices=[
            ("relevance", "Relevance"),
            ("newest", "Newest First"),
            ("oldest", "Oldest First"),
            ("price_low", "Price: Low to High"),
            ("price_high", "Price: High to Low"),
            ("popular", "Most Popular"),
        ],
        default="relevance",
        help_text="Sort order for results"
    )


class AutocompleteSerializer(serializers.Serializer):
    """Serializer for autocomplete suggestions."""

    q = serializers.CharField(
        required=True,
        min_length=1,
        max_length=50,
        help_text="Autocomplete query"
    )
    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        default=5,
        help_text="Number of suggestions to return"
    )


class AutocompleteSuggestionSerializer(serializers.Serializer):
    """Serializer for autocomplete suggestion results."""

    text = serializers.CharField()
    type = serializers.CharField()  # 'course', 'category', 'instructor'
    id = serializers.IntegerField()
    url = serializers.CharField(required=False)
