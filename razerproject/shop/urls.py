from django.urls import path
from . import views
from .views import RazerUserListCreateView
urlpatterns = [
    path("", views.django_user_signup_interface, name="signup-interface"),
    path("django-login-interface/", views.django_user_login_interface, name="login-interface"),
    path("django-signup/", views.django_user_signup_view, name="django-signup"),
    path("django-login/", views.django_user_login_view, name="django-login"),
    path("run", views.run_view, name="run"),
    path("form", views.form_view, name="form"),
    path("form-operation", views.form_view_operation, name="form-operation"),
    path("get-product-info", views.get_product_info, name="get-product-info"),
    path('razerusers/', RazerUserListCreateView.as_view(), name='razerusers'),
    path("download-results/", views.download_results, name="download_results"),
    path("save-and-store-file/", views.save_and_store_file, name="save_and_store_file"),

]

