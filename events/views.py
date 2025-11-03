from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import Event, RSVP, Review, UserProfile
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsPublicEventOrInvited
from .tasks import send_event_notification
from .forms import EventForm, RSVPForm, CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['location', 'organizer']
    search_fields = ['title', 'description', 'location']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Show public events and private events where user is organizer or has RSVP
            return Event.objects.filter(
                models.Q(is_public=True) |
                models.Q(organizer=self.request.user) |
                models.Q(rsvps__user=self.request.user)
            ).distinct()
        else:
            # Show only public events for anonymous users
            return Event.objects.filter(is_public=True)
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if user can access this event
        if not instance.is_public and request.user != instance.organizer:
            if not request.user.is_authenticated or not instance.rsvps.filter(user=request.user).exists():
                return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        
        # Check if user can access this event
        if not event.is_public and request.user != event.organizer:
            if not event.rsvps.filter(user=request.user).exists():
                return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        rsvp_data = request.data.copy()
        rsvp_data['event'] = event.id
        
        try:
            rsvp = RSVP.objects.get(event=event, user=request.user)
            serializer = RSVPSerializer(rsvp, data=rsvp_data, context={'request': request})
        except RSVP.DoesNotExist:
            serializer = RSVPSerializer(data=rsvp_data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def reviews(self, request, pk=None):
        event = self.get_object()
        
        # Check if user can access this event
        if not event.is_public and request.user != event.organizer:
            if not event.rsvps.filter(user=request.user).exists():
                return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            reviews = event.reviews.all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            review_data = request.data.copy()
            review_data['event'] = event.id
            
            serializer = ReviewSerializer(data=review_data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], url_path='rsvp/(?P<user_id>[^/.]+)', permission_classes=[permissions.IsAuthenticated])
    def update_rsvp(self, request, pk=None, user_id=None):
        event = self.get_object()
        
        # Only allow users to update their own RSVP or organizer to update any RSVP
        if request.user.id != int(user_id) and request.user != event.organizer:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        rsvp = get_object_or_404(RSVP, event=event, user_id=user_id)
        serializer = RSVPSerializer(rsvp, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RSVPViewSet(viewsets.ModelViewSet):
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RSVP.objects.filter(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


# Template-based views

def event_list(request):
    """Display list of events with filtering and pagination"""
    # Get filter parameters
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    organizer_filter = request.GET.get('organizer', '')

    # Base queryset
    if request.user.is_authenticated:
        events = Event.objects.filter(
            Q(is_public=True) |
            Q(organizer=request.user) |
            Q(rsvps__user=request.user)
        ).distinct()
    else:
        events = Event.objects.filter(is_public=True)

    # Apply filters
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if location_filter:
        events = events.filter(location__icontains=location_filter)

    if organizer_filter:
        events = events.filter(organizer_id=organizer_filter)

    # Annotate with RSVP count
    events = events.annotate(rsvp_count=Count('rsvps'))

    # Pagination
    paginator = Paginator(events, 12)  # 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all organizers for filter dropdown
    organizers = User.objects.filter(
        Q(organized_events__is_public=True) |
        Q(organized_events__rsvps__user=request.user)
    ).distinct() if request.user.is_authenticated else User.objects.filter(organized_events__is_public=True).distinct()

    context = {
        'events': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'organizers': organizers,
        'request': request,
    }

    return render(request, 'events/event_list.html', context)


def event_detail(request, event_id):
    """Display event details"""
    if request.user.is_authenticated:
        event = get_object_or_404(
            Event,
            Q(id=event_id) & (
                Q(is_public=True) |
                Q(organizer=request.user) |
                Q(rsvps__user=request.user)
            )
        )
    else:
        event = get_object_or_404(Event, id=event_id, is_public=True)

    # Get RSVPs
    rsvps = event.rsvps.all().order_by('created_at')
    rsvp_count = rsvps.count()

    # Get user's RSVP if authenticated
    user_rsvp = None
    if request.user.is_authenticated:
        try:
            user_rsvp = RSVP.objects.get(event=event, user=request.user)
        except RSVP.DoesNotExist:
            pass

    context = {
        'event': event,
        'rsvps': rsvps,
        'rsvp_count': rsvp_count,
        'user_rsvp': user_rsvp,
    }

    return render(request, 'events/event_detail.html', context)


@login_required
def event_create(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {'form': form})


@login_required
def event_edit(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form})


@login_required
@require_POST
def event_delete(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('event_list')


@require_POST
@csrf_protect
@login_required
def rsvp_event(request, event_id):
    """Handle RSVP for an event"""
    if request.user.is_authenticated:
        event = get_object_or_404(
            Event,
            Q(id=event_id) & (
                Q(is_public=True) |
                Q(organizer=request.user) |
                Q(rsvps__user=request.user)
            )
        )
    else:
        event = get_object_or_404(Event, id=event_id, is_public=True)

    status_value = request.POST.get('status')
    if status_value in dict(RSVP.STATUS_CHOICES):
        rsvp, created = RSVP.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={'status': status_value}
        )
        if not created:
            rsvp.status = status_value
            rsvp.save()

        messages.success(request, f'RSVP updated to "{status_value}"')

    return redirect('event_detail', event_id=event.id)


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('event_list')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('event_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('event_list')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('event_list')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('event_list')


@login_required
def profile_view(request):
    """Display user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user, full_name=request.user.username)
    
    # Get user's organized events
    organized_events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    
    # Get user's RSVPs
    user_rsvps = RSVP.objects.filter(user=request.user).select_related('event').order_by('-created_at')
    
    context = {
        'profile': profile,
        'organized_events': organized_events,
        'user_rsvps': user_rsvps,
    }
    
    return render(request, 'registration/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user, full_name=request.user.username)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'registration/profile_edit.html', {'form': form})



