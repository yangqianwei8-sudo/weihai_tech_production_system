#!/usr/bin/env python
"""
测试合同洽谈创建视图
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/home/devbox/project/vihhi/weihai_tech_production_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from backend.apps.customer_management.views_pages import contract_negotiation_create

User = get_user_model()

print("=" * 60)
print("测试合同洽谈创建视图")
print("=" * 60)

# 1. 检查用户
user = User.objects.first()
if not user:
    print("❌ 没有找到用户")
    sys.exit(1)
print(f"✅ 使用用户: {user.username}")

# 2. 测试表单
try:
    from backend.apps.customer_management.forms import ContractNegotiationForm
    form = ContractNegotiationForm(user=user)
    print("✅ 表单创建成功")
    
    # 检查project字段
    if 'project' in form.fields:
        qs = form.fields['project'].queryset
        print(f"✅ Project字段查询集: {qs.model.__name__}, 数量: {qs.count()}")
    else:
        print("⚠️ Project字段不存在")
except Exception as e:
    print(f"❌ 表单创建失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试视图（使用Client模拟真实请求）
try:
    client = Client()
    client.force_login(user)
    
    response = client.get('/business/contracts/negotiation/create/')
    print(f"✅ 视图响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 页面可以正常访问")
    elif response.status_code == 302:
        print(f"⚠️ 重定向到: {response.url}")
    else:
        print(f"⚠️ 状态码: {response.status_code}")
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')[:500]
            print(f"响应内容（前500字符）: {content}")
            
except Exception as e:
    print(f"❌ 视图测试失败: {str(e)}")
    import traceback
    traceback.print_exc()

print("=" * 60)

