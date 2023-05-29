from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from website import views
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView

router = DefaultRouter()
router.register("register", views.Register_ViewAPI, basename="register")
router.register("company", views.Company_management, basename="company")
router.register("update/emp", views.ProfileImage_View, basename="update_emp")
router.register("view/emp", views.View_Employee, basename="view_emp")

urlpatterns = [
    path("", include(router.urls)),
    path("verify/<token>/<pk>/", views.verify, name="verify"),
    path(
        "api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
