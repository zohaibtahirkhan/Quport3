from django.urls import path
from .views import QuPortChatbotView, PadelChatbotView, SoccerChatbotView, BakermanChatbotView

urlpatterns = [
    path('padel/', PadelChatbotView.as_view(), name='padel'),
    path('quport/', QuPortChatbotView.as_view(), name='quport'),
    path('soccer/', SoccerChatbotView.as_view(), name='soccer'),
    path('bakerman/', BakermanChatbotView.as_view(), name='bakerman')
]
