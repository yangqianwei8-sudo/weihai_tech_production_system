"""
自动登录中间件 - 绕过登录页面，直接进入dashboard
"""
from django.contrib.auth import get_user_model, login
from django.utils.deprecation import MiddlewareMixin


class AutoLoginMiddleware(MiddlewareMixin):
    """
    自动登录中间件
    如果用户访问admin页面但未登录，自动登录第一个superuser
    """
    
    def process_request(self, request):
        # 只处理admin相关的请求
        if request.path.startswith('/admin/'):
            # 如果用户未登录
            if not request.user.is_authenticated:
                User = get_user_model()
                try:
                    # 尝试获取第一个superuser
                    auto_user = User.objects.filter(is_superuser=True, is_active=True).first()
                    if auto_user:
                        login(request, auto_user)
                    else:
                        # 如果没有superuser，尝试获取第一个staff用户
                        auto_user = User.objects.filter(is_staff=True, is_active=True).first()
                        if auto_user:
                            login(request, auto_user)
                except Exception:
                    # 如果自动登录失败，继续正常流程
                    pass
        
        return None
