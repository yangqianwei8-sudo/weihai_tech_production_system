from django.core.management.base import BaseCommand
from django.db import transaction

from backend.apps.system_management.models import PermissionItem, Role


PERMISSION_DEFINITIONS = [
    # 项目中心
    {"code": "project_center.view_all", "module": "project_center", "action": "view_all", "name": "项目中心-查看全部", "description": "查看所有项目及统计信息"},
    {"code": "project_center.view_assigned", "module": "project_center", "action": "view_assigned", "name": "项目中心-查看负责项目", "description": "查看本人相关项目数据"},
    {"code": "project_center.create", "module": "project_center", "action": "create", "name": "项目中心-创建项目", "description": "创建新项目、录入基础信息"},
    {"code": "project_center.configure_team", "module": "project_center", "action": "configure_team", "name": "项目中心-团队配置", "description": "配置项目团队成员及角色"},
    {"code": "project_center.monitor", "module": "project_center", "action": "monitor", "name": "项目中心-项目监控", "description": "监控项目进度、风险、里程碑"},
    {"code": "project_center.archive", "module": "project_center", "action": "archive", "name": "项目中心-项目归档", "description": "归档项目资料、导出报表"},
    {"code": "project_center.manage_finance", "module": "project_center", "action": "manage_finance", "name": "项目中心-财务管理", "description": "管理项目合同、费用、回款计划"},
    {"code": "project_center.delete", "module": "project_center", "action": "delete", "name": "项目中心-项目删除终止", "description": "删除或终止项目，需要审批"},
    {"code": "project_center.approve_stage", "module": "project_center", "action": "approve_stage", "name": "项目中心-阶段审批", "description": "审批项目阶段流转"},
    {"code": "project_center.export", "module": "project_center", "action": "export", "name": "项目中心-数据导出", "description": "导出项目数据并记录审计"},

    # 任务与协作中心
    {"code": "task_collaboration.manage", "module": "task_collaboration", "action": "manage", "name": "任务协作-流程配置", "description": "配置任务流程、模板、审批节点"},
    {"code": "task_collaboration.assign", "module": "task_collaboration", "action": "assign", "name": "任务协作-任务分配", "description": "分配任务、调整进度、指派责任人"},
    {"code": "task_collaboration.execute", "module": "task_collaboration", "action": "execute", "name": "任务协作-任务执行", "description": "领取任务、提交成果、更新进度"},
    {"code": "task_collaboration.audit_timesheet", "module": "task_collaboration", "action": "audit_timesheet", "name": "任务协作-工时审核", "description": "审核工时填报与任务消耗"},
    {"code": "task_collaboration.view_all", "module": "task_collaboration", "action": "view_all", "name": "任务协作-查看全部", "description": "查看全局任务和协作动态"},
    {"code": "task_collaboration.comment", "module": "task_collaboration", "action": "comment", "name": "任务协作-留言沟通", "description": "在任务中留言、协作沟通"},

    # 生产与质量中心
    {"code": "production_quality.submit_feedback", "module": "production_quality", "action": "submit_feedback", "name": "生产质量-意见填报", "description": "提交优化意见、质量问题、检查结果"},
    {"code": "production_quality.professional_review", "module": "production_quality", "action": "professional_review", "name": "生产质量-专业审核", "description": "对专业意见与成果进行审核"},
    {"code": "production_quality.project_review", "module": "production_quality", "action": "project_review", "name": "生产质量-项目审核", "description": "项目负责人对整体质量成果进行审核"},
    {"code": "production_quality.generate_report", "module": "production_quality", "action": "generate_report", "name": "生产质量-生成报告", "description": "生成质量报告、优化成果"},
    {"code": "production_quality.view_statistics", "module": "production_quality", "action": "view_statistics", "name": "生产质量-统计分析", "description": "查看质量统计、指标分析"},
    {"code": "production_quality.manage_standard", "module": "production_quality", "action": "manage_standard", "name": "生产质量-质量设置", "description": "维护质量标准、检查清单"},

    # 交付与客户门户
    {"code": "delivery_center.view", "module": "delivery_center", "action": "view", "name": "交付中心-访问", "description": "查看交付中心导航与相关功能入口"},
    {"code": "delivery_portal.view", "module": "delivery_portal", "action": "view", "name": "交付门户-查看", "description": "查看交付成果、客户协同记录"},
    {"code": "delivery_portal.submit", "module": "delivery_portal", "action": "submit", "name": "交付门户-成果提交", "description": "提交交付成果、上传报告"},
    {"code": "delivery_portal.approve", "module": "delivery_portal", "action": "approve", "name": "交付门户-成果审核", "description": "审核或确认交付成果"},
    {"code": "delivery_portal.configure", "module": "delivery_portal", "action": "configure", "name": "交付门户-配置管理", "description": "配置客户门户、访问权限"},
    {"code": "delivery_portal.sign", "module": "delivery_portal", "action": "sign", "name": "交付门户-电子签章", "description": "完成交付电子签章确认"},

    # 结算中心
    {"code": "settlement_center.initiate", "module": "settlement_center", "action": "initiate", "name": "结算中心-发起结算", "description": "发起项目结算流程"},
    {"code": "settlement_center.manage_output", "module": "settlement_center", "action": "manage_output", "name": "结算中心-产值管理", "description": "管理项目产值与成本"},
    {"code": "settlement_center.manage_finance", "module": "settlement_center", "action": "manage_finance", "name": "结算中心-财务管理", "description": "处理财务台账、开票、收款"},
    {"code": "settlement_center.approve", "module": "settlement_center", "action": "approve", "name": "结算中心-审批", "description": "审批结算、确认款项"},
    {"code": "settlement_center.view_analysis", "module": "settlement_center", "action": "view_analysis", "name": "结算中心-统计分析", "description": "查看结算统计与分析报表"},
    {"code": "settlement_center.configure", "module": "settlement_center", "action": "configure", "name": "结算中心-财务设置", "description": "维护财务参数、审批流程"},
    {"code": "settlement_center.view_sensitive", "module": "settlement_center", "action": "view_sensitive", "name": "结算中心-敏感金额查看", "description": "查看敏感财务金额与利润"},

    # 资源与标准中心
    {"code": "resource_center.manage_library", "module": "resource_center", "action": "manage_library", "name": "资源中心-标准库维护", "description": "维护企业标准、模板、指标库"},
    {"code": "resource_center.manage_template", "module": "resource_center", "action": "manage_template", "name": "资源中心-模板管理", "description": "维护模板资源"},
    {"code": "resource_center.manage_professional", "module": "resource_center", "action": "manage_professional", "name": "资源中心-专业标准维护", "description": "维护各专业标准数据"},
    {"code": "resource_center.view", "module": "resource_center", "action": "view", "name": "资源中心-查看", "description": "查看知识库与参考资料"},
    {"code": "resource_center.contribute", "module": "resource_center", "action": "contribute", "name": "资源中心-知识贡献", "description": "提交知识库案例与资料"},
    {"code": "resource_center.data_maintenance", "module": "resource_center", "action": "data_maintenance", "name": "资源中心-数据维护", "description": "维护数据字典与基础数据"},

    # 客户成功中心
    {"code": "customer_success.manage", "module": "customer_success", "action": "manage", "name": "客户成功-客户管理", "description": "管理客户档案、商机跟踪"},
    {"code": "customer_success.view", "module": "customer_success", "action": "view", "name": "客户成功-查看", "description": "查看客户信息、跟踪记录"},
    {"code": "customer_success.analyze", "module": "customer_success", "action": "analyze", "name": "客户成功-价值分析", "description": "分析客户价值、满意度"},
    {"code": "customer_success.opportunity", "module": "customer_success", "action": "opportunity", "name": "客户成功-商机挖掘", "description": "商机识别与跟进"},

    # 风控中心
    {"code": "risk_management.view", "module": "risk_management", "action": "view", "name": "风控中心-查看", "description": "查看风险事件、预警信息"},
    {"code": "risk_management.manage", "module": "risk_management", "action": "manage", "name": "风控中心-处理", "description": "处理风险事件、制定方案"},
    {"code": "risk_management.analyze", "module": "risk_management", "action": "analyze", "name": "风控中心-风险分析", "description": "分析风险趋势、生成报告"},
    {"code": "risk_management.configure", "module": "risk_management", "action": "configure", "name": "风控中心-配置", "description": "维护风险规则、预警设置"},

    # 系统管理
    {"code": "system_management.manage_users", "module": "system_management", "action": "manage_users", "name": "系统管理-用户管理", "description": "管理用户账号、角色、组织"},
    {"code": "system_management.manage_settings", "module": "system_management", "action": "manage_settings", "name": "系统管理-配置管理", "description": "维护系统配置、参数设置"},
    {"code": "system_management.view_settings", "module": "system_management", "action": "view_settings", "name": "系统管理-查看设置", "description": "查看系统配置、参数"},
    {"code": "system_management.audit", "module": "system_management", "action": "audit", "name": "系统管理-权限审计", "description": "执行权限审计、操作日志"},
    {"code": "system_management.backup", "module": "system_management", "action": "backup", "name": "系统管理-数据备份", "description": "执行数据备份与恢复"},
]


ROLE_PERMISSION_MAP = {
    "system_admin": {
        "name": "系统管理员",
        "description": "拥有平台全部功能的管理员角色",
        "permissions": "__all__",
    },
    "general_manager": {
        "name": "总经理",
        "description": "公司管理层，查看与管理全局业务",
        "permissions": "__all__",
    },
    "technical_manager": {
        "name": "技术部经理",
        "description": "负责技术部业务与生产协作管理",
        "permissions": [
            "project_center.view_all",
            "project_center.create",
            "project_center.configure_team",
            "project_center.monitor",
            "project_center.archive",
            "project_center.manage_finance",
            "project_center.approve_stage",
            "project_center.export",
            "task_collaboration.manage",
            "task_collaboration.assign",
            "task_collaboration.execute",
            "task_collaboration.audit_timesheet",
            "task_collaboration.view_all",
            "task_collaboration.comment",
            "delivery_center.view",
            "production_quality.submit_feedback",
            "production_quality.professional_review",
            "production_quality.project_review",
            "production_quality.generate_report",
            "production_quality.view_statistics",
            "production_quality.manage_standard",
            "delivery_portal.view",
            "delivery_portal.submit",
            "delivery_portal.approve",
            "delivery_portal.configure",
            "delivery_portal.sign",
            "settlement_center.initiate",
            "settlement_center.manage_output",
            "settlement_center.manage_finance",
            "settlement_center.approve",
            "settlement_center.view_analysis",
            "settlement_center.configure",
            "settlement_center.view_sensitive",
            "resource_center.manage_library",
            "resource_center.manage_template",
            "resource_center.manage_professional",
            "resource_center.view",
            "resource_center.contribute",
            "resource_center.data_maintenance",
            "customer_success.manage",
            "customer_success.view",
            "customer_success.analyze",
            "customer_success.opportunity",
            "risk_management.view",
            "risk_management.manage",
            "risk_management.analyze",
            "system_management.view_settings",
            "system_management.audit",
        ],
    },
    "project_manager": {
        "name": "项目负责人",
        "description": "管理所负责项目的全流程",
        "permissions": [
            "project_center.view_assigned",
            "project_center.create",
            "project_center.configure_team",
            "project_center.monitor",
            "project_center.archive",
            "project_center.manage_finance",
            "project_center.approve_stage",
            "task_collaboration.assign",
            "task_collaboration.execute",
            "task_collaboration.audit_timesheet",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.view",
            "production_quality.submit_feedback",
            "production_quality.professional_review",
            "production_quality.project_review",
            "production_quality.generate_report",
            "production_quality.view_statistics",
            "delivery_portal.submit",
            "delivery_portal.approve",
            "delivery_portal.sign",
            "settlement_center.initiate",
            "settlement_center.manage_output",
            "settlement_center.view_analysis",
            "resource_center.view",
            "resource_center.contribute",
            "customer_success.manage",
            "customer_success.view",
            "customer_success.analyze",
            "risk_management.view",
            "risk_management.manage",
        ],
    },
    "professional_lead": {
        "name": "专业负责人",
        "description": "负责专业团队管理与审核",
        "permissions": [
            "project_center.view_assigned",
            "project_center.monitor",
            "task_collaboration.assign",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.view",
            "production_quality.submit_feedback",
            "production_quality.professional_review",
            "production_quality.generate_report",
            "production_quality.view_statistics",
            "delivery_portal.submit",
            "delivery_portal.approve",
            "delivery_portal.sign",
            "resource_center.view",
            "resource_center.contribute",
            "resource_center.manage_professional",
            "customer_success.view",
            "risk_management.view",
        ],
    },
    "professional_engineer": {
        "name": "专业工程师",
        "description": "执行任务、提交质量成果",
        "permissions": [
            "project_center.view_assigned",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "production_quality.submit_feedback",
            "delivery_center.view",
            "delivery_portal.view",
            "resource_center.view",
            "resource_center.contribute",
        ],
    },
    "technical_assistant": {
        "name": "技术助理",
        "description": "协助项目资料整理与基础运营",
        "permissions": [
            "project_center.view_assigned",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "production_quality.submit_feedback",
            "delivery_center.view",
            "delivery_portal.view",
        ],
    },
    "business_team": {
        "name": "商务部经理",
        "description": "负责商务、结算、客户相关工作",
        "permissions": [
            "project_center.view_all",
            "project_center.create",
            "project_center.manage_finance",
            "project_center.monitor",
            "project_center.export",
            "task_collaboration.view_all",
            "task_collaboration.assign",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.view",
            "delivery_portal.configure",
            "delivery_portal.approve",
            "delivery_portal.sign",
            "settlement_center.initiate",
            "settlement_center.manage_finance",
            "settlement_center.manage_output",
            "settlement_center.approve",
            "settlement_center.view_analysis",
            "settlement_center.view_sensitive",
            "customer_success.manage",
            "customer_success.view",
            "customer_success.analyze",
            "customer_success.opportunity",
            "resource_center.view",
            "risk_management.view",
        ],
    },
    "business_assistant": {
        "name": "商务助理",
        "description": "协助商务信息维护与客户跟进",
        "permissions": [
            "project_center.view_assigned",
            "project_center.manage_finance",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.view",
            "settlement_center.manage_finance",
            "settlement_center.view_analysis",
            "customer_success.manage",
            "customer_success.view",
            "resource_center.view",
        ],
    },
    "cost_team": {
        "name": "造价审核人",
        "description": "负责成本、造价审核与管理",
        "permissions": [
            "project_center.view_all",
            "task_collaboration.view_all",
            "resource_center.manage_professional",
            "resource_center.view",
            "production_quality.professional_review",
            "production_quality.manage_standard",
            "settlement_center.manage_output",
            "settlement_center.approve",
            "settlement_center.view_analysis",
            "settlement_center.view_sensitive",
            "risk_management.view",
        ],
    },
    "cost_engineer": {
        "name": "造价工程师",
        "description": "负责造价测算与结算准备",
        "permissions": [
            "project_center.view_assigned",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "resource_center.manage_professional",
            "resource_center.view",
            "production_quality.submit_feedback",
            "settlement_center.manage_output",
            "settlement_center.view_analysis",
            "delivery_center.view",
            "delivery_portal.view",
        ],
    },
    "admin_office": {
        "name": "行政主管",
        "description": "负责行政、人事及基础财务支撑",
        "permissions": [
            "project_center.view_all",
            "settlement_center.manage_finance",
            "settlement_center.view_analysis",
            "system_management.manage_users",
            "system_management.manage_settings",
            "system_management.view_settings",
            "system_management.audit",
            "resource_center.data_maintenance",
        ],
    },
    "finance_supervisor": {
        "name": "财务主管",
        "description": "负责财务管理、付款审批和分析",
        "permissions": [
            "project_center.view_all",
            "project_center.manage_finance",
            "settlement_center.manage_finance",
            "settlement_center.approve",
            "settlement_center.view_analysis",
            "settlement_center.view_sensitive",
            "settlement_center.configure",
            "delivery_center.view",
            "delivery_portal.view",
            "customer_success.view",
            "system_management.view_settings",
        ],
    },
    "design_project_lead": {
        "name": "设计方项目负责人",
        "description": "外部设计方项目负责人",
        "permissions": [
            "project_center.view_assigned",
            "task_collaboration.assign",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.submit",
            "delivery_portal.approve",
            "delivery_portal.view",
            "delivery_portal.sign",
            "customer_success.view",
        ],
    },
    "design_professional_lead": {
        "name": "设计方专业负责人",
        "description": "外部设计方专业负责人",
        "permissions": [
            "project_center.view_assigned",
            "task_collaboration.assign",
            "task_collaboration.execute",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.submit",
            "delivery_portal.view",
            "delivery_portal.sign",
        ],
    },
    "design_engineer": {
        "name": "设计方专业工程师",
        "description": "外部设计方专业工程师",
        "permissions": [
            "task_collaboration.execute",
            "task_collaboration.comment",
            "delivery_center.view",
            "delivery_portal.view",
        ],
    },
    "client_project_lead": {
        "name": "甲方项目负责人",
        "description": "客户方项目负责人",
        "permissions": [
            "project_center.view_assigned",
            "delivery_center.view",
            "delivery_portal.approve",
            "delivery_portal.view",
            "delivery_portal.sign",
            "settlement_center.approve",
            "customer_success.manage",
            "customer_success.view",
        ],
    },
    "client_professional_lead": {
        "name": "甲方专业负责人",
        "description": "客户方专业负责人",
        "permissions": [
            "project_center.view_assigned",
            "delivery_center.view",
            "delivery_portal.approve",
            "delivery_portal.view",
            "delivery_portal.sign",
            "customer_success.view",
        ],
    },
    "client_engineer": {
        "name": "甲方专业工程师",
        "description": "客户方专业工程师",
        "permissions": [
            "project_center.view_assigned",
            "delivery_center.view",
            "delivery_portal.view",
            "customer_success.view",
        ],
    },
}


class Command(BaseCommand):
    help = "Seed business permission items and default role assignments"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding permission items..."))
        permission_lookup = {}
        for definition in PERMISSION_DEFINITIONS:
            item, created = PermissionItem.objects.update_or_create(
                code=definition["code"],
                defaults={
                    "module": definition["module"],
                    "action": definition["action"],
                    "name": definition["name"],
                    "description": definition.get("description", ""),
                    "is_active": True,
                },
            )
            permission_lookup[item.code] = item
            self.stdout.write(f"  - {'Created' if created else 'Updated'} permission: {item.code}")

        all_permissions = list(permission_lookup.values())

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding roles and assigning permissions..."))
        for role_code, payload in ROLE_PERMISSION_MAP.items():
            role, created = Role.objects.update_or_create(
                code=role_code,
                defaults={
                    "name": payload["name"],
                    "description": payload.get("description", ""),
                    "is_active": True,
                },
            )
            permissions = payload["permissions"]
            if permissions == "__all__":
                role.custom_permissions.set(all_permissions)
            else:
                missing = [code for code in permissions if code not in permission_lookup]
                if missing:
                    raise ValueError(f"Permission codes not found for role {role_code}: {missing}")
                role.custom_permissions.set([permission_lookup[code] for code in permissions])
            role.save()
            self.stdout.write(f"  - {'Created' if created else 'Updated'} role: {role.name}")

        self.stdout.write(self.style.SUCCESS("Permission seeding completed."))
