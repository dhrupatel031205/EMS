from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet, RSVPViewSet, ReviewViewSet,
    event_list, event_detail, event_create, event_edit, event_delete,
    rsvp_event, register_view, login_view, logout_view, profile_view, profile_edit,
    submit_review, delete_review
)

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'rsvps', RSVPViewSet, basename='rsvp')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Template URLs
    path('', event_list, name='event_list'),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path('events/create/', event_create, name='create_event'),
    path('events/<int:event_id>/edit/', event_edit, name='edit_event'),
    path('events/<int:event_id>/delete/', event_delete, name='delete_event'),
    path('events/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),
    path('events/<int:event_id>/review/', submit_review, name='submit_review'),
    path('events/<int:event_id>/review/delete/', delete_review, name='delete_review'),
    
    # Auth URLs
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
]
