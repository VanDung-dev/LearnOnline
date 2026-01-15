"""
Search views for LearnOnline API.
Provides full-text search for courses and lessons with filtering and autocomplete.
"""

from django.db.models import Q, F, Value, FloatField, Case, When, Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from apps.courses.models import Category, Course, Lesson

from .search_serializers import (
    SearchCourseSerializer,
    SearchLessonSerializer,
    SearchQuerySerializer,
    AutocompleteSerializer,
    AutocompleteSuggestionSerializer,
)
from .pagination import StandardResultsSetPagination


from apps.courses.services.search_service import log_search_query, get_popular_search_terms

class SearchCoursesView(APIView):
    """
    Search courses by title, description, or instructor name.
    Supports filtering by category, price range, and sorting options.
    """

    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name="q", description="Search query", required=True, type=str),
            OpenApiParameter(name="category", description="Category ID filter", required=False, type=int),
            OpenApiParameter(name="is_free", description="Filter free courses", required=False, type=bool),
            OpenApiParameter(name="min_price", description="Minimum price", required=False, type=float),
            OpenApiParameter(name="max_price", description="Maximum price", required=False, type=float),
            OpenApiParameter(name="instructor", description="Instructor ID", required=False, type=int),
            OpenApiParameter(name="ordering", description="Sort order", required=False, type=str),
        ],
        responses={200: SearchCourseSerializer(many=True)},
        description="Search courses with full-text search and filters",
        tags=["search"],
    )
    def get(self, request):
        # Validate query parameters
        serializer = SearchQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data["q"].strip().lower()
        filters = serializer.validated_data

        # Log search query
        log_search_query(query, request.user if request.user.is_authenticated else None)

        # Build search query
        queryset = Course.objects.filter(is_active=True)


        # Full-text search across multiple fields
        search_query = (
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query) |
            Q(category__name__icontains=query)
        )
        queryset = queryset.filter(search_query)

        # Apply filters
        if filters.get("category"):
            queryset = queryset.filter(category_id=filters["category"])

        if filters.get("is_free"):
            queryset = queryset.filter(price=0)

        if filters.get("min_price") is not None:
            queryset = queryset.filter(price__gte=filters["min_price"])

        if filters.get("max_price") is not None:
            queryset = queryset.filter(price__lte=filters["max_price"])

        if filters.get("instructor"):
            queryset = queryset.filter(instructor_id=filters["instructor"])

        # Calculate relevance score and apply ordering
        queryset = self._apply_relevance_and_ordering(queryset, query, filters.get("ordering", "relevance"))

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = SearchCourseSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SearchCourseSerializer(queryset, many=True)
        return Response(serializer.data)

    def _apply_relevance_and_ordering(self, queryset, query, ordering):
        """Apply relevance scoring and ordering to queryset."""

        # Simple relevance scoring based on field matches
        queryset = queryset.annotate(
            title_match=Case(
                When(title__iexact=query, then=Value(10.0)),
                When(title__istartswith=query, then=Value(5.0)),
                When(title__icontains=query, then=Value(3.0)),
                default=Value(0.0),
                output_field=FloatField(),
            ),
            desc_match=Case(
                When(short_description__icontains=query, then=Value(2.0)),
                When(description__icontains=query, then=Value(1.0)),
                default=Value(0.0),
                output_field=FloatField(),
            ),
            enrollment_count=Count("enrollments"),
        ).annotate(
            relevance_score=F("title_match") + F("desc_match")
        )

        # Apply ordering
        if ordering == "relevance":
            queryset = queryset.order_by("-relevance_score", "-enrollment_count", "-created_at")
        elif ordering == "newest":
            queryset = queryset.order_by("-created_at")
        elif ordering == "oldest":
            queryset = queryset.order_by("created_at")
        elif ordering == "price_low":
            queryset = queryset.order_by("price", "-relevance_score")
        elif ordering == "price_high":
            queryset = queryset.order_by("-price", "-relevance_score")
        elif ordering == "popular":
            queryset = queryset.order_by("-enrollment_count", "-relevance_score")

        return queryset


class SearchLessonsView(APIView):
    """
    Search lessons by title and content.
    Returns lessons with course context.
    """

    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name="q", description="Search query", required=True, type=str),
            OpenApiParameter(name="course", description="Filter by course slug", required=False, type=str),
            OpenApiParameter(name="lesson_type", description="Filter by type (text/video/quiz)", required=False, type=str),
        ],
        responses={200: SearchLessonSerializer(many=True)},
        description="Search lessons within courses",
        tags=["search"],
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if len(query) < 2:
            return Response(
                {"error": "Search query must be at least 2 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build search query
        queryset = Lesson.objects.filter(is_published=True)

        search_query = (
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
        queryset = queryset.filter(search_query)

        # Apply filters
        course_slug = request.query_params.get("course")
        if course_slug:
            queryset = queryset.filter(section__course__slug=course_slug)

        lesson_type = request.query_params.get("lesson_type")
        if lesson_type in ["text", "video", "quiz"]:
            queryset = queryset.filter(lesson_type=lesson_type)

        # Annotate with relevance score
        queryset = queryset.annotate(
            relevance_score=Case(
                When(title__iexact=query, then=Value(10.0)),
                When(title__istartswith=query, then=Value(5.0)),
                When(title__icontains=query, then=Value(3.0)),
                When(content__icontains=query, then=Value(1.0)),
                default=Value(0.0),
                output_field=FloatField(),
            )
        ).order_by("-relevance_score", "order")

        # Select related for efficiency
        queryset = queryset.select_related("section", "section__course")

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = SearchLessonSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SearchLessonSerializer(queryset, many=True)
        return Response(serializer.data)


class AutocompleteView(APIView):
    """
    Provide autocomplete suggestions for search queries.
    Returns suggestions from courses, categories, and instructors.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="q", description="Autocomplete query", required=True, type=str),
            OpenApiParameter(name="limit", description="Max suggestions", required=False, type=int),
        ],
        responses={200: AutocompleteSuggestionSerializer(many=True)},
        description="Get autocomplete suggestions",
        tags=["search"],
    )
    def get(self, request):
        serializer = AutocompleteSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data["q"].strip().lower()
        limit = serializer.validated_data.get("limit", 5)

        suggestions = []

        # Course suggestions
        courses = Course.objects.filter(
            is_active=True,
            title__icontains=query
        ).values("id", "title", "slug")[:limit]

        for course in courses:
            suggestions.append({
                "text": course["title"],
                "type": "course",
                "id": course["id"],
                "url": f"/courses/{course['slug']}/"
            })

        # Category suggestions
        if len(suggestions) < limit:
            remaining = limit - len(suggestions)
            categories = Category.objects.filter(
                name__icontains=query
            ).values("id", "name")[:remaining]

            for category in categories:
                suggestions.append({
                    "text": category["name"],
                    "type": "category",
                    "id": category["id"],
                    "url": f"/courses/?category={category['id']}"
                })

        return Response(suggestions)


class SearchGlobalView(APIView):
    """
    Global search across courses, lessons, and categories.
    Returns combined results from all searchable content.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="q", description="Search query", required=True, type=str),
        ],
        description="Search across all content types",
        tags=["search"],
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if len(query) < 2:
            return Response(
                {"error": "Search query must be at least 2 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = {
            "query": query,
            "courses": [],
            "lessons": [],
            "categories": [],
        }

        # Search courses (limit 5)
        courses = Course.objects.filter(
            is_active=True
        ).filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query)
        ).select_related("instructor", "category")[:5]

        results["courses"] = SearchCourseSerializer(courses, many=True).data

        # Search lessons (limit 5)
        lessons = Lesson.objects.filter(
            is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).select_related("section", "section__course")[:5]

        results["lessons"] = SearchLessonSerializer(lessons, many=True).data

        # Search categories (limit 3)
        categories = Category.objects.filter(
            name__icontains=query
        )[:3]

        results["categories"] = [
            {"id": cat.id, "name": cat.name, "description": cat.description}
            for cat in categories
        ]

        return Response(results)


class PopularSearchTermsView(APIView):
    """
    Get popular search terms.
    Returns a list of popular search queries from the last 30 days.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="limit", description="Number of results", required=False, type=int),
        ],
        description="Get popular search terms",
        tags=["search"],
    )
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        # Cap limit at 50
        limit = min(limit, 50)
        
        popular_terms = get_popular_search_terms(limit=limit)
        
        return Response(popular_terms)
