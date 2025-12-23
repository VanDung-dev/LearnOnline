from rest_framework import serializers
from .models import Discussion, Reply, Vote

class UserSerializer(serializers.Serializer):
    """Minimal user serializer for author info"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True, allow_null=True)


class ReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_author = serializers.SerializerMethodField()
    vote_count = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'discussion', 'author', 'parent', 'body', 'created_at', 'updated_at', 'is_answer', 'is_author', 'vote_count', 'user_vote']
        read_only_fields = ['discussion', 'created_at', 'updated_at', 'is_answer']

    def get_is_author(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.author

    def get_vote_count(self, obj):
        # Optimally this should be annotated
        return obj.votes.filter(vote_type=1).count() - obj.votes.filter(vote_type=-1).count()

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                # Optimized access would need prefetch_related
                vote = obj.votes.filter(user=request.user).first()
                if vote:
                    return vote.vote_type
            except:
                pass
        return 0


class DiscussionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    vote_count = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = ['id', 'course', 'author', 'title', 'body', 'created_at', 'updated_at', 'is_resolved', 'replies', 'reply_count', 'vote_count', 'user_vote', 'is_author']
        read_only_fields = ['course', 'created_at', 'updated_at', 'is_resolved', 'replies', 'reply_count']

    def get_is_author(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.author

    def get_vote_count(self, obj):
        return obj.votes.filter(vote_type=1).count() - obj.votes.filter(vote_type=-1).count()

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = obj.votes.filter(user=request.user).first()
                if vote:
                    return vote.vote_type
            except:
                pass
        return 0

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'vote_type']
