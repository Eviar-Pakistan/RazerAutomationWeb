from django.urls import path
from . import views
from .views import RazerUserListCreateView
urlpatterns = [
    path("", views.django_user_login_interface, name="login-interface"),
    path("su/", views.django_user_signup_interface, name="signup-interface"),
    path("login/", views.django_user_login_interface, name="login-interface"),
    path("django-signup/", views.django_user_signup_view, name="django-signup"),
    path("django-login/", views.django_user_login_view, name="django-login"),
    path("run", views.run_view, name="run"),
    path("form", views.form_view, name="form"),
    path("form-operation", views.form_view_operation, name="form-operation"),
    path("get-product-info", views.get_product_info, name="get-product-info"),
    path('razerusers/', RazerUserListCreateView.as_view(), name='razerusers'),
    path("download-results/", views.download_results, name="download_results"),
    path("save-and-store-file/", views.save_and_store_file, name="save_and_store_file"),
    path("get-user-files/", views.get_user_files, name="get_user_files"),
    path("start-login/", views.start_login, name="start-login"),
    path("submit-otp/", views.submit_otp, name="submit-otp"),
    path("checkUserExist/", views.check_user, name="checkUserExists"),
    path("shutdown_automation/", views.shutdown_automation, name="shutdown_automation"),


]

