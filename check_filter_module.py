#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选功能模块检查脚本
检查筛选功能模块的配置、引入、语法等问题
"""

import os
import re
import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "vihhi/weihai_tech_production_system/backend/templates/customer_management"
STATIC_DIR = PROJECT_ROOT / "vihhi/weihai_tech_production_system/backend/static"
JS_DIR = STATIC_DIR / "js"
CSS_DIR = STATIC_DIR / "css/components"

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if file_path.exists():
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description} 不存在: {file_path}")
        return False

def check_template_file(template_name):
    """检查模板文件"""
    template_path = TEMPLATES_DIR / template_name
    
    if not template_path.exists():
        print_error(f"模板文件不存在: {template_path}")
        return False
    
    print_success(f"模板文件存在: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查必要的脚本引入
    required_scripts = [
        ('filter-fields-settings.js', 'filter-fields-settings.js'),
        ('list-filters.js', 'list-filters.js'),
    ]
    
    for script_name, display_name in required_scripts:
        if script_name in content:
            # 检查是否有正确的 script 标签
            pattern = rf'<script[^>]*src=["\']{{% static [\'"]js/{re.escape(script_name)}[\'"] %}}["\'][^>]*></script>'
            if re.search(pattern, content):
                print_success(f"  {display_name} 已正确引入")
            else:
                # 检查是否有 script 标签但格式不对
                if f"static 'js/{script_name}'" in content or f'static "js/{script_name}"' in content:
                    print_warning(f"  {display_name} 引入格式可能有问题")
                    issues.append(f"{display_name} 引入格式可能有问题")
                else:
                    print_error(f"  {display_name} 未引入")
                    issues.append(f"{display_name} 未引入")
        else:
            print_error(f"  {display_name} 未引入")
            issues.append(f"{display_name} 未引入")
    
    # 检查 listFiltersConfig
    if 'listFiltersConfig' in content:
        print_success("  listFiltersConfig 配置存在")
        
        # 检查必要的配置项
        required_configs = [
            'enableFieldsSettings',
            'fieldsSettingsStorageKey',
            'fieldsSettingsContainerId',
            'fieldsSettingsModalId',
            'fieldsSettingsBtnId',
        ]
        
        for config in required_configs:
            if config in content:
                print_success(f"    配置项 {config} 存在")
            else:
                print_warning(f"    配置项 {config} 缺失")
                issues.append(f"配置项 {config} 缺失")
    else:
        print_error("  listFiltersConfig 配置不存在")
        issues.append("listFiltersConfig 配置不存在")
    
    # 检查按钮元素
    if 'settingsFilterFieldsBtn' in content:
        print_success("  设置筛选字段按钮存在")
        
        # 检查按钮是否有 data-bs-toggle（不应该有，会冲突）
        if 'data-bs-toggle="modal"' in content and 'settingsFilterFieldsBtn' in content:
            # 检查是否在同一行
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'settingsFilterFieldsBtn' in line and 'data-bs-toggle' in line:
                    print_warning(f"  按钮在第 {i} 行有 data-bs-toggle 属性（可能冲突）")
                    issues.append(f"按钮有 data-bs-toggle 属性（可能冲突）")
    else:
        print_error("  设置筛选字段按钮不存在")
        issues.append("设置筛选字段按钮不存在")
    
    # 检查模态框
    if 'filterFieldsSettingsModal' in content:
        print_success("  筛选字段设置模态框存在")
    else:
        print_error("  筛选字段设置模态框不存在")
        issues.append("筛选字段设置模态框不存在")
    
    # 检查模态框模板引入
    if 'filter_fields_settings_modal.html' in content:
        print_success("  模态框模板已引入")
    else:
        print_warning("  模态框模板未引入（可能直接在模板中）")
    
    # 检查 script 标签匹配
    open_scripts = len(re.findall(r'<script[^>]*>', content, re.IGNORECASE))
    close_scripts = len(re.findall(r'</script>', content, re.IGNORECASE))
    
    if open_scripts == close_scripts:
        print_success(f"  Script 标签匹配 ({open_scripts} 个)")
    else:
        print_error(f"  Script 标签不匹配: 打开 {open_scripts} 个, 关闭 {close_scripts} 个")
        issues.append(f"Script 标签不匹配: {open_scripts} 打开, {close_scripts} 关闭")
    
    # 检查 {% load static %}
    if '{% load static %}' in content:
        print_success("  {% load static %} 标签存在")
    else:
        print_warning("  {% load static %} 标签不存在（可能在其他地方）")
    
    # 检查 {% block extra_js %}
    if '{% block extra_js %}' in content:
        print_success("  {% block extra_js %} 存在")
    else:
        print_warning("  {% block extra_js %} 不存在（脚本可能在 content block 中）")
    
    return len(issues) == 0, issues

def check_js_file(js_file):
    """检查 JavaScript 文件"""
    js_path = JS_DIR / js_file
    
    if not js_path.exists():
        print_error(f"JavaScript 文件不存在: {js_path}")
        return False
    
    print_success(f"JavaScript 文件存在: {js_path}")
    
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查是否有语法错误（简单检查）
    # 检查括号匹配
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        print_error(f"  大括号不匹配: 打开 {open_braces} 个, 关闭 {close_braces} 个")
        issues.append("大括号不匹配")
    else:
        print_success(f"  大括号匹配 ({open_braces} 个)")
    
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        print_error(f"  小括号不匹配: 打开 {open_parens} 个, 关闭 {close_parens} 个")
        issues.append("小括号不匹配")
    else:
        print_success(f"  小括号匹配 ({open_parens} 个)")
    
    # 检查 filter-fields-settings.js 特定问题
    if js_file == 'filter-fields-settings.js':
        # 检查 z-index 设置
        if 'zIndex' in content or 'z-index' in content:
            # 检查 backdrop 的 z-index
            if re.search(r'backdrop.*zIndex.*1054', content, re.IGNORECASE):
                print_warning("  backdrop z-index 为 1054（可能过高）")
                issues.append("backdrop z-index 可能过高")
            elif re.search(r'backdrop.*zIndex.*1040', content, re.IGNORECASE):
                print_success("  backdrop z-index 为 1040（正确）")
            
            # 检查 modal 的 z-index
            if re.search(r'modalElement.*zIndex.*1055', content, re.IGNORECASE):
                print_warning("  modal z-index 为 1055（可能不够高）")
            elif re.search(r'modalElement.*zIndex.*1050', content, re.IGNORECASE):
                print_success("  modal z-index 为 1050（正确）")
        
        # 检查 pointerEvents
        if 'pointerEvents' in content:
            # 检查 modal 的 pointerEvents
            if re.search(r'modalElement.*pointerEvents.*["\']none["\']', content, re.IGNORECASE):
                print_error("  modal pointerEvents 设置为 'none'（会导致无法交互）")
                issues.append("modal pointerEvents 设置为 'none'")
            elif re.search(r'modalElement.*pointerEvents.*["\']auto["\']', content, re.IGNORECASE):
                print_success("  modal pointerEvents 设置为 'auto'（正确）")
    
    return len(issues) == 0, issues

def check_css_file():
    """检查 CSS 文件"""
    css_path = CSS_DIR / "list-filters.css"
    
    if not css_path.exists():
        print_error(f"CSS 文件不存在: {css_path}")
        return False
    
    print_success(f"CSS 文件存在: {css_path}")
    return True

def check_modal_template():
    """检查模态框模板"""
    modal_path = TEMPLATES_DIR / "includes" / "filter_fields_settings_modal.html"
    
    if modal_path.exists():
        print_success(f"模态框模板存在: {modal_path}")
        
        with open(modal_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的元素
        required_elements = [
            ('filterFieldsSettingsModal', '模态框容器'),
            ('filterFieldsList', '字段列表容器'),
            ('saveFilterFieldsSettings', '保存按钮'),
            ('resetFilterFieldsSettings', '重置按钮'),
        ]
        
        for element_id, description in required_elements:
            if element_id in content:
                print_success(f"  {description} ({element_id}) 存在")
            else:
                print_error(f"  {description} ({element_id}) 不存在")
        
        return True
    else:
        print_warning(f"模态框模板不存在: {modal_path}（可能直接在模板中）")
        return True  # 不算错误，可能直接在模板中

def main():
    """主函数"""
    print_header("筛选功能模块检查脚本")
    
    print_info("检查项目路径...")
    print(f"  项目根目录: {PROJECT_ROOT}")
    print(f"  模板目录: {TEMPLATES_DIR}")
    print(f"  静态文件目录: {STATIC_DIR}")
    
    all_issues = []
    
    # 检查必要的文件
    print_header("1. 检查必要文件")
    
    js_files = [
        ('filter-fields-settings.js', '筛选字段设置脚本'),
        ('list-filters.js', '列表筛选脚本'),
    ]
    
    for js_file, description in js_files:
        if check_file_exists(JS_DIR / js_file, description):
            is_ok, issues = check_js_file(js_file)
            if issues:
                all_issues.extend([f"{description}: {issue}" for issue in issues])
    
    check_css_file()
    check_modal_template()
    
    # 检查模板文件
    print_header("2. 检查模板文件")
    
    template_files = [
        'customer_list.html',
        'customer_public_sea.html',
        'customer_visit.html',
        'contact_list.html',
    ]
    
    for template_file in template_files:
        if (TEMPLATES_DIR / template_file).exists():
            print(f"\n检查 {template_file}:")
            is_ok, issues = check_template_file(template_file)
            if issues:
                all_issues.extend([f"{template_file}: {issue}" for issue in issues])
    
    # 总结
    print_header("3. 检查总结")
    
    if all_issues:
        print_error(f"发现 {len(all_issues)} 个问题：")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        print(f"\n{Colors.RED}❌ 检查失败，请修复上述问题{Colors.RESET}")
        return 1
    else:
        print_success("所有检查通过！")
        print(f"\n{Colors.GREEN}✅ 筛选功能模块配置正确{Colors.RESET}")
        return 0

if __name__ == '__main__':
    sys.exit(main())

