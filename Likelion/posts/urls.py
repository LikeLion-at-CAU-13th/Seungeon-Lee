from django.urls import path
from posts.views import *

urlpatterns = [
    ## path('', hello_world, name = 'hello_world'),
    ## path('page', index, name='my-page'),
    ## path('<int:id>', get_post_detail), # 추가
    ### path('', post_list, name="post_list"),
    ### path('<int:post_id>/', post_detail, name='post_detail'), # Post 단일 조회
    ### path('comment/<int:post_id>/', show_comment, name="show_comment"),
    ### path('filter/<int:category>/', filter_post, name="filter_category")
    
    path('', PostList.as_view()),
    path('<int:post_id>/', PostDetail.as_view()),    
    path('comment/<int:post_id>/', CommentList.as_view()),
    path('filter/<int:category>/', CategoryPost.as_view())
]

