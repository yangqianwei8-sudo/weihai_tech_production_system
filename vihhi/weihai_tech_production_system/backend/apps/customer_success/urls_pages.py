from django.urls import path

from . import views_pages

app_name = "business"

urlpatterns = [
    path("customers/", views_pages.customer_management, name="customer_management"),
    path("contracts/", views_pages.contract_management, name="contract_management"),
    path("settlements/", views_pages.project_settlement, name="project_settlement"),
    path("analysis/", views_pages.output_analysis, name="output_analysis"),
    path("payments/", views_pages.payment_tracking, name="payment_tracking"),
]

