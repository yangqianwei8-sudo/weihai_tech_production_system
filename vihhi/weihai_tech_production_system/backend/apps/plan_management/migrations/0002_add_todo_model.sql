-- 手动SQL迁移脚本：创建plan_todo表
-- 如果Django迁移无法运行，可以直接在数据库中执行此SQL脚本
-- 适用于PostgreSQL数据库

-- 创建plan_todo表
CREATE TABLE IF NOT EXISTS plan_todo (
    id BIGSERIAL PRIMARY KEY,
    todo_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    is_overdue BOOLEAN NOT NULL DEFAULT FALSE,
    created_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assignee_id BIGINT NOT NULL,
    created_by_id BIGINT,
    related_goal_id BIGINT,
    related_plan_id BIGINT,
    CONSTRAINT plan_todo_assignee_id_fk FOREIGN KEY (assignee_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT plan_todo_created_by_id_fk FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE PROTECT,
    CONSTRAINT plan_todo_related_goal_id_fk FOREIGN KEY (related_goal_id) REFERENCES plan_strategic_goal(id) ON DELETE CASCADE,
    CONSTRAINT plan_todo_related_plan_id_fk FOREIGN KEY (related_plan_id) REFERENCES plan_plan(id) ON DELETE CASCADE,
    CONSTRAINT plan_todo_todo_type_check CHECK (todo_type IN (
        'goal_creation', 'goal_decomposition', 'goal_progress_update',
        'company_plan_creation', 'personal_plan_creation',
        'weekly_plan_decomposition', 'daily_plan_decomposition',
        'plan_progress_update'
    )),
    CONSTRAINT plan_todo_status_check CHECK (status IN (
        'pending', 'in_progress', 'completed', 'overdue', 'cancelled'
    ))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS plan_todo_assignee_status_idx ON plan_todo(assignee_id, status);
CREATE INDEX IF NOT EXISTS plan_todo_deadline_idx ON plan_todo(deadline);
CREATE INDEX IF NOT EXISTS plan_todo_overdue_status_idx ON plan_todo(is_overdue, status);
CREATE INDEX IF NOT EXISTS plan_todo_type_status_idx ON plan_todo(todo_type, status);

-- 添加表注释
COMMENT ON TABLE plan_todo IS '待办事项表';
COMMENT ON COLUMN plan_todo.todo_type IS '待办类型';
COMMENT ON COLUMN plan_todo.title IS '待办标题';
COMMENT ON COLUMN plan_todo.description IS '待办描述';
COMMENT ON COLUMN plan_todo.deadline IS '截止时间';
COMMENT ON COLUMN plan_todo.completed_at IS '完成时间';
COMMENT ON COLUMN plan_todo.status IS '状态：pending=待处理, in_progress=进行中, completed=已完成, overdue=已逾期, cancelled=已取消';
COMMENT ON COLUMN plan_todo.is_overdue IS '是否逾期';
COMMENT ON COLUMN plan_todo.assignee_id IS '负责人ID';
COMMENT ON COLUMN plan_todo.created_by_id IS '创建人ID（系统自动创建时可为空）';
COMMENT ON COLUMN plan_todo.related_goal_id IS '关联目标ID';
COMMENT ON COLUMN plan_todo.related_plan_id IS '关联计划ID';
