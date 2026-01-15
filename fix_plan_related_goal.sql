-- 修复计划表中 related_goal 字段的 NULL 约束
-- 允许 related_goal_id 为 NULL

-- 检查当前约束
SELECT 
    column_name, 
    is_nullable, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'plan_plan' 
AND column_name = 'related_goal_id';

-- 修改列允许 NULL（如果当前不允许）
ALTER TABLE plan_plan 
ALTER COLUMN related_goal_id DROP NOT NULL;

-- 验证修改
SELECT 
    column_name, 
    is_nullable, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'plan_plan' 
AND column_name = 'related_goal_id';
