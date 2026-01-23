#!/usr/bin/env python3
"""
迁移文件验证脚本

验证迁移文件的语法和完整性，不实际执行迁移
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../'))

def verify_migration_file(file_path):
    """验证迁移文件"""
    print(f"检查文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"  ❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查基本结构
    checks = [
        ('class Migration', '迁移类定义'),
        ('dependencies', '依赖声明'),
        ('operations', '操作列表'),
    ]
    
    all_ok = True
    for check, desc in checks:
        if check in content:
            print(f"  ✓ {desc}")
        else:
            print(f"  ❌ 缺少: {desc}")
            all_ok = False
    
    # 检查特定迁移内容
    if '0002_add_todo_model' in file_path:
        if 'CreateModel' in content and 'Todo' in content:
            print(f"  ✓ Todo模型创建")
        else:
            print(f"  ❌ Todo模型创建不完整")
            all_ok = False
        
        if 'plan_todo' in content:
            print(f"  ✓ 表名正确")
        else:
            print(f"  ❌ 表名不正确")
            all_ok = False
    
    if '0003_extend_notification_event_types' in file_path:
        if 'AlterField' in content and 'event' in content:
            print(f"  ✓ 事件类型扩展")
        else:
            print(f"  ❌ 事件类型扩展不完整")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("=" * 60)
    print("迁移文件验证")
    print("=" * 60)
    print()
    
    migration_dir = os.path.dirname(__file__)
    
    migrations = [
        '0002_add_todo_model.py',
        '0003_extend_notification_event_types.py',
    ]
    
    all_ok = True
    for migration in migrations:
        file_path = os.path.join(migration_dir, migration)
        print(f"\n验证: {migration}")
        print("-" * 60)
        if not verify_migration_file(file_path):
            all_ok = False
        print()
    
    # 检查SQL脚本
    sql_files = [
        '0002_add_todo_model.sql',
        '0003_extend_notification_event_types.sql',
    ]
    
    print("\n检查SQL脚本:")
    print("-" * 60)
    for sql_file in sql_files:
        file_path = os.path.join(migration_dir, sql_file)
        if os.path.exists(file_path):
            print(f"  ✓ {sql_file} 存在")
        else:
            print(f"  ❌ {sql_file} 不存在")
            all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("✅ 所有迁移文件验证通过！")
        print("\n下一步：")
        print("1. 在有Django环境的服务器上运行: python manage.py migrate plan_management")
        print("2. 或直接执行SQL脚本: psql -U postgres -d weihai_tech -f migrations/0002_add_todo_model.sql")
    else:
        print("❌ 部分迁移文件存在问题，请检查")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
