"""
上下文处理器：自动为所有模板提供当前模块的左侧菜单
"""
from backend.apps.system_management.services import get_user_permission_codes


def sidebar_menu(request):
    """
    上下文处理器：根据当前URL路径自动获取对应的左侧菜单
    
    使用方式：
    1. 在 settings.py 的 TEMPLATES['OPTIONS']['context_processors'] 中添加：
       'backend.core.context_processors.sidebar_menu',
    2. 在模板中直接使用 {{ sidebar_menu }} 即可获取当前模块的左侧菜单
    """
    if not request or not request.user.is_authenticated:
        return {'sidebar_menu': []}
    
    try:
        # 如果导入的函数不存在，直接返回空菜单
        # 这样可以避免导入错误导致整个应用无法启动
        try:
            from backend.core.views import _get_current_module_from_path, _get_sidebar_menu_for_module
        except ImportError:
            # 如果函数不存在，返回空菜单
            return {'sidebar_menu': []}
        
        # 获取当前路径
        request_path = request.path
        
        # 判断当前模块
        current_module = _get_current_module_from_path(request_path)
        
        # 如果无法判断模块，返回空菜单
        if not current_module:
            return {'sidebar_menu': []}
        
        # 获取用户权限
        permission_set = get_user_permission_codes(request.user)
        
        # 获取当前模块的左侧菜单
        sidebar_menu_items = _get_sidebar_menu_for_module(
            current_module,
            permission_set,
            request_path,
            request.user
        )
        
        return {'sidebar_menu': sidebar_menu_items}
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f'获取左侧菜单失败: {e}')
        return {'sidebar_menu': []}

