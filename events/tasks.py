from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, RSVP


@shared_task
def send_event_notification(event_id, notification_type, user_email=None):
    """
    Send email notifications for events
    """
    try:
        event = Event.objects.get(id=event_id)
        
        if notification_type == 'event_created':
            subject = f'New Event Created: {event.title}'
            message = f'''
            A new event has been created!
            
            Event: {event.title}
            Description: {event.description}
            Location: {event.location}
            Start Time: {event.start_time}
            End Time: {event.end_time}
            Organizer: {event.organizer.username}
            '''
            
            # Send to all users who have RSVP'd to organizer's previous events
            previous_attendees = RSVP.objects.filter(
                event__organizer=event.organizer,
                status='Going'
            ).values_list('user__email', flat=True).distinct()
            
            recipient_list = list(previous_attendees)
            
        elif notification_type == 'event_updated':
            subject = f'Event Updated: {event.title}'
            message = f'''
            An event you're interested in has been updated!
            
            Event: {event.title}
            Description: {event.description}
            Location: {event.location}
            Start Time: {event.start_time}
            End Time: {event.end_time}
            '''
            
            # Send to all users who have RSVP'd to this event
            recipient_list = list(event.rsvps.values_list('user__email', flat=True))
            
        elif notification_type == 'rsvp_confirmation':
            subject = f'RSVP Confirmation: {event.title}'
            message = f'''
            Your RSVP has been confirmed!
            
            Event: {event.title}
            Location: {event.location}
            Start Time: {event.start_time}
            End Time: {event.end_time}
            
            We look forward to seeing you there!
            '''
            recipient_list = [user_email] if user_email else []
        
        else:
            return False
        
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return True
        
    except Event.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    
    return False


@shared_task
def send_event_reminder(event_id):
    """
    Send reminder emails 24 hours before event
    """
    try:
        event = Event.objects.get(id=event_id)
        
        subject = f'Event Reminder: {event.title} - Tomorrow!'
        message = f'''
        Don't forget about the event tomorrow!
        
        Event: {event.title}
        Location: {event.location}
        Start Time: {event.start_time}
        End Time: {event.end_time}
        
        See you there!
        '''
        
        # Send to all users who RSVP'd as 'Going'
        recipient_list = list(
            event.rsvps.filter(status='Going').values_list('user__email', flat=True)
        )
        
        if recipient_list:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            return True
            
    except Event.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error sending reminder: {e}")
        return False
    
    return False