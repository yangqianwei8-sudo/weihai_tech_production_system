#!/usr/bin/env python3
"""
检查迁移状态脚本

检查数据库中是否已执行迁移
"""
import os
import sys
import re

# 尝试导入psycopg2
try:
    import psycopg2
except ImportError:
    print("错误：需要安装psycopg2")
    print("安装命令：pip install psycopg2-binary")
    sys.exit(1)

def parse_database_url(url):
    """解析数据库URL"""
    pattern = r'postgres://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, url)
    if match:
        return {
            'user': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'port': int(match.group(4)),
            'database': match.group(5)
        }
    return None

def check_migration_status(db_config):
    """检查迁移状态"""
    results = {
        'plan_todo_table_exists': False,
        'migration_0002_recorded': False,
        'migration_0003_recorded': False,
        'table_columns': [],
        'indexes': [],
        'errors': []
    }
    
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. 检查plan_todo表是否存在
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'plan_todo'
        """)
        if cur.fetchone():
            results['plan_todo_table_exists'] = True
            
            # 检查表结构
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'plan_todo'
                ORDER BY ordinal_position
            """)
            results['table_columns'] = cur.fetchall()
            
            # 检查索引
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public' 
                AND tablename = 'plan_todo'
            """)
            results['indexes'] = cur.fetchall()
        
        # 2. 检查迁移记录
        cur.execute("""
            SELECT name, applied
            FROM django_migrations
            WHERE app = 'plan_management'
            AND name IN ('0002_add_todo_model', '0003_extend_notification_event_types')
            ORDER BY name
        """)
        migrations = cur.fetchall()
        
        for migration_name, applied_time in migrations:
            if migration_name == '0002_add_todo_model':
                results['migration_0002_recorded'] = True
            elif migration_name == '0003_extend_notification_event_types':
                results['migration_0003_recorded'] = True
        
        cur.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        results['errors'].append(f"数据库连接失败: {str(e)}")
        results['errors'].append("提示：数据库地址可能是Kubernetes集群内部地址，需要从Pod内或通过端口转发访问")
    except Exception as e:
        results['errors'].append(f"检查失败: {str(e)}")
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("检查迁移状态")
    print("=" * 60)
    print()
    
    # 获取数据库配置
    database_url = os.getenv('DATABASE_URL', '').strip()
    
    if not database_url:
        # 尝试从.env.production读取
        env_file = os.path.join(os.path.dirname(__file__), '../../../../.env.production')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break
    
    if not database_url:
        print("⚠️  未找到DATABASE_URL环境变量")
        print("\n请手动检查迁移状态：")
        print("1. 检查plan_todo表是否存在")
        print("2. 检查django_migrations表中的迁移记录")
        return 1
    
    db_config = parse_database_url(database_url)
    if not db_config:
        print("错误：无法解析DATABASE_URL")
        return 1
    
    print(f"数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    print()
    
    results = check_migration_status(db_config)
    
    # 显示结果
    if results['errors']:
        print("❌ 检查过程中出现错误：")
        for error in results['errors']:
            print(f"  • {error}")
        print()
        print("建议：")
        print("1. 在Kubernetes Pod中执行检查")
        print("2. 或使用端口转发后检查")
        print("3. 或手动执行SQL检查（见下方）")
        return 1
    
    # 检查plan_todo表
    print("1. plan_todo表状态：")
    if results['plan_todo_table_exists']:
        print("   ✅ 表已存在")
        
        if results['table_columns']:
            print(f"   ✅ 表有 {len(results['table_columns'])} 个字段")
            print("   主要字段：")
            for col_name, col_type, is_nullable in results['table_columns'][:10]:
                null_text = "NULL" if is_nullable == 'YES' else "NOT NULL"
                print(f"     • {col_name} ({col_type}, {null_text})")
        
        if results['indexes']:
            print(f"   ✅ 表有 {len(results['indexes'])} 个索引")
            for idx_name, idx_def in results['indexes']:
                print(f"     • {idx_name}")
    else:
        print("   ❌ 表不存在")
    
    print()
    
    # 检查迁移记录
    print("2. Django迁移记录：")
    if results['migration_0002_recorded']:
        print("   ✅ 0002_add_todo_model 已记录")
    else:
        print("   ❌ 0002_add_todo_model 未记录")
    
    if results['migration_0003_recorded']:
        print("   ✅ 0003_extend_notification_event_types 已记录")
    else:
        print("   ❌ 0003_extend_notification_event_types 未记录")
    
    print()
    
    # 总结
    print("=" * 60)
    all_ok = (
        results['plan_todo_table_exists'] and 
        results['migration_0002_recorded'] and 
        results['migration_0003_recorded']
    )
    
    if all_ok:
        print("✅ 迁移已完成！")
        print()
        print("所有迁移已成功执行：")
        print("  • plan_todo表已创建")
        print("  • 迁移记录已保存")
    else:
        print("⚠️  迁移未完成或部分完成")
        print()
        print("需要执行的操作：")
        if not results['plan_todo_table_exists']:
            print("  • 创建plan_todo表（执行0002迁移）")
        if not results['migration_0002_recorded']:
            print("  • 记录0002迁移状态")
        if not results['migration_0003_recorded']:
            print("  • 记录0003迁移状态")
        print()
        print("执行迁移：")
        print("  python manage.py migrate plan_management")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
