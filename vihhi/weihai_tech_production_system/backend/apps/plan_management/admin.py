"""
计划管理模块Django Admin配置
"""
from django.contrib import admin
from .models import (
    StrategicGoal,
    GoalStatusLog,
    GoalProgressRecord,
    GoalAdjustment,
    GoalAlignmentRecord,
    Plan,
    PlanStatusLog,
    PlanProgressRecord,
    PlanIssue,
    PlanApproval,
)
from backend.core.admin_base import BaseModelAdmin, AuditAdminMixin, ReadOnlyAdminMixin


@admin.register(StrategicGoal)
class StrategicGoalAdmin(AuditAdminMixin, BaseModelAdmin):
    """战略目标管理"""
    list_display = (
        'goal_number', 'name', 'goal_type', 'goal_period', 'status',
        'target_value', 'current_value', 'completion_rate',
        'responsible_person', 'start_date', 'end_date', 'created_time'
    )
    list_filter = (
        'goal_type', 'goal_period', 'status', 'created_time',
        'responsible_person', 'responsible_department'
    )
    search_fields = (
        'goal_number', 'name', 'indicator_name',
        'responsible_person__username', 'responsible_person__full_name'
    )
    readonly_fields = (
        'goal_number', 'completion_rate', 'duration_days',
        'created_time', 'updated_time', 'created_by'
    )
    filter_horizontal = ('participants', 'related_projects')
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)
    fieldsets = (
        ('基本信息', {
            'fields': ('goal_number', 'name', 'goal_type', 'goal_period', 'status')
        }),
        ('目标指标', {
            'fields': (
                'indicator_name', 'indicator_type', 'indicator_unit',
                'target_value', 'current_value', 'completion_rate'
            )
        }),
        ('责任人信息', {
            'fields': ('responsible_person', 'responsible_department', 'participants')
        }),
        ('目标描述', {
            'fields': ('description', 'background', 'significance')
        }),
        ('权重设置', {
            'fields': ('weight', 'weight_description')
        }),
        ('时间信息', {
            'fields': ('start_date', 'end_date', 'duration_days')
        }),
        ('关联信息', {
            'fields': ('parent_goal', 'related_projects', 'notes')
        }),
        ('系统信息', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
        # 系统时间信息会自动添加
    )


@admin.register(GoalStatusLog)
class GoalStatusLogAdmin(ReadOnlyAdminMixin, BaseModelAdmin):
    """目标状态日志管理（只读）"""
    list_display = (
        'goal', 'old_status', 'new_status', 'changed_by', 'changed_time'
    )
    list_filter = ('old_status', 'new_status', 'changed_time')
    search_fields = (
        'goal__goal_number', 'goal__name',
        'changed_by__username', 'changed_by__full_name'
    )
    readonly_fields = ('goal', 'old_status', 'new_status', 'changed_by', 'changed_time')
    date_hierarchy = 'changed_time'
    ordering = ('-changed_time',)


@admin.register(GoalProgressRecord)
class GoalProgressRecordAdmin(ReadOnlyAdminMixin, BaseModelAdmin):
    """目标进度记录管理（只读）"""
    list_display = (
        'goal', 'current_value', 'completion_rate',
        'recorded_by', 'recorded_time'
    )
    list_filter = ('recorded_time', 'goal__status')
    search_fields = (
        'goal__goal_number', 'goal__name',
        'recorded_by__username', 'recorded_by__full_name'
    )
    readonly_fields = ('goal', 'completion_rate', 'recorded_by', 'recorded_time')
    date_hierarchy = 'recorded_time'
    ordering = ('-recorded_time',)


@admin.register(GoalAdjustment)
class GoalAdjustmentAdmin(AuditAdminMixin, BaseModelAdmin):
    """目标调整申请管理"""
    list_display = (
        'goal', 'status', 'created_by', 'approved_by',
        'created_time', 'approved_time'
    )
    list_filter = ('status', 'created_time', 'approved_time')
    search_fields = (
        'goal__goal_number', 'goal__name',
        'created_by__username', 'created_by__full_name',
        'approved_by__username', 'approved_by__full_name'
    )
    readonly_fields = ('goal', 'created_by', 'created_time', 'updated_time')
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)


@admin.register(GoalAlignmentRecord)
class GoalAlignmentRecordAdmin(ReadOnlyAdminMixin, BaseModelAdmin):
    """目标对齐度记录管理（只读）"""
    list_display = (
        'parent_goal', 'child_goal', 'alignment_score', 'recorded_time'
    )
    list_filter = ('recorded_time',)
    search_fields = (
        'parent_goal__goal_number', 'parent_goal__name',
        'child_goal__goal_number', 'child_goal__name'
    )
    readonly_fields = ('parent_goal', 'child_goal', 'recorded_time')
    date_hierarchy = 'recorded_time'
    ordering = ('-recorded_time',)


@admin.register(Plan)
class PlanAdmin(AuditAdminMixin, BaseModelAdmin):
    """计划管理"""
    list_display = (
        'plan_number', 'name', 'plan_type', 'plan_period', 'status',
        'related_goal', 'responsible_person', 'progress',
        'start_time', 'end_time', 'created_time'
    )
    list_filter = (
        'plan_type', 'plan_period', 'status', 'priority',
        'created_time', 'responsible_person', 'responsible_department'
    )
    search_fields = (
        'plan_number', 'name', 'plan_objective',
        'responsible_person__username', 'responsible_person__full_name',
        'related_goal__goal_number', 'related_goal__name'
    )
    readonly_fields = (
        'plan_number', 'duration_days', 'alignment_score',
        'created_time', 'updated_time', 'created_by'
    )
    filter_horizontal = ('participants',)
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)
    fieldsets = (
        ('基本信息', {
            'fields': ('plan_number', 'name', 'plan_type', 'plan_period', 'status')
        }),
        ('关联战略目标', {
            'fields': ('related_goal', 'alignment_score', 'contribution_score')
        }),
        ('计划内容', {
            'fields': ('content', 'plan_objective', 'description')
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time', 'duration_days')
        }),
        ('责任人信息', {
            'fields': ('responsible_person', 'responsible_department', 'participants')
        }),
        ('优先级和预算', {
            'fields': ('priority', 'budget')
        }),
        ('关联信息', {
            'fields': ('related_project', 'parent_plan', 'notes')
        }),
        ('进度信息', {
            'fields': ('progress',)
        }),
        ('系统信息', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
        # 系统时间信息会自动添加
    )


@admin.register(PlanStatusLog)
class PlanStatusLogAdmin(ReadOnlyAdminMixin, BaseModelAdmin):
    """计划状态日志管理（只读）"""
    list_display = (
        'plan', 'old_status', 'new_status', 'changed_by', 'changed_time'
    )
    list_filter = ('old_status', 'new_status', 'changed_time')
    search_fields = (
        'plan__plan_number', 'plan__name',
        'changed_by__username', 'changed_by__full_name'
    )
    readonly_fields = ('plan', 'old_status', 'new_status', 'changed_by', 'changed_time')
    date_hierarchy = 'changed_time'
    ordering = ('-changed_time',)


@admin.register(PlanProgressRecord)
class PlanProgressRecordAdmin(ReadOnlyAdminMixin, BaseModelAdmin):
    """计划进度记录管理（只读）"""
    list_display = (
        'plan', 'progress', 'recorded_by', 'recorded_time'
    )
    list_filter = ('recorded_time', 'plan__status')
    search_fields = (
        'plan__plan_number', 'plan__name',
        'recorded_by__username', 'recorded_by__full_name'
    )
    readonly_fields = ('plan', 'recorded_by', 'recorded_time')
    date_hierarchy = 'recorded_time'
    ordering = ('-recorded_time',)


@admin.register(PlanIssue)
class PlanIssueAdmin(AuditAdminMixin, BaseModelAdmin):
    """计划问题管理"""
    list_display = (
        'plan', 'title', 'severity', 'status', 'assigned_to', 'created_time'
    )
    list_filter = ('severity', 'status', 'created_time')
    search_fields = (
        'plan__plan_number', 'plan__name',
        'title', 'description',
        'assigned_to__username', 'assigned_to__full_name'
    )
    readonly_fields = ('plan', 'created_by', 'created_time', 'updated_time')
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)


@admin.register(PlanApproval)
class PlanApprovalAdmin(ReadOnlyAdminMixin, BaseModelAdmin):
    """计划审批记录管理（只读）"""
    list_display = (
        'plan', 'approval_node', 'status', 'approved_by', 'approved_time'
    )
    list_filter = ('status', 'approved_time')
    search_fields = (
        'plan__plan_number', 'plan__name',
        'approved_by__username', 'approved_by__full_name'
    )
    readonly_fields = ('plan', 'created_time', 'updated_time')
    date_hierarchy = 'created_time'
    ordering = ('-created_time',)

