from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods # 추가
from .models import * # 추가

from .serializers import PostSerializer, CommentSerializer, LinkCategorySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
import json
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from config.permissions import BlockPermission, IsOwnerOrReadOnly

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.core.files.storage import default_storage  
from .serializers import ImageSerializer
from django.conf import settings
import boto3
import uuid

class ImageUploadView(APIView):
    @swagger_auto_schema(
        operation_summary="이미지 업로드",
        operation_description="이미지를 업로드하면 S3에 저장되고, 해당 URL이 DB에 저장됩니다.",
        manual_parameters=[],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['image'],
            properties={
                'image': openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description='업로드할 이미지 파일'
                )
            },
        ),
        responses={
            201: openapi.Response('성공', ImageSerializer),
            400: "잘못된 요청 (이미지가 없음)",
            500: "서버 오류 (S3 업로드 실패)"
        }
    )
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image file"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        unique_filename = f"{uuid.uuid4()}_{image_file.name}"
        file_path = f"uploads/{unique_filename}"

        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=image_file.read(),
                ContentType=image_file.content_type,
            )
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_path}"

        image_instance = Image.objects.create(image_url=image_url)
        serializer = ImageSerializer(image_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# week12
class PostList(APIView):
    @swagger_auto_schema(
        operation_summary="게시글 생성",
        operation_description="새로운 게시글을 생성합니다.",
        request_body=PostSerializer,
        responses={201: PostSerializer, 400: "잘못된 요청"}
    )
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="게시글 목록 조회",
        operation_description="모든 게시글을 조회합니다.",
        responses={200: PostSerializer(many=True)}
    )
    def get(self, request, format=None):
        posts = Post.objects.all()
	    # 많은 post들을 받아오려면 (many=True) 써줘야 한다!
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

## 세션 ##
class PostDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, BlockPermission]

    @swagger_auto_schema(
        operation_summary="게시글 상세 조회",
        operation_description="게시글의 상세 정보를 조회합니다.",
        responses={200: openapi.Response('성공', PostSerializer)},
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="게시글 수정",
        operation_description="게시글을 수정합니다. 인증된 사용자만 가능.",
        request_body=PostSerializer,
        responses={
            200: openapi.Response('수정 성공', PostSerializer),
            400: '유효성 검사 실패'
        }
    )
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="게시글 삭제",
        operation_description="게시글을 삭제합니다. 인증된 사용자만 가능.",
        responses={
            204: '삭제 성공',
            404: '존재하지 않는 게시글'
        }
    )
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentList(APIView):
    @swagger_auto_schema(
        operation_summary="특정 게시글의 댓글 목록 조회",
        operation_description="post_id에 해당하는 게시글에 달린 모든 댓글을 조회합니다.",
        responses={
            200: openapi.Response("성공", CommentSerializer(many=True)),
            404: "게시글이 존재하지 않음"
        }
    )
    def get(self, request, post_id):
        comment = Comment.objects.filter(post=post_id)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)


class CategoryPost(APIView):
    @swagger_auto_schema(
        operation_summary="카테고리별 게시글 목록 조회",
        operation_description="category_id에 해당하는 카테고리의 게시글 목록을 최신순으로 정렬하여 조회합니다.",
        responses={
            200: openapi.Response("성공", LinkCategorySerializer(many=True)),
            404: "카테고리가 존재하지 않음"
        }
    )
    def get(self, request, category):
        linkcategory = LinkCategory.objects.filter(category_id=category).order_by('-post__created')
        serializer = LinkCategorySerializer(linkcategory, many=True)
        return Response(serializer.data)



def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello likelion-13th!"
        })
    
def index(request):
    return render(request, 'index.html')

@require_http_methods(["GET"])
def get_post_detail(reqeust, id):
    post = get_object_or_404(Post, pk=id)
    post_detail_json = {
        "id" : post.id,
        "title" : post.title,
        "content" : post.content,
        "status" : post.status,
        "user" : post.user.username,
    }
    return JsonResponse({
        "status" : 200,
        "data": post_detail_json})
    
@require_http_methods(["POST", "GET"])
def post_list(request):
    
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
   
        user_id = body.get('user')
        user = get_object_or_404(User, pk=user_id)
        
        new_post = Post.objects.create(
            title = body['title'],
            content = body['content'],
            status = body['status'],
            user = user
        )
    
        new_post_json = {
            "id": new_post.id,
            "title" : new_post.title,
            "content": new_post.content,
            "status": new_post.status,
            "user": new_post.user.id
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 생성 성공',
            'data': new_post_json
        })
    
    # 게시글 전체 조회
    if request.method == "GET":
        post_all = Post.objects.all()
    
		# 각 데이터를 Json 형식으로 변환하여 리스트에 저장
        post_json_all = []
        
        for post in post_all:
            post_json = {
                "id": post.id,
                "title" : post.title,
                "content": post.content,
                "status": post.status,
                "user": post.user.id
            }
            post_json_all.append(post_json)

        return JsonResponse({
            'status': 200,
            'message': '게시글 목록 조회 성공',
            'data': post_json_all
        })
        
@require_http_methods(["GET", "PATCH", "DELETE"])
def post_detail(request, post_id):

    # post_id에 해당하는 단일 게시글 조회
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id)

        post_json = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "status": post.status,
            "user": post.user.id,
        }
        
        return JsonResponse({
            'status': 200,
            'message': '게시글 단일 조회 성공',
            'data': post_json
        })
    
    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))
        
        update_post = get_object_or_404(Post, pk=post_id)

        if 'title' in body:
            update_post.title = body['title']
        if 'content' in body:
            update_post.content = body['content']
        if 'status' in body:
            update_post.status = body['status']
    
        
        update_post.save()

        update_post_json = {
            "id": update_post.id,
            "title" : update_post.title,
            "content": update_post.content,
            "status": update_post.status,
            "user": update_post.user.id,
        }

        return JsonResponse({
            'status': 200,
            'message': '게시글 수정 성공',
            'data': update_post_json
        })
    
    if request.method == "DELETE":
        delete_post = get_object_or_404(Post, pk=post_id)
        delete_post.delete()

        return JsonResponse({
                'status': 200,
                'message': '게시글 삭제 성공',
                'data': None
        })
        
@require_http_methods(["GET"])
def show_comment(request, post_id):
    if request.method == "GET":
        comment = Comment.objects.filter(post = post_id)
        
        comment_json_all = []
        
        for comm in comment:
            comm_json = {
                "comment_id" : comm.comment_id,
                "writer" : comm.writer,
                "comment_content" : comm.comment_content,
                "createdtime" : comm.createdtime,
                "updatedtime" : comm.updatedtime
            }
            comment_json_all.append(comm_json)
            
        return JsonResponse({
            'status': 200,
            'message': '특정 게시글에 포함된 모든 comment를 조회',
            'data': comment_json_all
        })
        


@require_http_methods(["GET"])
def filter_post(request, category):
    if request.method == "GET":
        link_qs = LinkCategory.objects.filter(category_id=category).order_by('-post__created')
        filtered_post = [link.post for link in link_qs]
        
        filtered_post_json_all = []
        
        for filt_post in filtered_post :
            filt_json = {
                "id": filt_post.id,
                "title" : filt_post.title,
                "content": filt_post.content,
                "status": filt_post.status,
                "user": filt_post.user.id,
            }
            filtered_post_json_all.append(filt_json)
        
        return JsonResponse({
            'status': 200,
            'message': '카테고리별 POST 조회',
            'data': filtered_post_json_all
        })
        
