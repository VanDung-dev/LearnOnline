from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Count, Prefetch
from apps.courses.models import Course, Enrollment
from .models import Discussion, Reply, Vote
from .serializers import DiscussionSerializer, ReplySerializer, VoteSerializer
from apps.notifications.services import create_notification
from django.urls import reverse

class IsEnrolledOrInstructor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj is Discussion or course_id from view
        if hasattr(obj, 'course'):
            course = obj.course
        else:
            # If obj is a Reply, get course via discussion
            if hasattr(obj, 'discussion'):
                course = obj.discussion.course
            else:
                return False # Should not happen
        
        # Check enrollment or instructor status
        if course.instructor == request.user:
            return True
        return Enrollment.objects.filter(course=course, user=request.user).exists()


class DiscussionViewSet(viewsets.ModelViewSet):
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolledOrInstructor]

    def get_queryset(self):
        # Optimizations
        queryset = Discussion.objects.select_related('author', 'author__profile').prefetch_related(
            'votes',
            Prefetch('replies', queryset=Reply.objects.select_related('author', 'author__profile').order_by('created_at'))
        ).annotate(reply_count=Count('replies'))
        
        course_slug = self.request.query_params.get('course_slug')
        if course_slug:
            queryset = queryset.filter(course__slug=course_slug)
        
        return queryset

    def perform_create(self, serializer):
        course_slug = self.request.data.get('course_slug')
        course = get_object_or_404(Course, slug=course_slug)
        
        # Verify permission (instructor or enrolled)
        if course.instructor != self.request.user and not Enrollment.objects.filter(course=course, user=self.request.user).exists():
            raise permissions.PermissionDenied("You are not enrolled in this course.")

        serializer.save(author=self.request.user, course=course)



    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        discussion = self.get_object()
        serializer = ReplySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            reply = serializer.save(author=request.user, discussion=discussion)
            
            # Notify discussion author if someone else replied
            if discussion.author != request.user:
                link = reverse('discussions:discussion_detail', kwargs={'course_slug': discussion.course.slug, 'slug': discussion.slug, 'pk': discussion.pk})
                create_notification(
                    recipient=discussion.author,
                    title=f"New reply in {discussion.title}",
                    message=f"{request.user.username} replied to your discussion.",
                    link=link,
                    notification_type='discussion',
                    sender=request.user
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        discussion = self.get_object()
        try:
            vote_type = int(request.data.get('vote_type'))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid vote type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if vote_type not in [1, -1, 0]:
            return Response({'error': 'Invalid vote type'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove existing vote
        Vote.objects.filter(user=request.user, discussion=discussion).delete()

        if vote_type != 0:
            Vote.objects.create(user=request.user, discussion=discussion, vote_type=vote_type)

        return Response({'status': 'voted'})


class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset()

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        reply = self.get_object()
        vote_type = int(request.data.get('vote_type', 0))
        
        if vote_type not in [1, -1, 0]:
            return Response({'error': 'Invalid vote type'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove existing vote
        Vote.objects.filter(user=request.user, reply=reply).delete()

        if vote_type != 0:
            Vote.objects.create(user=request.user, reply=reply, vote_type=vote_type)

        return Response({'status': 'voted'})

    @action(detail=True, methods=['post'])
    def mark_answer(self, request, pk=None):
        reply = self.get_object()
        discussion = reply.discussion
        
        # Only discussion author or instructor can mark answer
        if request.user != discussion.author and request.user != discussion.course.instructor:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Unmark other answers in this discussion
        discussion.replies.filter(is_answer=True).update(is_answer=False)
        
        reply.is_answer = True
        reply.save()
        
        discussion.is_resolved = True
        discussion.is_resolved = True
        discussion.save()
        
        # Notify reply author if their answer was marked
        if reply.author != request.user:
            link = reverse('discussions:discussion_detail', kwargs={'course_slug': discussion.course.slug, 'slug': discussion.slug, 'pk': discussion.pk})
            create_notification(
                recipient=reply.author,
                title="Your reply marked as answer",
                message=f"Your reply in '{discussion.title}' was marked as the answer.",
                link=link,
                notification_type='discussion',
                sender=request.user
            )

        return Response({'status': 'marked as answer'})
