from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from backend.apps.customer_success.models import (
    BusinessContract,
    BusinessPaymentPlan,
    Client,
    ClientProject,
)


def _context(page_title, page_icon, description, summary_cards=None, sections=None):
    return {
        "page_title": page_title,
        "page_icon": page_icon,
        "description": description,
        "summary_cards": summary_cards or [],
        "sections": sections or [],
    }


@login_required
def customer_management(request):
    clients = Client.objects.all()
    summary_cards = [
        {"label": "客户总数", "value": clients.count(), "hint": "系统中维护的客户数量"},
        {
            "label": "活跃客户",
            "value": clients.filter(is_active=True).count(),
            "hint": "状态为活跃的客户数量",
        },
        {
            "label": "VIP 客户",
            "value": clients.filter(client_level="vip").count(),
            "hint": "高价值客户数量",
        },
        {
            "label": "累计合同额",
            "value": f"¥{clients.aggregate(total=Sum('total_contract_amount'))['total'] or Decimal('0'):,.0f}",
            "hint": "录入客户的合同金额汇总",
        },
    ]
    top_clients = clients.order_by("-total_contract_amount")[:6]
    section_items = [
        {
            "label": client.name,
            "description": f"合同额 ¥{client.total_contract_amount:,.0f} · 回款 ¥{client.total_payment_amount:,.0f}",
            "url": "#",
            "icon": "🏢",
        }
        for client in top_clients
    ]
    context = _context(
        "客户管理",
        "🧾",
        "集中维护客户信息、联系人及信用情况，为项目交付与商务沟通提供支持。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "重点客户",
                "description": "合同金额排名靠前的客户。",
                "items": section_items or [
                    {
                        "label": "暂无客户数据",
                        "description": "请先录入客户基本信息。",
                        "url": "#",
                        "icon": "ℹ️",
                    }
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
def contract_management(request):
    projects = ClientProject.objects.select_related("client", "project").order_by("-created_time")[:6]
    payment_summary = BusinessPaymentPlan.objects.aggregate(
        planned_total=Sum("planned_amount"), actual_total=Sum("actual_amount")
    )
    summary_cards = [
        {"label": "合同项目", "value": projects.count(), "hint": "客户合同关联的项目数量"},
        {
            "label": "计划回款",
            "value": f"¥{payment_summary['planned_total'] or Decimal('0'):,.0f}",
            "hint": "累计计划回款金额",
        },
        {
            "label": "已回款",
            "value": f"¥{payment_summary['actual_total'] or Decimal('0'):,.0f}",
            "hint": "已确认到账的回款金额",
        },
        {
            "label": "回款进度",
            "value": _calc_progress(payment_summary),
            "hint": "已回款金额占计划金额的比例",
        },
    ]
    section_items = [
        {
            "label": f"{record.client.name} · {record.project.project_number if record.project else '未关联'}",
            "description": f"合同金额 ¥{record.contract_amount:,.0f} · 状态 {record.status}",
            "url": "#",
            "icon": "📑",
        }
        for record in projects
    ]
    context = _context(
        "合同管理",
        "📃",
        "跟踪合同执行情况、回款进度及关键商务节点。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "合同详情",
                "description": "最近签署的合同与进展情况。",
                "items": section_items or [
                    {
                        "label": "暂无合同数据",
                        "description": "请同步合同与回款计划信息。",
                        "url": "#",
                        "icon": "ℹ️",
                    }
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
def project_settlement(request):
    settlements = BusinessPaymentPlan.objects.select_related("contract__project")
    status_counts = settlements.values("status").annotate(total=Count("id"))
    status_map = {row["status"]: row["total"] for row in status_counts}
    summary_cards = [
        {"label": "待结算", "value": status_map.get("pending", 0), "hint": "尚未启动结算流程的节点"},
        {"label": "结算中", "value": status_map.get("partial", 0) + status_map.get("overdue", 0), "hint": "正在核对或逾期的结算节点"},
        {"label": "已结算", "value": status_map.get("completed", 0), "hint": "结算完成并归档的节点"},
        {
            "label": "结算项目",
            "value": settlements.values("project_id").distinct().count(),
            "hint": "涉及结算流程的项目数量",
        },
    ]
    latest_settlements = settlements.order_by("-planned_date")[:6]
    section_items = []
    for plan in latest_settlements:
        project = plan.contract.project if plan.contract and plan.contract.project_id else None
        section_items.append({
            'label': f"{project.project_number if project else '未关联'} · {plan.phase_name}",
            'description': f"计划金额 ¥{plan.planned_amount:,.0f} · 状态 {plan.get_status_display()}",
            'url': '#',
            'icon': '💰',
        })
    context = _context(
        "项目结算",
        "🧾",
        "统筹项目回款计划、结算单以及内部核算任务。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "结算进度",
                "description": "按项目维度查看结算节点和状态。",
                "items": section_items or [
                    {
                        "label": "暂无结算数据",
                        "description": "尚未创建结算计划。",
                        "url": "#",
                        "icon": "ℹ️",
                    }
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
def output_analysis(request):
    contracts = BusinessContract.objects.select_related('project')
    payments = BusinessPaymentPlan.objects.all()
    total_contract = contracts.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_payment = payments.aggregate(total=Sum('actual_amount'))['total'] or Decimal('0')
    summary_cards = [
        {"label": "合同数量", "value": contracts.count(), "hint": "已录入的商务合同数量"},
        {"label": "合同金额", "value": f"¥{total_contract:,.0f}", "hint": "合同金额汇总"},
        {"label": "已回款", "value": f"¥{total_payment:,.0f}", "hint": "实际到账金额"},
        {"label": "回款进度", "value": _calc_ratio(total_payment, total_contract), "hint": "回款金额占合同金额比例"},
    ]
    context = _context(
        "产值分析",
        "📊",
        "汇总商务合同与回款数据，为经营分析提供支持。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "常用报表",
                "description": "产值分析所需的核心报表与数据视图。",
                "items": [
                    {"label": "合同执行情况", "description": "查看合同签订、变更与执行情况。", "url": "#", "icon": "📑"},
                    {"label": "回款趋势分析", "description": "跟踪月度回款走势与贡献度。", "url": "#", "icon": "📈"},
                    {"label": "客户贡献榜", "description": "识别合同金额贡献度较高的客户。", "url": "#", "icon": "🏆"},
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


@login_required
def payment_tracking(request):
    plans = BusinessPaymentPlan.objects.select_related("contract__project").order_by("planned_date")[:8]
    outstanding = sum(
        max((plan.planned_amount or Decimal("0")) - (plan.actual_amount or Decimal("0")), Decimal("0"))
        for plan in plans
        if plan.status in {"pending", "partial", "overdue"}
    )
    summary_cards = [
        {"label": "待回款金额", "value": f"¥{outstanding:,.0f}", "hint": "尚未到账的计划金额"},
        {"label": "提醒节点", "value": plans.filter(status="pending").count(), "hint": "需要提醒的回款节点"},
        {"label": "已到账节点", "value": plans.filter(status="completed").count(), "hint": "已完成收款的节点数量"},
        {
            "label": "本月到期",
            "value": plans.filter(planned_date__month=timezone.now().month).count(),
            "hint": "本月即将到期的回款计划数量",
        },
    ]
    section_items = []
    for plan in plans:
        project = plan.contract.project if plan.contract and plan.contract.project_id else None
        section_items.append({
            'label': f"{project.project_number if project else '未关联'} · {plan.phase_name}",
            'description': f"计划金额 ¥{plan.planned_amount:,.0f} · 状态 {plan.get_status_display()}",
            'url': '#',
            'icon': '⏰',
        })
    context = _context(
        "收款跟踪",
        "💵",
        "统一跟踪项目回款节点、提醒通知与实际到账情况。",
        summary_cards=summary_cards,
        sections=[
            {
                "title": "回款计划",
                "description": "重点关注即将到期的回款与提醒。",
                "items": section_items or [
                    {
                        "label": "暂无回款计划",
                        "description": "请在项目中配置回款计划。",
                        "url": "#",
                        "icon": "ℹ️",
                    }
                ],
            }
        ],
    )
    return render(request, "shared/center_dashboard.html", context)


def _calc_progress(summary):
    expected = summary.get("planned_total") or Decimal("0")
    actual = summary.get("actual_total") or Decimal("0")
    if expected == 0:
        return "--"
    return f"{(actual / expected * 100):.0f}%"


def _calc_ratio(value, base):
    if not base:
        return "--"
    return f"{(value / base * 100):.1f}%"

