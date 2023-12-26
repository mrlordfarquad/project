from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('form/list', views.form_list_view, name="form_list"),
    path('register', views.register, name="register"),
    path('about-us/', views.about_us, name='about_us'),
    path('change_profile_image/', views.change_profile_image, name='change_profile_image'),
    path('delete_profile_image/', views.delete_profile_image, name='delete_profile_image'),
    path('change-username/', views.change_username, name='change_username'),
    path('change-email/', views.change_email, name='change_email'),
    path('change-gender/', views.change_gender, name='change_gender'),
    path('change_date_of_birth/', views.change_date_of_birth, name='change_date_of_birth'),
    path('delete_date_of_birth/', views.delete_date_of_birth, name='delete_date_of_birth'),
    path('change_city/', views.change_city, name='change_city'),
    path('profile/<int:pk>/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('form/<str:code>/export_csv', views.exportcsv,name='export_csv'),
    path('logout', views.logout_view, name="logout"),
    path('form/create', views.create_form, name="create_form"),
    path('form/create/contact', views.contact_form_template, name="contact_form_template"),
    path('form/create/feedback', views.customer_feedback_template, name="customer_feedback_template"),
    path('form/create/event', views.event_registration_template, name="event_registration_template"),
    path('form/create/survey', views.social_survey_template, name="social_survey_template"),
    path('form/<str:code>/edit', views.edit_form, name="edit_form"),
    path('form/<str:code>/edit_title', views.edit_title, name="edit_title"),
    path('form/<str:code>/edit_description', views.edit_description, name="edit_description"),
    path('form/<str:code>/edit_background_color', views.edit_bg_color, name="edit_background_color"),
    path('form/<str:code>/edit_text_color', views.edit_text_color, name="edit_text_color"),
    path('form/<str:code>/edit_setting', views.edit_setting, name="edit_setting"),
    path('form/<str:code>/delete', views.delete_form, name="delete_form"),
    path('form/<str:code>/edit_question', views.edit_question, name="edit_question"),
    path('form/<str:code>/edit_choice', views.edit_choice, name="edit_choice"),
    path('form/<str:code>/add_choice', views.add_choice, name="add_choice"),
    path('form/<str:code>/remove_choice', views.remove_choice, name="remove_choice"),
    path('form/<str:code>/get_choice/<str:question>', views.get_choice, name="get_choice"),
    path('form/<str:code>/add_question', views.add_question, name="add_question"),
    path('form/<str:code>/delete_question/<str:question>', views.delete_question, name="delete_question"),
    path('form/<str:code>/score', views.score, name="score"),
    path('form/<str:code>/edit_score', views.edit_score, name="edit_score"),
    path('form/<str:code>/answer_key', views.answer_key, name="answer_key"),
    path('form/<str:code>/feedback', views.feedback, name="feedback"),
    path('form/<str:code>/viewform', views.view_form, name="view_form"),
    path('form/<str:code>/submit', views.submit_form, name="submit_form"),
    path('form/<str:code>/responses', views.responses, name='responses'),
    path('form/<str:code>/response/<str:response_code>', views.response, name="response"),
    path('form/<str:code>/response/<str:response_code>/edit', views.edit_response, name="edit_response"),
    path('form/<str:code>/responses/delete', views.delete_responses, name="delete_responses"),
    path('403', views.FourZeroThree, name="403"),
    path('404', views.FourZeroFour, name="404"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name ='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name ='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name ='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += [re_path(r'^.*/$', views.FourZeroFour)]