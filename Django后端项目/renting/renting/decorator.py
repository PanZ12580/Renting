from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
import jwt

from apiApp.models import User

def auth_permission_required():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            try:
                auth = request.META.get('HTTP_AUTHORIZATION').split()
            except AttributeError:
                return JsonResponse({"code": 401, "message": "未携带token信息"})

            # 用户通过API获取数据验证流程
            if auth[0].lower() == 'token':
                try:
                    dict = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
                    username = dict.get('data').get('username')
                except jwt.ExpiredSignatureError:
                    return JsonResponse({"statusCode": 401, "message": "Token过期"})
                except jwt.InvalidTokenError:
                    return JsonResponse({"statusCode": 401, "message": "无效的token"})
                except Exception as e:
                    return JsonResponse({"statusCode": 401, "message": "无法获取用户身份信息"})

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({"statusCode": 401, "message": "用户不存在"})

            else:
                return JsonResponse({"statusCode": 401, "message": "不支持的认证类型"})

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
