from rest_framework.permissions import BasePermission, SAFE_METHODS
from datetime import datetime, time
import pytz

class BlockPermission(BasePermission):
    def has_permission(self, request, view):
        korea_tz = pytz.timezone('Asia/Seoul')
        now = datetime.now(tz=korea_tz).time()

        start_block = time(22, 0)
        end_block = time(7, 0)

        if start_block <= now or now < end_block:
            return False
        return True
    
class IsOwnerOrReadOnly(BasePermission):
    message = '작성자만 수정하거나 삭제할 수 있습니다.'
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.author == request.user 
        