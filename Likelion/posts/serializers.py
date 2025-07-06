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
	# 어떤 모델을 시리얼라이즈할 건지
        model = Post
        # 모델에서 어떤 필드를 가져올지
        # 전부 가져오고 싶을 때
        fields = "__all__"
    
    # 예외 처리 (필드 단위 체크)
    def validate(self, data):
        if Post.objects.filter(title=data['title']).exists():
            raise serializers.ValidationError({
                'title': f"'{data['title']}' 제목의 게시글이 이미 존재합니다."
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