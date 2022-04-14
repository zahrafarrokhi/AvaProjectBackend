from django.urls import path
from authentication import views
app_name = 'authentication'
urlpatterns = [

    path('mobile/', views.RequestOTP.as_view(), name="mobile_login")
]