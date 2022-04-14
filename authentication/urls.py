from django.urls import path
from authentication import views
app_name = 'authentication'
urlpatterns = [
    path('mobile/', views.RequestOTP.as_view(), name="mobile_login"),
    path('confirm/', views.TokenObtainPairView.as_view(), name="confirm_code"),
    path('refresh/', views.TokenRefreshView.as_view(), name="refresh_token"),
]