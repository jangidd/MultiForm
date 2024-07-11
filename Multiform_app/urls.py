from django.urls import path
from . import views
from .views import callback_form_view, callback_complete_view   

urlpatterns = [
    path('', views.login, name = 'login'),
    path('radiologist', views.index, name='index'), 
    path('work', views.work, name='work'), 
    path('coordinator', views.coordinator, name = 'coordinator'),
    path('step1/', views.step1, name='step1'),
    path('step2/', views.step2, name='step2'),
    path('step3/', views.step3, name='step3'),
    path('step4/', views.step4, name='step4'),
    path('step5/', views.step5, name='step5'),
    path('step6/', views.step6, name='step6'),
    path('step7/', views.step7, name='step7'),
    path('submit/', views.submit, name='submit'),
    path('registration_pending/<int:pk>/', views.registration_pending, name='registration_pending'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('coordinator/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('supercoordinator/', views.supercoordinator_dashboard, name='supercoordinator_dashboard'),
    # path('update_status/<int:pk>/', views.update_status, name='update_status'),
    path('update_stage1status/<int:pk>/', views.update_stage1status, name='update_stage1status'),
    path('update_stage2status/<int:pk>/', views.update_stage2status, name='update_stage2status'),
    # the below url is for handling the logic of the callback form page.
    path('callback-form/', callback_form_view, name='callback_form'),
    path('callback-complete/', callback_complete_view, name='callback_complete'),
    path('view_complete_form/<int:pk>/', views.view_complete_form, name='view_complete_form'),
    path('update_messages/', views.update_messages, name='update_messages'),
    # The below url is for getting the response in pdf format.
    path('generate_pdf/<int:pk>/', views.generate_pdf, name='generate_pdf'),
    # This is the url to go to the success page after submitting the form.
    path('success/<int:pk>/', views.success, name='success'),
    # This is the url to see the response page after form submission.
    path('view_response/<int:pk>/', views.view_response, name='view_response'),
    # This is the url to go to the ratelist page.
    path('rate_list/<int:radiologist_id>/', views.rate_list, name='rate_list'),
    
    # This is the url to update the ratelist status.
    path('update_status_rate_list/', views.update_status_rate_list, name='update_status_rate_list'),
    path('check_email_existence/', views.check_email_existence, name='check_email_existence'),

 
    
]
