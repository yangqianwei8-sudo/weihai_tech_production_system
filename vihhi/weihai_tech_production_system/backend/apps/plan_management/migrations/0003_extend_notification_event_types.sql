-- 手动SQL迁移脚本：扩展通知事件类型
-- 如果Django迁移无法运行，可以直接在数据库中执行此SQL脚本
-- 适用于PostgreSQL数据库

-- 注意：此迁移主要是更新Django模型的选择项，数据库层面不需要修改
-- 但如果需要添加约束，可以执行以下SQL

-- 检查并更新approval_notification表的event字段约束（如果需要）
-- 注意：PostgreSQL的CHECK约束需要先删除旧的再添加新的

-- 删除旧的约束（如果存在）
ALTER TABLE plan_approval_notification 
DROP CONSTRAINT IF EXISTS plan_approval_notification_event_check;

-- 添加新的约束（包含所有新的事件类型）
ALTER TABLE plan_approval_notification
ADD CONSTRAINT plan_approval_notification_event_check CHECK (event IN (
    'submit', 'approve', 'reject', 'cancel',
    'draft_timeout', 'approval_timeout',
    'company_goal_published', 'personal_goal_published', 'goal_accepted',
    'company_plan_published', 'personal_plan_published', 'plan_accepted',
    'weekly_plan_reminder', 'weekly_plan_overdue',
    'goal_creation', 'goal_decomposition', 'goal_progress_update',
    'goal_progress_updated', 'goal_overdue', 'subordinate_goal_overdue',
    'company_plan_creation', 'personal_plan_creation',
    'weekly_plan_decomposition', 'daily_plan_decomposition',
    'plan_progress_update', 'plan_progress_updated',
    'plan_auto_started', 'plan_overdue', 'subordinate_plan_overdue',
    'todo_overdue', 'daily_todo_reminder',
    'weekly_summary', 'monthly_summary', 'daily_notification'
));

-- 检查并更新object_type字段约束（如果需要）
ALTER TABLE plan_approval_notification 
DROP CONSTRAINT IF EXISTS plan_approval_notification_object_type_check;

ALTER TABLE plan_approval_notification
ADD CONSTRAINT plan_approval_notification_object_type_check CHECK (object_type IN (
    'plan', 'goal', 'todo', 'summary', 'notification'
));

-- 注意：如果表结构中没有这些约束，可以跳过约束添加步骤
-- Django ORM会在应用层进行验证
