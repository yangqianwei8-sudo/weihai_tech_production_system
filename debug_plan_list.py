#!/usr/bin/env python
"""
计划列表显示问题调试脚本
用于排查为什么计划总数为9个，但表格中只显示6个的问题
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/home/devbox/project/vihhi/weihai_tech_production_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')
django.setup()

from django.db.models import Q
from backend.apps.plan_management.models import Plan
from django.core.paginator import Paginator

def debug_plan_list():
    """调试计划列表查询"""
    print("=" * 80)
    print("计划列表调试信息")
    print("=" * 80)
    
    # 1. 检查数据库中的总计划数
    total_plans = Plan.objects.count()
    print(f"\n1. 数据库中的计划总数: {total_plans}")
    
    # 2. 检查所有计划的详细信息
    print("\n2. 所有计划的详细信息:")
    all_plans = Plan.objects.select_related(
        'responsible_person', 'responsible_department', 'related_goal',
        'related_project', 'parent_plan', 'created_by'
    ).prefetch_related('participants').all()
    
    for i, plan in enumerate(all_plans, 1):
        print(f"   [{i}] {plan.plan_number} - {plan.name}")
        print(f"       状态: {plan.get_status_display()} ({plan.status})")
        print(f"       类型: {plan.get_plan_type_display()} ({plan.plan_type})")
        print(f"       周期: {plan.get_plan_period_display()} ({plan.plan_period})")
        print(f"       负责人: {plan.responsible_person.username if plan.responsible_person else 'None'}")
        print(f"       关联目标: {plan.related_goal.name if plan.related_goal else 'None'}")
        print(f"       开始时间: {plan.start_time}")
        print(f"       结束时间: {plan.end_time}")
        print(f"       创建时间: {plan.created_time}")
        print()
    
    # 3. 模拟视图中的查询逻辑（无筛选条件）
    print("3. 模拟视图查询（无筛选条件）:")
    plans_no_filter = Plan.objects.select_related(
        'responsible_person', 'responsible_department', 'related_goal',
        'related_project', 'parent_plan', 'created_by'
    ).prefetch_related('participants').all().order_by('-created_time')
    
    count_no_filter = plans_no_filter.count()
    print(f"   查询结果数量: {count_no_filter}")
    
    # 4. 检查分页逻辑
    print("\n4. 检查分页逻辑:")
    paginator = Paginator(plans_no_filter, 20)
    page_obj = paginator.get_page(1)
    print(f"   总页数: {paginator.num_pages}")
    print(f"   每页数量: {paginator.per_page}")
    print(f"   第1页计划数量: {page_obj.object_list.count()}")
    print(f"   page_obj 中的计划:")
    for i, plan in enumerate(page_obj.object_list, 1):
        print(f"      [{i}] {plan.plan_number} - {plan.name}")
    
    # 5. 检查是否有筛选条件导致过滤
    print("\n5. 检查各种筛选条件的影响:")
    
    # 检查状态筛选
    for status_code, status_name in Plan.STATUS_CHOICES:
        count = Plan.objects.filter(status=status_code).count()
        print(f"   状态 '{status_name}' ({status_code}): {count} 个计划")
    
    # 检查类型筛选
    for type_code, type_name in Plan.PLAN_TYPE_CHOICES:
        count = Plan.objects.filter(plan_type=type_code).count()
        print(f"   类型 '{type_name}' ({type_code}): {count} 个计划")
    
    # 检查周期筛选
    for period_code, period_name in Plan.PLAN_PERIOD_CHOICES:
        count = Plan.objects.filter(plan_period=period_code).count()
        print(f"   周期 '{period_name}' ({period_code}): {count} 个计划")
    
    # 6. 检查是否有计划因为关联关系缺失而被过滤
    print("\n6. 检查关联关系:")
    plans_without_goal = Plan.objects.filter(related_goal__isnull=True).count()
    print(f"   没有关联目标的计划: {plans_without_goal}")
    
    plans_without_responsible = Plan.objects.filter(responsible_person__isnull=True).count()
    print(f"   没有负责人的计划: {plans_without_responsible}")
    
    # 7. 检查是否有计划因为时间问题被过滤
    print("\n7. 检查时间范围:")
    from django.utils import timezone
    now = timezone.now()
    plans_before_now = Plan.objects.filter(start_time__lt=now).count()
    plans_after_now = Plan.objects.filter(start_time__gte=now).count()
    print(f"   开始时间 < 当前时间: {plans_before_now} 个计划")
    print(f"   开始时间 >= 当前时间: {plans_after_now} 个计划")
    
    # 8. 检查是否有计划被软删除或标记为不可见
    print("\n8. 检查是否有特殊标记:")
    # 如果有 is_deleted 或 is_active 字段，检查它们
    # 这里假设没有这些字段，但可以检查其他可能的过滤条件
    
    # 9. 生成SQL查询语句用于调试
    print("\n9. 生成的SQL查询（无筛选）:")
    query = plans_no_filter.query
    print(f"   SQL: {query}")
    
    print("\n" + "=" * 80)
    print("调试完成")
    print("=" * 80)
    
    # 10. 建议检查项
    print("\n建议检查项:")
    print("1. 检查浏览器控制台是否有JavaScript错误")
    print("2. 检查模板中是否有条件过滤（如 {% if %} 语句）")
    print("3. 检查是否有权限过滤导致某些计划不显示")
    print("4. 检查是否有前端JavaScript过滤了部分数据")
    print("5. 检查分页是否正确显示所有页面")

if __name__ == '__main__':
    debug_plan_list()
