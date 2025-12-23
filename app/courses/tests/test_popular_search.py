from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from courses.models import SearchQuery
from courses.services.search_service import log_search_query, get_popular_search_terms

User = get_user_model()

class PopularSearchTrackingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_log_search_query(self):
        # Test logging a valid query
        query = log_search_query("Python Course", self.user)
        self.assertIsNotNone(query)
        self.assertEqual(query.query, "python course")
        self.assertEqual(query.user, self.user)
        self.assertEqual(SearchQuery.objects.count(), 1)

    def test_log_search_query_anonymous(self):
        # Test logging without user
        query = log_search_query("Django", None)
        self.assertIsNotNone(query)
        self.assertEqual(query.query, "django")
        self.assertIsNone(query.user)
        self.assertEqual(SearchQuery.objects.count(), 1)

    def test_log_search_query_too_short(self):
        # Test logging short query
        query = log_search_query("a", self.user)
        self.assertIsNone(query)
        self.assertEqual(SearchQuery.objects.count(), 0)

    def test_log_search_query_whitespace(self):
        # Test logging whitespace
        query = log_search_query("   ", self.user)
        self.assertIsNone(query)
        self.assertEqual(SearchQuery.objects.count(), 0)

    def test_get_popular_search_terms(self):
        # Create some search queries
        log_search_query("python", self.user)
        log_search_query("python", self.user)
        log_search_query("python", None)
        log_search_query("django", self.user)
        log_search_query("django", None)
        log_search_query("react", self.user)

        # Create an old query
        old_query = SearchQuery.objects.create(query="old query", created_at=timezone.now() - timedelta(days=31))
        # Hack to bypass auto_now_add limitation in tests
        SearchQuery.objects.filter(id=old_query.id).update(created_at=timezone.now() - timedelta(days=31))

        popular = get_popular_search_terms(days=30, limit=2)
        
        self.assertEqual(len(popular), 2)
        # Sort by query to ensure deterministic order for assertion if counts are equal? 
        # But popular returns ordered by -count.
        # python: 3, django: 2. So python should be first.
        
        self.assertEqual(popular[0]['query'], 'python')
        self.assertEqual(popular[0]['count'], 3)
        self.assertEqual(popular[1]['query'], 'django')
        self.assertEqual(popular[1]['count'], 2)

        # Check that 'old query' is not included
        queries = [p['query'] for p in popular]
        self.assertNotIn('old query', queries)
