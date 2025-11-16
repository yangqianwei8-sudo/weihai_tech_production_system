from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.urls import reverse

from collections import defaultdict, OrderedDict

from backend.apps.system_management.models import Department, Role, User, PermissionItem
from backend.apps.system_management.serializers import (
    AccountProfileSerializer,
    AccountNotificationSerializer,
    AccountPasswordChangeSerializer,
)
from backend.apps.system_management.services import get_user_permission_codes
from backend.apps.system_management.forms import POSITION_CHOICES


def _context(page_title, page_icon, description, summary_cards=None, sections=None):
    return {
        "page_title": page_title,
        "page_icon": page_icon,
        "description": description,
        "summary_cards": summary_cards or [],
        "sections": sections or [],
    }


@login_required
def account_settings(request):
    user = request.user
    tab = request.GET.get("tab", "profile")
    if tab not in {"profile", "notifications", "security"}:
        tab = "profile"

    profile_errors = {}
    notification_errors = {}
    password_errors = {}

    profile_data = AccountProfileSerializer(instance=user, context={"request": request}).data
    notification_values = user.get_notification_preferences()
    position_choices = POSITION_CHOICES.get(user.user_type, POSITION_CHOICES.get('internal', []))

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "profile":
            payload = {
                "first_name": request.POST.get("first_name", "").strip(),
                "last_name": request.POST.get("last_name", "").strip(),
                "email": request.POST.get("email", "").strip(),
                "position": request.POST.get("position", "").strip(),
            }
            avatar_file = request.FILES.get("avatar")
            if avatar_file:
                payload["avatar"] = avatar_file

            serializer = AccountProfileSerializer(
                instance=user,
                data=payload,
                partial=True,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save()
                messages.success(request, "账号资料已更新。")
                return redirect("system_pages:account_settings")
            profile_errors = serializer.errors
            display_payload = payload.copy()
            display_payload.pop("avatar", None)
            profile_data = {**profile_data, **display_payload}
            tab = "profile"
            messages.error(request, "资料保存失败，请检查填写内容。")

        elif form_type == "notifications":
            payload = {
                "inbox": request.POST.get("inbox") == "on",
                "email": request.POST.get("email") == "on",
                "wecom": request.POST.get("wecom") == "on",
            }
            serializer = AccountNotificationSerializer(data=payload)
            if serializer.is_valid():
                preferences = user.get_notification_preferences()
                preferences.update(serializer.validated_data)
                user.notification_preferences = preferences
                user.save(update_fields=["notification_preferences"])
                messages.success(request, "通知偏好已保存。")
                return redirect(f"{reverse('system_pages:account_settings')}?tab=notifications")
            notification_errors = serializer.errors
            notification_values = payload
            tab = "notifications"
            messages.error(request, "通知偏好保存失败，请至少开启一种通知方式。")

        elif form_type == "password":
            serializer = AccountPasswordChangeSerializer(
                data={
                    "old_password": request.POST.get("old_password", ""),
                    "new_password": request.POST.get("new_password", ""),
                    "confirm_password": request.POST.get("confirm_password", ""),
                },
                context={"request": request},
            )
            if serializer.is_valid():
                user.set_password(serializer.validated_data["new_password"])
                user.save(update_fields=["password"])
                logout(request)
                messages.success(request, "密码已更新，请重新登录。")
                return redirect("login")
            password_errors = serializer.errors
            tab = "security"
            messages.error(request, "密码修改失败，请检查输入内容。")

    roles = user.roles.all().order_by("name")
    permission_codes = sorted(get_user_permission_codes(user))

    context = {
        "user_obj": user,
        "active_tab": tab,
        "profile_data": profile_data,
        "notification_values": notification_values,
        "profile_errors": profile_errors,
        "notification_errors": notification_errors,
        "password_errors": password_errors,
        "roles": roles,
        "permission_codes": permission_codes,
        "position_choices": position_choices,
    }
    return render(request, "system_management/account_settings.html", context)


@login_required
@permission_required("system_management.manage_users", raise_exception=True)
def system_settings(request):
    departments = Department.objects.count()
    users = User.objects.count()
    summary_cards = [
        {"label": "系统用户", "value": users, "hint": "已在系统内开通的账号数量"},
        {"label": "部门结构", "value": departments, "hint": "组织架构中的部门数量"},
        {"label": "角色模板", "value": Role.objects.count(), "hint": "可复用的角色模板数量"},
        {"label": "待处理事项", "value": 0, "hint": "需要管理员关注的系统任务"},
    ]
    context = _context(
        "系统设置",
        "⚙️",
        "配置组织结构、账号策略及平台参数，保障系统稳定运行。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "设置项",
                "description": "常用的系统配置入口。",
                "items": [
                    {"label": "组织架构", "description": "维护部门层级与职责。", "url": "#", "icon": "🏢"},
                    {"label": "安全策略", "description": "配置密码、登录与审计策略。", "url": "#", "icon": "🔐"},
                    {"label": "参数开关", "description": "启用业务功能与自定义阈值。", "url": "#", "icon": "🧩"},
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
@permission_required("system_management.manage_settings", raise_exception=True)
def operation_logs(request):
    summary_cards = [
        {"label": "今日日志", "value": 0, "hint": "今日新增的操作日志条目"},
        {"label": "异常告警", "value": 0, "hint": "捕获的异常告警数量"},
        {"label": "活跃用户", "value": User.objects.filter(is_active=True).count(), "hint": "近期登录的活跃账号"},
        {"label": "审计状态", "value": "正常", "hint": "系统审计功能运行状态"},
    ]
    context = _context(
        "操作日志",
        "🧾",
        "记录系统操作行为与异常告警，为审计与问题排查提供依据。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "日志视图",
                "description": "查看不同维度的日志信息。",
                "items": [
                    {"label": "用户操作", "description": "审计用户关键操作记录。", "url": "#", "icon": "🧑‍💼"},
                    {"label": "系统运行", "description": "监控系统服务运行情况。", "url": "#", "icon": "🖥"},
                    {"label": "异常告警", "description": "处理系统异常与安全告警。", "url": "#", "icon": "🚨"},
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
@permission_required("system_management.manage_settings", raise_exception=True)
def data_dictionary(request):
    summary_cards = [
        {"label": "字典条目", "value": 0, "hint": "系统维护的数据字典项数量"},
        {"label": "待审核更新", "value": 0, "hint": "需要审核的数据字典修改请求"},
        {"label": "引用模块", "value": 0, "hint": "引用数据字典的业务模块数量"},
        {"label": "最近更新", "value": "--", "hint": "字典最近一次更新的时间"},
    ]
    context = _context(
        "数据字典",
        "📚",
        "维护系统基础数据、编码规则与引用关系，为业务表单提供统一标准。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "数据维护",
                "description": "按类别维护和发布字典条目。",
                "items": [
                    {"label": "基础资料", "description": "行业、专业、阶段等基础数据。", "url": "#", "icon": "📘"},
                    {"label": "编码规则", "description": "维护编码方案与生成规则。", "url": "#", "icon": "🧮"},
                    {"label": "版本管理", "description": "管理字典版本与发布记录。", "url": "#", "icon": "🗃"},
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
@permission_required("system_management.manage_users", raise_exception=True)
def permission_matrix(request):
    roles = (
        Role.objects.prefetch_related("custom_permissions")
        .filter(is_active=True)
        .order_by("name")
    )
    permission_items = PermissionItem.objects.filter(is_active=True).order_by(
        "module", "action"
    )

    role_entries = []
    for role in roles:
        perms = sorted(role.custom_permissions.filter(is_active=True), key=lambda item: (item.module, item.action))
        module_summary = OrderedDict()
        for perm in perms:
            module_summary.setdefault(perm.module, []).append(perm)
        role_entries.append(
            {
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "description": role.description,
                "permission_count": len(perms),
                "module_summary": module_summary,
            }
        )

    module_catalog = defaultdict(list)
    for item in permission_items:
        module_catalog[item.module].append(item)

    context = {
        "role_entries": role_entries,
        "module_catalog": sorted(
            ((module, perms) for module, perms in module_catalog.items()),
            key=lambda entry: entry[0],
        ),
        "permission_total": permission_items.count(),
        "role_total": roles.count(),
    }
    return render(request, "system_management/permission_matrix.html", context)
