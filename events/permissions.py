from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers of an event to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the organizer of the event
        return obj.organizer == request.user


class IsPublicEventOrInvited(permissions.BasePermission):
    """
    Custom permission to allow access to public events or private events for invited users.
    """
    
    def has_object_permission(self, request, view, obj):
        # Allow access to public events
        if obj.is_public:
            return True
        
        # For private events, check if user is the organizer or has RSVP'd
        if request.user.is_authenticated:
            return (obj.organizer == request.user or 
                   obj.rsvps.filter(user=request.user).exists())
        
        return False