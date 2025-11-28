from django.urls import path
from .views import AnalyzeTaskView, SuggestTaskView

urlpatterns = [
    path('analyze/', AnalyzeTaskView.as_view(), name='analyze_tasks'),
    path('suggest/', SuggestTaskView.as_view(), name='suggest_tasks'),
]