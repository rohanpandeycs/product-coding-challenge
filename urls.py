from django.urls import path
from ai.views.controller import extract_financial_details

urlpatterns = [
    path('api/financialSummary', extract_financial_details, name='extract_financial_details'),
]
