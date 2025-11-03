from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'location']
    search_fields = ['user__username', 'full_name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'location', 'start_time', 'is_public']
    list_filter = ['is_public', 'start_time', 'location']
    search_fields = ['title', 'description', 'organizer__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['event__title', 'user__username']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['event__title', 'user__username']
