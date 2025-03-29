from django.db import models
from accounts.models import User

# Create your models here.
# 추상 클래스 정의
class BaseModel(models.Model): # models.Model을 상속받음
    created = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장
    updated = models.DateTimeField(auto_now=True) # 객체를 저장할 때 날짜와 시간 갱신

    class Meta:
        abstract = True


class Post(BaseModel): # BaseModel을 상속받음

    CHOICES = (
        ('STORED', '보관'),
        ('PUBLISHED', '발행')
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    content = models.TextField()
    status = models.CharField(max_length=15, choices=CHOICES, default='STORED')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')

    def __str__(self):
        return self.title


class Comment(BaseModel):
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    comment_id = models.AutoField(primary_key=True)
    writer = models.CharField(max_length=20)
    comment_content = models.TextField()
    createdtime = models.DateTimeField(auto_now_add=True)
    updatedtime = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.comment_content


class Category(BaseModel):
    
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.category_name


class LinkCategory(BaseModel):
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="linkpost")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="linkcategory")
    
    def __str__(self):
        return f"{self.post.title} - {self.category.category_name}"