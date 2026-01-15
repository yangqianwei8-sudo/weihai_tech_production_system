#!/usr/bin/env python3
"""
计划管理模块快速功能测试脚本
用于检查代码完整性、配置正确性和基本功能
"""

import os
import re
import sys

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - 文件不存在")
        return False

def check_urls_config():
    """检查URL配置"""
    print_header("URL配置检查")
    
    urls_file = "vihhi/weihai_tech_production_system/backend/apps/plan_management/urls_pages.py"
    if not check_file_exists(urls_file, "URL配置文件"):
        return False
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取路由
    routes = re.findall(r"path\(['\"]([^'\"]+)['\"],\s*views_pages\.(\w+)", content)
    
    print(f"\n找到 {len(routes)} 个路由配置")
    
    # 检查关键路由
    key_routes = {
        'plan_management_home': ['', 'home/'],
        'plan_list': ['plans/'],
        'plan_create': ['plans/create/'],
        'strategic_goal_list': ['strategic-goals/'],
        'strategic_goal_create': ['strategic-goals/create/'],
        'plan_statistics': ['analysis/statistics/'],
        'strategic_goal_track_entry': ['strategic-goals/track/'],
        'strategic_goal_decompose_entry': ['strategic-goals/decompose/'],
        'strategic_goal_track': ['strategic-goals/<int:goal_id>/track/'],
        'strategic_goal_decompose': ['strategic-goals/<int:goal_id>/decompose/'],
    }
    
    all_ok = True
    for view_name, expected_routes in key_routes.items():
        found = False
        for route, view in routes:
            if view == view_name and route in expected_routes:
                found = True
                print(f"  ✓ {route} -> {view_name}")
                break
        if not found:
            print(f"  ❌ 未找到路由: {view_name}")
            all_ok = False
    
    return all_ok

def check_views():
    """检查视图函数"""
    print_header("视图函数检查")
    
    views_file = "vihhi/weihai_tech_production_system/backend/apps/plan_management/views_pages.py"
    if not check_file_exists(views_file, "视图文件"):
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取视图函数
    view_functions = re.findall(r'def\s+(\w+)\(', content)
    public_views = [v for v in view_functions if not v.startswith('_')]
    
    print(f"\n找到 {len(public_views)} 个公共视图函数")
    
    # 检查关键视图函数
    key_views = [
        'plan_management_home',
        'plan_list',
        'plan_create',
        'plan_edit',
        'plan_detail',
        'strategic_goal_list',
        'strategic_goal_create',
        'strategic_goal_edit',
        'strategic_goal_detail',
        'plan_statistics',
        'plan_completion_analysis',
        'plan_goal_achievement',
        'strategic_goal_track',
        'strategic_goal_track_entry',
        'strategic_goal_decompose',
        'strategic_goal_decompose_entry',
    ]
    
    all_ok = True
    for view in key_views:
        if view in public_views:
            print(f"  ✓ {view}")
        else:
            print(f"  ❌ {view} - 缺失")
            all_ok = False
    
    return all_ok

def check_templates():
    """检查模板文件"""
    print_header("模板文件检查")
    
    templates_dir = "vihhi/weihai_tech_production_system/backend/templates/plan_management"
    goal_templates_dir = "vihhi/weihai_tech_production_system/backend/templates/goal_management"
    
    key_templates = {
        templates_dir: [
            'plan_list.html',
            'plan_form.html',
            'plan_detail.html',
            'plan_statistics.html',
            'plan_completion_analysis.html',
            'plan_goal_achievement.html',
            'plan_approval_list.html',
            'plan_execution_track.html',
            'strategic_goal_list.html',
            'strategic_goal_form.html',
            'strategic_goal_detail.html',
            'strategic_goal_decompose.html',
            'strategic_goal_track.html',
        ],
        goal_templates_dir: [
            'goal_list.html',
            'goal_form.html',
            'goal_detail.html',
        ]
    }
    
    all_ok = True
    for template_dir, templates in key_templates.items():
        dir_name = os.path.basename(template_dir)
        print(f"\n{dir_name}/:")
        for template in templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                print(f"  ✓ {template}")
            else:
                print(f"  ❌ {template} - 文件不存在")
                all_ok = False
    
    return all_ok

def check_static_files():
    """检查静态文件"""
    print_header("静态文件检查")
    
    css_files = [
        "vihhi/weihai_tech_production_system/backend/static/css/components/list_layout.css",
        "vihhi/weihai_tech_production_system/backend/static/css/components/tables.css",
    ]
    
    all_ok = True
    for css_file in css_files:
        if os.path.exists(css_file):
            # 检查是否包含目标编号样式
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'code' in content and 'color' in content:
                print(f"  ✓ {os.path.basename(css_file)} - 包含code样式")
            else:
                print(f"  ⚠️  {os.path.basename(css_file)} - 可能缺少code样式")
        else:
            print(f"  ❌ {os.path.basename(css_file)} - 文件不存在")
            all_ok = False
    
    return all_ok

def check_template_syntax():
    """检查模板语法"""
    print_header("模板语法检查")
    
    templates_to_check = [
        "vihhi/weihai_tech_production_system/backend/templates/goal_management/goal_list.html",
        "vihhi/weihai_tech_production_system/backend/templates/goal_management/goal_detail.html",
        "vihhi/weihai_tech_production_system/backend/templates/goal_management/goal_form.html",
    ]
    
    all_ok = True
    for template in templates_to_check:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            errors = []
            if content.count('{%') != content.count('%}'):
                errors.append("模板标签不匹配")
            if content.count('{{') != content.count('}}'):
                errors.append("变量标签不匹配")
            
            if errors:
                print(f"  ❌ {os.path.basename(template)}: {', '.join(errors)}")
                all_ok = False
            else:
                print(f"  ✓ {os.path.basename(template)}")
        else:
            print(f"  ⚠️  {os.path.basename(template)} - 文件不存在")
    
    return all_ok

def check_url_view_mapping():
    """检查URL和视图的映射关系"""
    print_header("URL与视图映射检查")
    
    urls_file = "vihhi/weihai_tech_production_system/backend/apps/plan_management/urls_pages.py"
    views_file = "vihhi/weihai_tech_production_system/backend/apps/plan_management/views_pages.py"
    
    if not os.path.exists(urls_file) or not os.path.exists(views_file):
        print("❌ 无法检查：缺少必要文件")
        return False
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls_content = f.read()
    
    with open(views_file, 'r', encoding='utf-8') as f:
        views_content = f.read()
    
    # 提取URL中的视图函数名
    url_views = set(re.findall(r'views_pages\.(\w+)', urls_content))
    
    # 提取视图文件中的函数名
    view_functions = set(re.findall(r'def\s+(\w+)\(', views_content))
    public_views = {v for v in view_functions if not v.startswith('_')}
    
    # 检查URL引用的视图是否存在
    missing_in_views = url_views - public_views
    
    if missing_in_views:
        print(f"❌ URL中引用了不存在的视图函数: {', '.join(missing_in_views)}")
        return False
    else:
        print(f"✓ 所有 {len(url_views)} 个URL引用的视图函数都存在")
        return True

def main():
    """主函数"""
    print_header("计划管理模块功能测试")
    print("测试时间: 2025-01-14")
    print("测试范围: 代码完整性、配置正确性、基本功能")
    
    results = {
        'URL配置': check_urls_config(),
        '视图函数': check_views(),
        '模板文件': check_templates(),
        '静态文件': check_static_files(),
        '模板语法': check_template_syntax(),
        'URL视图映射': check_url_view_mapping(),
    }
    
    print_header("测试结果汇总")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for name, result in results.items():
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {total} 项")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    
    if failed == 0:
        print("\n✅ 所有检查项通过！可以进行实际功能测试。")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 项检查未通过，请修复后再进行测试。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
