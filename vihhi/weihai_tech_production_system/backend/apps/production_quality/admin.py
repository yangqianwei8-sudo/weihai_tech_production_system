from django.contrib import admin

from .models import (
    Opinion,
    OpinionAttachment,
    OpinionReview,
    ProductionReport,
    ProductionReportSection,
    ProductionStatistic,
)


class OpinionAttachmentInline(admin.TabularInline):
    model = OpinionAttachment
    extra = 0
    fields = ("attachment_type", "file", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class OpinionReviewInline(admin.TabularInline):
    model = OpinionReview
    extra = 0
    fields = (
        "role",
        "reviewer",
        "status",
        "technical_score",
        "economic_score",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = (
        "opinion_number",
        "project",
        "professional_category",
        "status",
        "severity_level",
        "saving_amount",
        "created_by",
        "created_at",
    )
    search_fields = ("opinion_number", "project__name", "project__project_number")
    list_filter = ("status", "issue_category", "severity_level", "professional_category")
    inlines = [OpinionAttachmentInline, OpinionReviewInline]
    raw_id_fields = ("project", "professional_category", "created_by", "current_reviewer")
    filter_horizontal = ("review_points",)


@admin.register(ProductionReport)
class ProductionReportAdmin(admin.ModelAdmin):
    list_display = ("report_number", "name", "project", "professional_category", "status", "generated_at")
    search_fields = ("report_number", "name", "project__name", "project__project_number")
    list_filter = ("status", "professional_category")
    raw_id_fields = ("project", "professional_category", "template", "generated_by")


@admin.register(ProductionReportSection)
class ProductionReportSectionAdmin(admin.ModelAdmin):
    list_display = ("report", "title", "order")
    list_filter = ("report",)
    search_fields = ("report__report_number", "title")


@admin.register(ProductionStatistic)
class ProductionStatisticAdmin(admin.ModelAdmin):
    list_display = ("project", "statistic_type", "snapshot_date")
    list_filter = ("statistic_type", "snapshot_date")
    search_fields = ("project__project_number", "project__name")


@admin.register(OpinionAttachment)
class OpinionAttachmentAdmin(admin.ModelAdmin):
    list_display = ("opinion", "attachment_type", "uploaded_by", "uploaded_at")
    list_filter = ("attachment_type", "uploaded_at")
    raw_id_fields = ("opinion", "uploaded_by")


@admin.register(OpinionReview)
class OpinionReviewAdmin(admin.ModelAdmin):
    list_display = ("opinion", "reviewer", "role", "status", "created_at")
    list_filter = ("role", "status")
    search_fields = ("opinion__opinion_number", "reviewer__username")
    raw_id_fields = ("opinion", "reviewer")

