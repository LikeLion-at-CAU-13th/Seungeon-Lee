### Model Serializer case

from rest_framework import serializers
from .models import Post
from .models import Comment
from .models import LinkCategory
from .models import Image
from config.custom_api_exceptions import PostConflictException

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None

        # 1. 중복 제목 검사
        if Post.objects.filter(title=data['title']).exists():
            raise serializers.ValidationError({
                'title': f"'{data['title']}' 제목의 게시글이 이미 존재합니다."
            })

        # 2. 하루 1개 게시글 제한 (오늘 날짜 기준)
        if user and Post.objects.filter(
            user=user,
            created__date=timezone.now().date()
        ).exists():
            raise serializers.ValidationError({
                'non_field_errors': ["하루에 하나의 게시글만 작성할 수 있습니다."]
            })

        return data
        
class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = "__all__"
    
    def validate_content(self, value):
        if len(value.strip()) < 15:
            raise serializers.ValidationError("댓글은 최소 15자 이상 작성해야 합니다.")
        return value
        
class LinkCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LinkCategory
        fields = "__all__"