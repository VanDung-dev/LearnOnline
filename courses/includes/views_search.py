"""
Search views for the web interface.
Provides autocomplete and search functionality.
"""

from django.http import JsonResponse
from django.db.models import Q

from ..models import Course, Category


def search_autocomplete(request):
    """
    AJAX endpoint for search autocomplete suggestions.
    Returns JSON list of suggestions from courses and categories.
    
    Query Parameters:
        q: Search query (minimum 1 character)
        limit: Maximum number of suggestions (default 5, max 10)
    """
    query = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 5)), 10)
    
    if len(query) < 1:
        return JsonResponse([], safe=False)
    
    suggestions = []
    
    # Course suggestions
    courses = Course.objects.filter(
        is_active=True,
        title__icontains=query
    ).values('id', 'title', 'slug')[:limit]
    
    for course in courses:
        suggestions.append({
            'text': course['title'],
            'type': 'course',
            'id': course['id'],
            'url': f"/courses/{course['slug']}/"
        })
    
    # Category suggestions (if room for more)
    if len(suggestions) < limit:
        remaining = limit - len(suggestions)
        categories = Category.objects.filter(
            name__icontains=query
        ).values('id', 'name')[:remaining]
        
        for cat in categories:
            suggestions.append({
                'text': cat['name'],
                'type': 'category',
                'id': cat['id'],
                'url': f"/courses/?category={cat['id']}"
            })
    
    return JsonResponse(suggestions, safe=False)
