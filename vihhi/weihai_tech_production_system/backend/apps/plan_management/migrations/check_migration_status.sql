-- 检查迁移状态的SQL脚本
-- 可以在数据库中直接执行此脚本来检查迁移状态

-- 1. 检查plan_todo表是否存在
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'plan_todo'
        ) THEN '✅ plan_todo表已存在'
        ELSE '❌ plan_todo表不存在'
    END AS table_status;

-- 2. 如果表存在，显示表结构
SELECT 
    column_name AS "字段名",
    data_type AS "数据类型",
    CASE WHEN is_nullable = 'YES' THEN '可空' ELSE '非空' END AS "是否可空"
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'plan_todo'
ORDER BY ordinal_position;

-- 3. 如果表存在，显示索引
SELECT 
    indexname AS "索引名",
    indexdef AS "索引定义"
FROM pg_indexes
WHERE schemaname = 'public' 
AND tablename = 'plan_todo'
ORDER BY indexname;

-- 4. 检查迁移记录
SELECT 
    name AS "迁移名称",
    applied AS "执行时间",
    CASE 
        WHEN name = '0002_add_todo_model' THEN '✅ 已记录'
        WHEN name = '0003_extend_notification_event_types' THEN '✅ 已记录'
        ELSE '❌ 未记录'
    END AS "状态"
FROM django_migrations
WHERE app = 'plan_management'
AND name IN ('0002_add_todo_model', '0003_extend_notification_event_types')
ORDER BY name;

-- 5. 统计信息
SELECT 
    'plan_todo表记录数' AS "统计项",
    COUNT(*)::text AS "值"
FROM plan_todo
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'plan_todo'
);

-- 6. 检查是否有逾期待办
SELECT 
    '逾期待办数量' AS "统计项",
    COUNT(*)::text AS "值"
FROM plan_todo
WHERE is_overdue = TRUE
AND EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'plan_todo'
);
