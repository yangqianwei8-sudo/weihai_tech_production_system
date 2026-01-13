"""
plan_management 的可选依赖收口点：
- P1 不改其他模块，但也不让 try/except 散落在 views/serializers/services。
"""

from __future__ import annotations
from typing import Any, Callable, Optional

# ---- Audit ----
_audit_log: Optional[Callable[..., Any]] = None
try:
    from backend.apps.system_management.models import AuditLog, AuditAction
    _audit_log = AuditLog
    _audit_action = AuditAction
except Exception:
    _audit_log = None
    _audit_action = None


def safe_audit_log(actor=None, action=None, object_type=None, object_id=None, changes=None, meta=None, **kwargs: Any) -> None:
    """无审计模块时静默跳过，避免 P1 被外部模块拖死。"""
    if _audit_log and action:
        try:
            _audit_log.objects.create(
                actor=actor,
                action=action,
                object_type=object_type,
                object_id=object_id,
                changes=changes or {},
                meta=meta or {},
                **kwargs
            )
        except Exception:
            pass  # 静默失败，不影响业务


def get_audit_action():
    """获取 AuditAction，如果不存在返回 None"""
    return _audit_action


# ---- ApprovalNotification ----
_ApprovalNotification: Optional[type] = None
try:
    from backend.apps.plan_management.models import ApprovalNotification
    _ApprovalNotification = ApprovalNotification
except Exception:
    _ApprovalNotification = None


def safe_approval_notification(*args: Any, **kwargs: Any) -> Any:
    """无通知类时返回 None，调用方不得依赖返回值作为业务判断。"""
    if _ApprovalNotification:
        try:
            return _ApprovalNotification.objects.create(*args, **kwargs)
        except Exception:
            return None
    return None


def has_approval_notification() -> bool:
    """检查 ApprovalNotification 是否可用"""
    return _ApprovalNotification is not None


def get_approval_notification_model():
    """获取 ApprovalNotification 模型类，如果不存在返回 None"""
    return _ApprovalNotification
