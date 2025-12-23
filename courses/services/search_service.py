from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from ..models import SearchQuery

def log_search_query(query, user=None):
    """
    Log a search query to the database.
    Query is automatically lowercased and stripped in the model save method.
    """
    if not query:
        return None
        
    query = query.strip()
    if len(query) < 2:  # Don't log very short queries
        return None

    # Optional: Don't log if same user searched same thing recently (e.g. last 1 minute)
    # to avoid spamming DB with same query refreshes
    # But for now, simple implementation
    
    return SearchQuery.objects.create(query=query, user=user)

def get_popular_search_terms(days=30, limit=10):
    """
    Get popular search terms from the last `days` days.
    Returns a list of dictionaries with 'query' and 'count'.
    """
    start_date = timezone.now() - timedelta(days=days)
    
    return SearchQuery.objects.filter(
        created_at__gte=start_date
    ).values('query').annotate(
        count=Count('query')
    ).order_by('-count')[:limit]
