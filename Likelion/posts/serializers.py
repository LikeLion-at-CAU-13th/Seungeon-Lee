### Model Serializer case

from rest_framework import serializers
from .models import Post
from .models import Comment
from .models import LinkCategory
from .models import Image
from config.custom_api_exceptions import PostConflictException
from config.custom_api_exceptions import CommentException
from config.custom_api_exceptions import UseroneConflictException
from django.utils import timezone

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

    # 중복된 게시글 제목이 있다면 예외 발생
    def validate(self, data):
        request = self.context.get('request')
        user = data["user"]
        today = timezone.localdate()
        print(user)
        
        if Post.objects.filter(title=data['title']).exists():
            raise PostConflictException(detail=f"A post with title: '{data['title']}' already exists.")
        
        if user and Post.objects.filter(
            user=user,
            created__date=today
        ).exists():
            raise UseroneConflictException(detail=f"User already made post.")
        
        return data

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = "__all__"
    
    def validate(self, value):
        if (len(value["comment_content"])<15):
            raise CommentException(detail=f"Comment is too short")
        return value
        
class LinkCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LinkCategory
        fields = "__all__"