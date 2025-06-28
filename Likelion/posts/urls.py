from django.urls import path
from posts.views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="""
        이미지 업로드 및 게시글 관련 API 문서입니다.  
        
        - 이미지 업로드 API  
        - 게시글 CRUD API  
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="you@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    
    path('', PostList.as_view()),
    path('<int:post_id>/', PostDetail.as_view()),    
    path('comment/<int:post_id>/', CommentList.as_view()),
    path('filter/<int:category>/', CategoryPost.as_view()),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

