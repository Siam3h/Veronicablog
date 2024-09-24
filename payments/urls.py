from django.urls import path
from . import views

urlpatterns = [
    path('projects', views.project_list, name='projects'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('payment/<int:project_id>/', views.process_payment, name='process_payment'),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('thankyou/<int:transaction_id>/', views.thankyou, name='thankyou'),
]
