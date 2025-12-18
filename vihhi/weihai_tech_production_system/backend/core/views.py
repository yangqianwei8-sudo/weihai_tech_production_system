from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.urls import reverse, NoReverseMatch

from backend.apps.project_center.models import Project, ProjectMilestone, ProjectTeamNotification, ProjectTask
from backend.apps.system_management.services import get_user_permission_codes


def _permission_granted(required_code, user_permissions: set) -> bool:
    if not required_code:
        return True
    # 检查是否有所有权限
    if '__all__' in user_permissions:
        return True
    if required_code in user_permissions:
        return True
    if isinstance(required_code, str) and required_code.endswith('.view_assigned'):
        return required_code.replace('view_assigned', 'view_all') in user_permissions
    return False

HOME_ACTION_DEFINITIONS = [
    {
        "id": "project_create",
        "label": "新建项目",
        "icon": "➕",
        "url_name": "production_pages:project_create",
        "permission": "production_management.create",
    },
    {
        "id": "project_monitor",
        "label": "项目监控",
        "icon": "📊",
        "url_name": "production_pages:project_list",
        "permission": "production_management.view_all",
    },
    {
        "id": "schedule_meeting",
        "label": "安排会议",
        "icon": "🗓",
        "url_name": None,
        "permission": "task_collaboration.assign",
    },
]

# 菜单结构：直接对应home页左侧菜单，取消所有"中心"概念
HOME_NAV_STRUCTURE = [
    # 按数据库模块定义顺序排列，确保与数据库一致
    {'label': '客户管理', 'icon': '👥', 'url_name': 'business_pages:customer_management_home', 'permission': 'customer_management.client.view'},
    {'label': '商机管理', 'icon': '💼', 'url_name': 'business_pages:opportunity_management', 'permission': 'customer_success.opportunity.view'},
    {'label': '合同管理', 'icon': '📄', 'url_name': 'business_pages:contract_management_list', 'permission': 'customer_management.contract.view'},
    {'label': '回款管理', 'icon': '💰', 'url_name': 'settlement_pages:payment_plan_list', 'permission': 'payment_management.payment_plan.view'},  # 回款管理独立模块
    {'label': '生产管理', 'icon': '🏗️', 'url_name': 'production_pages:project_list', 'permission': 'production_management.view_assigned'},
    {'label': '生产质量', 'icon': '🔍', 'url_name': 'production_quality_pages:opinion_review', 'permission': 'production_quality.view'},
    {'label': '资源管理', 'icon': '🗂️', 'url_name': 'resource_standard_pages:standard_list', 'permission': 'resource_center.view'},
    {'label': '任务协作', 'icon': '🤝', 'url_name': 'collaboration_pages:task_board', 'permission': 'task_collaboration.view'},
    {'label': '交付管理', 'icon': '📦', 'url_name': 'delivery_pages:report_delivery', 'permission': 'delivery_center.view'},
    {'label': '档案管理', 'icon': '📁', 'url_name': 'archive_management:archive_list', 'permission': 'archive_management.view'},
    {'label': '计划管理', 'icon': '📅', 'url_name': 'plan_pages:plan_list', 'permission': 'plan_management.view'},
    {'label': '诉讼管理', 'icon': '⚖️', 'url_name': 'litigation_pages:litigation_home', 'permission': 'litigation_management.view'},
    {'label': '风险管理', 'icon': '⚠️', 'url_name': '#', 'permission': 'risk_management.view'},  # 占位，待实现
    {'label': '财务管理', 'icon': '💵', 'url_name': 'finance_pages:financial_home', 'permission': 'financial_management.view'},
    {'label': '人事管理', 'icon': '👤', 'url_name': 'personnel_pages:personnel_home', 'permission': 'personnel_management.view'},
    {'label': '行政管理', 'icon': '🏢', 'url_name': 'admin_pages:administrative_home', 'permission': 'administrative_management.view'},
    {'label': '系统管理', 'icon': '⚙️', 'url_name': 'system_pages:system_settings', 'permission': 'system_management.view'},
    # 注意：权限管理仅保留在Django Admin后台管理中，不添加到前端导航栏
]


def _build_full_top_nav(permission_set, user=None):
    """构建完整的顶部导航菜单
    
    Args:
        permission_set: 用户权限集合
        user: 当前用户对象（可选）
    
    Returns:
        list: 导航菜单项列表
    """
    nav = []
    for item in HOME_NAV_STRUCTURE:
        # 检查权限
        if item.get('permission'):
            if not _permission_granted(item['permission'], permission_set):
                continue
        
        # 构建URL
        url = '#'
        if item.get('url_name'):
            try:
                url = reverse(item['url_name'])
            except NoReverseMatch:
                url = item.get('url', '#')
        else:
            url = item.get('url', '#')
        
        nav.append({
            'label': item['label'],
            'icon': item.get('icon', ''),
            'url': url,
        })
    
    return nav


def _serialize_task_for_home(task):
    project = task.project
    project_number = project.project_number if project else ''
    project_name = project.name if project else '关联项目'
    
    # 根据任务类型设置跳转URL
    url = '#'
    if project:
        if task.task_type == 'project_complete_info':
            # 完善项目信息 -> 跳转到项目信息完善页面
            url = reverse('production_pages:project_complete', args=[project.id])
        elif task.task_type == 'configure_team':
            # 配置项目团队 -> 跳转到团队配置页面
            url = reverse('production_pages:project_team', args=[project.id])
        else:
            # 其他任务 -> 跳转到项目详情页面
            url = reverse('production_pages:project_detail', args=[project.id])
    
    return {
        'id': task.id,
        'title': task.title,
        'project_name': project_name,
        'project_number': project_number,
        'status': task.status,
        'status_label': task.get_status_display(),
        'due_time': task.due_time,
        'completed_time': getattr(task, 'completed_time', None),
        'description': task.description,
        'url': url,
    }


def home(request):
    """系统首页 - Django工作台页面"""
    from django.contrib.auth.decorators import login_required
    from django.db.models import Count, Q, Sum
    from datetime import timedelta
    
    # 如果未登录，重定向到登录页
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    permission_set = get_user_permission_codes(user)
    
    # 构建导航菜单（centers_navigation）
    centers_navigation = _build_full_top_nav(permission_set, user)
    
    # 初始化统计数据
    pending_counts = {'personal': 0, 'due_today': 0, 'overdue': 0}
    approval_stats = {'my_pending': 0, 'my_submitted': 0}
    delivery_stats = {'pending': 0}
    stats_cards = []
    task_board = {'pending': [], 'in_progress': [], 'completed': []}
    
    # 获取待办任务统计
    try:
        today = timezone.now().date()
        user_tasks = ProjectTask.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).exclude(status='completed')
        
        pending_counts['personal'] = user_tasks.count()
        pending_counts['due_today'] = user_tasks.filter(due_time__date=today).count()
        pending_counts['overdue'] = user_tasks.filter(due_time__lt=timezone.now()).exclude(status='completed').count()
        
        # 构建任务看板
        pending_tasks = user_tasks.filter(status='pending')[:10]
        in_progress_tasks = user_tasks.filter(status='in_progress')[:10]
        completed_tasks = ProjectTask.objects.filter(
            Q(assigned_to=user) | Q(created_by=user),
            status='completed'
        ).order_by('-completed_time')[:10]
        
        task_board['pending'] = [_serialize_task_for_home(task) for task in pending_tasks]
        task_board['in_progress'] = [_serialize_task_for_home(task) for task in in_progress_tasks]
        task_board['completed'] = [_serialize_task_for_home(task) for task in completed_tasks]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('获取任务统计失败: %s', str(e))
    
    # 获取审批统计
    try:
        from backend.apps.workflow_engine.models import ApprovalInstance
        
        approval_stats['my_pending'] = ApprovalInstance.objects.filter(
            status='pending',
            records__approver=user,
            records__result='pending'
        ).distinct().count()
        
        approval_stats['my_submitted'] = ApprovalInstance.objects.filter(
            applicant=user
        ).count()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('获取审批统计失败: %s', str(e))
    
    # 获取交付统计
    try:
        from backend.apps.delivery_customer.models import DeliveryReport
        
        delivery_stats['pending'] = DeliveryReport.objects.filter(
            status='pending'
        ).count()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('获取交付统计失败: %s', str(e))
    
    # 构建统计卡片
    try:
        # 进行中项目数
        try:
            active_projects = Project.objects.filter(
                status__in=['in_progress', 'planning']
            ).count()
            stats_cards.append({
                'label': '进行中项目',
                'value': active_projects,
                'url': reverse('production_pages:project_list'),
                'variant': 'info'
            })
        except Exception:
            pass
        
        # 本月完成项目数
        try:
            this_month = timezone.now().replace(day=1)
            completed_projects = Project.objects.filter(
                status='completed',
                updated_time__gte=this_month
            ).count()
            stats_cards.append({
                'label': '本月完成',
                'value': completed_projects,
                'url': reverse('production_pages:project_list'),
                'variant': 'success'
            })
        except Exception:
            pass
        
        # 待审批任务
        if approval_stats['my_pending'] > 0:
            stats_cards.append({
                'label': '待审批',
                'value': approval_stats['my_pending'],
                'url': '#',
                'variant': 'danger'
            })
        
        # 待处理事项
        try:
            from backend.apps.administrative_management.models import AdministrativeAffair
            pending_affairs = AdministrativeAffair.objects.filter(
                status='pending',
                responsible_user=user
            ).count()
            if pending_affairs > 0:
                stats_cards.append({
                    'label': '待处理事项',
                    'value': pending_affairs,
                    'url': reverse('admin_pages:affair_list'),
                    'variant': 'warning'
                })
        except Exception:
            pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('构建统计卡片失败: %s', str(e))
    
    # 构建上下文
    context = {
        'user': user,
        'is_superuser': user.is_superuser,
        'centers_navigation': centers_navigation,
        'pending_counts': pending_counts,
        'approval_stats': approval_stats,
        'delivery_stats': delivery_stats,
        'stats_cards': stats_cards,
        'task_board': task_board,
    }
    
    return render(request, 'home.html', context)


def login_view(request):
    """登录页面 - 返回前端Vue登录页面，统一使用Vue登录"""
    # 统一使用Vue登录页面，Django模板登录已暂时注释
    # 无论是否登录，都返回前端页面，由前端路由处理登录逻辑
    import os
    from django.conf import settings
    from django.http import HttpResponse

    # 前端构建文件路径
    frontend_dist_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'dist', 'index.html')

    if os.path.exists(frontend_dist_path):
        # 如果前端构建文件存在，返回前端页面
        with open(frontend_dist_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    else:
        # 如果前端构建文件不存在，返回一个简单的提示页面
        return HttpResponse('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>维海科技信息化管理平台 - 登录</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>维海科技信息化管理平台</h1>
            <p>前端页面未找到，请先构建前端应用。</p>
            <p><a href="/admin/login/">访问后台管理登录</a></p>
        </body>
        </html>
        ''', content_type='text/html')

    # ========== Django模板登录（已暂时注释）==========
    # if request.user.is_authenticated:
    #     # 已登录用户，根据next参数决定重定向目标
    #     next_url = request.GET.get('next', '')
    #     if next_url and ('admin' in next_url or next_url.startswith('/admin')):
    #         return redirect('admin:index')
    #     else:
    #         return redirect('home')  # 重定向到前端首页
    #
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #
    #     if username and password:
    #         user = authenticate(request, username=username, password=password)
    #         if user:
    #             if user.is_active:
    #                 login(request, user)
    #                 if not user.profile_completed:
    #                     return redirect('complete_profile')
    #                 
    #                 # 根据next参数决定重定向目标
    #                 next_url = request.GET.get('next', 'home')
    #                 if next_url and ('admin' in next_url or next_url.startswith('/admin')):
    #                     # 如果next包含admin，重定向到后台管理
    #                     return redirect('admin:index')
    #                 else:
    #                     # 否则重定向到前端首页
    #                     return redirect('home')
    #             else:
    #                 messages.error(request, '用户账户已被禁用')
    #         else:
    #             messages.error(request, '用户名或密码错误')
    #     else:
    #         messages.error(request, '请输入用户名和密码')
    #
    # return render(request, 'login.html')


def logout_view(request):
    """登出页面"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('login')


@csrf_exempt
def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        'status': 'healthy',
        'service': '维海科技信息化管理平台',
        'version': '1.0.0',
        'timestamp': '2025-11-06T14:01:28Z'
    })


def favicon_view(request):
    """Favicon视图"""
    from django.http import HttpResponse
    from django.conf import settings
    import os
    
    favicon_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else '', 'favicon.ico')
    if os.path.exists(favicon_path):
        with open(favicon_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/x-icon')
    return HttpResponse(status=204)


def test_admin_page(request):
    """测试admin页面"""
    return redirect('admin:index')


def django_service_control(request):
    """Django服务控制"""
    return JsonResponse({'status': 'ok'})
