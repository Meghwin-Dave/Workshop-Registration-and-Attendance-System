from django.urls import path
from .  import views
from django.conf.urls.static import static
from django.conf import settings
from .views import feedback_view

urlpatterns = [
    path("", views.home,name='home'),
    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('show_workshop', views.show_workshop, name="show_workshop"),
    path('add_workshop', views.add_workshop, name="add_workshop"),
    path('edit_workshop/<int:pk>', views.edit_workshop, name="edit_workshop"),
    path('delete_workshop/<int:pk>', views.delete_workshop, name="delete_workshop"),
    
    path('save_group_details/<int:pk>', views.save_group_details, name="save_group_details"),
    path('edit_number_of_groups/<int:pk>', views.edit_number_of_groups, name="edit_number_of_groups"),
    path('get-designations-and-groups/<int:workshop_id>/', views.get_designations_and_groups, name='get_designations_and_groups'),
    path('close_workshop/<int:pk>', views.close_workshop, name="close_workshop"),
    
    path('show_visitors/<int:pk>', views.show_visitors, name="show_visitors"),
    path('register/<str:workshop_uuid>', views.visitor_registration_form, name="visitor_registration_form"),
    path('show-feedback/<uuid:visitor_uuid>/', views.show_feedback, name='show_feedback'),
    
    path('edit-visitor-details/', views.edit_visitor_details, name='edit_visitor_details'),
    
    path('save_designation_details/<int:pk>/', views.save_designation_details, name='save_designation_details'),
    
    path('add_feedback/', views.add_feedback, name='add_feedback'),
    path('workshop/<int:workshop_id>/send-emails/', views.send_emails, name='send_emails'),
    
    
    path('workshop/<int:workshop_id>/feedback/<uuid:visitor_uuid>/', views.feedback_view, name='feedback'),
    path('workshop/feedback', views.sms_feedback, name='sms_feedback'),
    
    path('workshop/<int:workshop_id>/send_feedback_emails/', views.send_feedback_emails, name='send_feedback_emails'),
    
    path('show_users', views.show_users, name="show_users"),
    path('add_user', views.add_user, name="add_user"),
    path('edit_user/<int:pk>', views.edit_user, name="edit_user"),
    path('delete_user/<int:pk>', views.delete_user, name="delete_user"),
    path('change_password/<int:pk>', views.change_password, name="change_password"),
    

    path('qr_scanner/<int:workshop_id>/', views.workshop_scanner, name='workshop_scanner'),
    # path('qr_scanner/', views.qr_scanner, name='qr_scanner'),
    path('generate_qr_code/<int:visitor_id>', views.generate_qr_code, name='generate_qr_code'),
    
    path('verify_visitor/<uuid:uuid>/<int:workshop_id>', views.verify_visitor, name='verify_visitor'),
    path('mark-attendance/<str:workshop_id>/<str:uuid>/',views.mark_attendance,name='mark_attendance'),
    path('ticket/<int:visitor_id>/', views.generate_ticket, name='generate_ticket'),
    
   
    path('ticket', views.sms_ticket, name='sms_ticket'),
    path('download_ticket/<int:id>/', views.download_ticket, name='download_ticket'),

    # --- Advanced Features Routes ---
    # API Endpoints
    path('api/workshop-stats/<uuid:workshop_uuid>/', views.api_workshop_stats, name='api_workshop_stats'),
    path('api/table-occupancy/<uuid:workshop_uuid>/', views.api_table_occupancy, name='api_table_occupancy'),
    path('api/live-poll/<uuid:workshop_uuid>/', views.api_live_poll, name='api_live_poll'),
    path('api/poll-vote/<int:poll_id>/', views.api_poll_vote, name='api_poll_vote'),
    path('api/leaderboard/<uuid:workshop_uuid>/', views.api_leaderboard, name='api_leaderboard'),
    path('api/feedback-sentiment/<uuid:workshop_uuid>/', views.api_feedback_sentiment, name='api_feedback_sentiment'),

    # Manager Pages
    path('workshop/<int:pk>/live-dashboard/', views.live_dashboard, name='live_dashboard'),
    path('workshop/<int:pk>/polls/', views.poll_management, name='poll_management'),
    path('workshop/<int:pk>/polls/create/', views.create_poll, name='create_poll'),
    path('poll/<int:poll_id>/toggle/', views.toggle_poll, name='toggle_poll'),
    path('workshop/<int:workshop_id>/polls/send-email/', views.send_poll_emails, name='send_poll_emails'),
    path('workshop/<int:pk>/leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('workshop/<int:pk>/feedback-analytics/', views.feedback_analytics_view, name='feedback_analytics'),

    # Visitor Pages
    path('poll/<uuid:visitor_uuid>/', views.visitor_poll, name='visitor_poll'),
    path('leaderboard/<uuid:workshop_uuid>/', views.visitor_leaderboard, name='visitor_leaderboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)