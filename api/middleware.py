from django.conf import settings
from django.http import JsonResponse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 排除登录接口
        if request.path == '/api/login/':
            return self.get_response(request)

        # 检查session中是否有认证信息
        if not request.session.get('is_authenticated'):
            return JsonResponse({'error': '未认证'}, status=401)

        return self.get_response(request) 