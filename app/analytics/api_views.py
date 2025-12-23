from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import get_student_progress, get_instructor_stats

class StudentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_student_progress(request.user)
        return Response(data)

class InstructorAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_instructor():
             return Response({"error": "Unauthorized"}, status=403)
        
        data = get_instructor_stats(request.user)
        return Response(data)
