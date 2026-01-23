#!/usr/bin/env python3
"""
直接执行数据库迁移脚本

不依赖Django，直接使用psycopg2连接数据库执行SQL
"""
import os
import sys
import re

# 尝试导入psycopg2
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("错误：需要安装psycopg2")
    print("安装命令：pip install psycopg2-binary")
    sys.exit(1)

def parse_database_url(url):
    """解析数据库URL"""
    # postgres://user:password@host:port/dbname
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

def read_sql_file(file_path):
    """读取SQL文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def execute_migration(db_config, sql_file):
    """执行迁移"""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        conn.autocommit = False
        
        cur = conn.cursor()
        
        print(f"执行迁移: {os.path.basename(sql_file)}")
        sql_content = read_sql_file(sql_file)
        
        # 执行SQL
        cur.execute(sql_content)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"  ✅ 迁移成功")
        return True
        
    except psycopg2.Error as e:
        print(f"  ❌ 迁移失败: {str(e)}")
        try:
            if 'conn' in locals() and conn:
                conn.rollback()
                conn.close()
        except:
            pass
        return False
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        return False

def record_migration(db_config, migration_name):
    """记录迁移到django_migrations表"""
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
        
        # 检查迁移是否已记录
        cur.execute("""
            SELECT id FROM django_migrations 
            WHERE app = 'plan_management' AND name = %s
        """, (migration_name,))
        
        if cur.fetchone():
            print(f"  ℹ️  迁移 {migration_name} 已记录，跳过")
        else:
            cur.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('plan_management', %s, NOW())
            """, (migration_name,))
            print(f"  ✅ 已记录迁移: {migration_name}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ⚠️  记录迁移失败: {str(e)}（可手动记录）")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("直接执行数据库迁移")
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
        print("错误：未找到DATABASE_URL环境变量")
        print("请设置: export DATABASE_URL='postgres://user:pass@host:port/dbname'")
        return 1
    
    print(f"数据库: {database_url.split('@')[1] if '@' in database_url else 'N/A'}")
    print()
    
    db_config = parse_database_url(database_url)
    if not db_config:
        print("错误：无法解析DATABASE_URL")
        return 1
    
    # 迁移文件路径
    migration_dir = os.path.dirname(__file__)
    migrations = [
        ('0002_add_todo_model.sql', '0002_add_todo_model'),
        ('0003_extend_notification_event_types.sql', '0003_extend_notification_event_types'),
    ]
    
    success_count = 0
    error_count = 0
    
    for sql_file, migration_name in migrations:
        sql_path = os.path.join(migration_dir, sql_file)
        
        if not os.path.exists(sql_path):
            print(f"⚠️  文件不存在: {sql_file}，跳过")
            continue
        
        if execute_migration(db_config, sql_path):
            record_migration(db_config, migration_name)
            success_count += 1
        else:
            error_count += 1
        print()
    
    print("=" * 60)
    print("迁移完成")
    print(f"成功: {success_count}, 失败: {error_count}")
    print("=" * 60)
    
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
