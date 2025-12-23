"""
Pagination classes for LearnOnline API.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Larger pagination for list views."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class SmallResultsSetPagination(PageNumberPagination):
    """Smaller pagination for nested or detail views."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20
