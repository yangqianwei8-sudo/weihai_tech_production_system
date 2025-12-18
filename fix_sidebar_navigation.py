#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量改造所有模块的导航栏为标准格式
"""

import re
import os
from pathlib import Path

BASE_DIR = Path("/home/devbox/project/vihhi/weihai_tech_production_system/backend/templates")

def replace_sidebar_html(content, menu_var_name):
    """替换导航栏HTML结构为标准格式"""
    
    # 匹配各种可能的导航栏结构模式
    patterns = [
        # 模式1: workspace-nav + customer-sidebar/production-sidebar等
        (r'<aside[^>]*class="[^"]*workspace-nav[^"]*(?:customer|production|personnel|administrative|delivery|contract|opportunity)-sidebar[^"]*"[^>]*>.*?</aside>', 
         create_new_nav_html(menu_var_name)),
        
        # 模式2: sidenav-group结构
        (r'<div class="sidenav-group">\s*<div class="sidenav-group-header">.*?</div>\s*<div class="sidenav-group-children"[^>]*>.*?</div>\s*</div>',
         None),  # 这个会在主替换中处理
    ]
    
    # 主要替换：将sidenav-group结构改为sidenav-item + submenu
    # 查找所有包含sidenav-group的导航栏块
    nav_pattern = r'(<aside[^>]*class="[^"]*workspace-nav[^"]*"[^>]*>.*?</aside>)'
    
    def replace_nav_block(match):
        nav_html = match.group(1)
        
        # 如果是旧的sidenav-group结构，替换为标准结构
        if 'sidenav-group' in nav_html:
            # 提取菜单变量名
            menu_match = re.search(r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}', nav_html)
            if menu_match:
                loop_var = menu_match.group(1)
                menu_var = menu_match.group(2)
                
                # 构建新的导航栏HTML
                new_html = f'''            <aside class="workspace-nav">
                <nav class="sidenav">
                    <div class="sidenav-section">
                        <div class="sidenav-links">
                        {% if {menu_var} %}
                            {% for {loop_var} in {menu_var} %}
                            <div class="sidenav-item {% if {loop_var}.active or {loop_var}.expanded %}expanded{% endif %}">
                                <a class="sidenav-link" 
                                   href="{% if {loop_var}.url %}{{{{{ {loop_var}.url }}}}}{% else %}#{% endif %}" 
                                   {% if {loop_var}.active %}data-active="true"{% endif %}>
                                    {% if {loop_var}.icon %}<span>{{{{{{ {loop_var}.icon }}}}}}</span>{% endif %}
                                    <span>{{{{{{ {loop_var}.label }}}}}}</span>
                                    {% if {loop_var}.children %}<span class="menu-arrow">▶</span>{% endif %}
                                </a>
                                {% if {loop_var}.children %}
                                <div class="submenu">
                                    {% for child in {loop_var}.children %}
                                    <a class="sidenav-link sidenav-sub-link" 
                                       href="{{{{{{ child.url }}}}}}" 
                                       {% if child.active %}data-active="true"{% endif %}>
                                        {% if child.icon %}<span>{{{{{{ child.icon }}}}}}</span>{% endif %}
                                        <span>{{{{{{ child.label }}}}}}</span>
                                    </a>
                                    {% endfor %}
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="alert alert-info m-3">
                                <i class="bi bi-info-circle me-2"></i>
                                暂无可用菜单
                            </div>
                        {% endif %}
                        </div>
                    </div>
                </nav>
            </aside>'''
                
                return new_html
        
        return nav_html
    
    # 执行替换
    content = re.sub(nav_pattern, replace_nav_block, content, flags=re.DOTALL)
    
    # 替换sidenav-group为标准结构（如果在主替换中没处理）
    content = re.sub(
        r'<div class="sidenav-group">\s*<div class="sidenav-group-header">\s*<span[^>]*>{{([^}]+)}}</span>\s*</div>\s*<div class="sidenav-group-children"[^>]*>(.*?)</div>\s*</div>',
        r'<div class="sidenav-item expanded">\n                                <a class="sidenav-link" href="#">\n                                    <span>\1</span>\n                                    <span class="menu-arrow">▶</span>\n                                </a>\n                                <div class="submenu">\2</div>\n                            </div>',
        content,
        flags=re.DOTALL
    )
    
    # 替换active类为data-active属性
    content = re.sub(
        r'class="[^"]*\bactive\b[^"]*"',
        lambda m: m.group(0).replace('active', '').strip().replace('class=""', '') + ' data-active="true"',
        content
    )
    
    # 移除额外的类名
    content = re.sub(
        r'(customer|production|personnel|administrative|delivery|contract|opportunity)-(sidebar|nav)',
        '',
        content
    )
    
    return content

def create_new_nav_html(menu_var_name):
    """创建新的导航栏HTML"""
    return f'''            <aside class="workspace-nav">
                <nav class="sidenav">
                    <div class="sidenav-section">
                        <div class="sidenav-links">
                        {% if {menu_var_name} %}
                            {% for menu_group in {menu_var_name} %}
                            <div class="sidenav-item {% if menu_group.active or menu_group.expanded %}expanded{% endif %}">
                                <a class="sidenav-link" 
                                   href="{% if menu_group.url %}{{{{ menu_group.url }}}}{% else %}#{% endif %}" 
                                   {% if menu_group.active %}data-active="true"{% endif %}>
                                    {% if menu_group.icon %}<span>{{{{ menu_group.icon }}}}</span>{% endif %}
                                    <span>{{{{ menu_group.label }}}}</span>
                                    {% if menu_group.children %}<span class="menu-arrow">▶</span>{% endif %}
                                </a>
                                {% if menu_group.children %}
                                <div class="submenu">
                                    {% for child in menu_group.children %}
                                    <a class="sidenav-link sidenav-sub-link" 
                                       href="{{{{ child.url }}}}" 
                                       {% if child.active %}data-active="true"{% endif %}>
                                        {% if child.icon %}<span>{{{{ child.icon }}}}</span>{% endif %}
                                        <span>{{{{ child.label }}}}</span>
                                    </a>
                                    {% endfor %}
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        {% endif %}
                        </div>
                    </div>
                </nav>
            </aside>'''

def cleanup_custom_styles(content):
    """清理覆盖标准样式的自定义CSS"""
    # 移除各种sidebar相关的自定义样式
    styles_to_remove = [
        r'\.(customer|production|personnel|administrative|delivery|contract|opportunity)-sidebar[^{]*\{[^}]*\}',
        r'\.(customer|production|personnel|administrative|delivery|contract|opportunity)-nav[^{]*\{[^}]*\}',
        r'\.sidenav-group[^{]*\{[^}]*\}',
    ]
    
    for pattern in styles_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    return content

def add_js_reference(content):
    """添加sidebar.js引用"""
    if 'sidebar.js' not in content and '</body>' in content:
        js_tag = '    <script src="{% static \'js/sidebar.js\' %}"></script>\n'
        content = content.replace('</body>', js_tag + '</body>')
    return content

def fix_module(module_name, menu_var_name):
    """修复单个模块"""
    file_path = BASE_DIR / module_name / "base.html"
    
    if not file_path.exists():
        print(f"  ⚠ {module_name}: 文件不存在")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 替换HTML结构
        content = replace_sidebar_html(content, menu_var_name)
        
        # 2. 清理自定义样式（保留必要的布局样式）
        # content = cleanup_custom_styles(content)  # 先注释，避免过度删除
        
        # 3. 添加JavaScript引用
        content = add_js_reference(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {module_name}: 改造完成")
            return True
        else:
            print(f"  - {module_name}: 无需修改")
            return False
            
    except Exception as e:
        print(f"  ✗ {module_name}: 错误 - {e}")
        return False

if __name__ == "__main__":
    modules = [
        ("customer_management", "customer_menu"),
        ("production_management", "production_sidebar_nav"),
        ("personnel_management", "personnel_sidebar_nav"),
        ("administrative_management", "administrative_sidebar_nav"),
    ]
    
    print("开始批量改造导航栏...")
    for module, menu_var in modules:
        fix_module(module, menu_var)
    print("批量改造完成！")

