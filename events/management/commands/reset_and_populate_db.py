from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from events.models import UserProfile, Event, RSVP, Review
from django.utils import timezone
from datetime import timedelta, datetime
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Clear all data and populate database with showcase data'

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing data...')
        
        # Clear all existing data
        Review.objects.all().delete()
        RSVP.objects.all().delete()
        Event.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        
        self.stdout.write('Creating users and profiles...')
        
        # Create sample users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'full_name': 'John Doe', 'bio': 'Event enthusiast and tech lover', 'location': 'San Francisco, CA'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'full_name': 'Jane Smith', 'bio': 'Professional event organizer', 'location': 'New York, NY'},
            {'username': 'mike_jones', 'email': 'mike@example.com', 'full_name': 'Mike Jones', 'bio': 'Music festival fanatic', 'location': 'Austin, TX'},
            {'username': 'sarah_wilson', 'email': 'sarah@example.com', 'full_name': 'Sarah Wilson', 'bio': 'Corporate event planner', 'location': 'Chicago, IL'},
            {'username': 'david_brown', 'email': 'david@example.com', 'full_name': 'David Brown', 'bio': 'Startup founder and networker', 'location': 'Seattle, WA'},
            {'username': 'emily_davis', 'email': 'emily@example.com', 'full_name': 'Emily Davis', 'bio': 'Marketing professional', 'location': 'Boston, MA'},
            {'username': 'alex_miller', 'email': 'alex@example.com', 'full_name': 'Alex Miller', 'bio': 'Software developer', 'location': 'Denver, CO'},
            {'username': 'lisa_garcia', 'email': 'lisa@example.com', 'full_name': 'Lisa Garcia', 'bio': 'Photography enthusiast', 'location': 'Miami, FL'},
        ]
        
        created_users = []
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='password123'
            )
            UserProfile.objects.create(
                user=user,
                full_name=user_data['full_name'],
                bio=user_data['bio'],
                location=user_data['location']
            )
            created_users.append(user)
        
        self.stdout.write('Creating events...')
        
        # Create sample events
        events_data = [
            {
                'title': 'Tech Innovation Summit 2024',
                'description': 'Join industry leaders for a day of cutting-edge technology discussions, networking opportunities, and innovation showcases. This summit brings together the brightest minds in tech to explore emerging trends and future possibilities.',
                'organizer': created_users[1],  # jane_smith
                'location': 'Moscone Center, San Francisco',
                'start_time': timezone.now() + timedelta(days=10),
                'end_time': timezone.now() + timedelta(days=10, hours=8),
                'is_public': True
            },
            {
                'title': 'Summer Music Festival',
                'description': 'Experience an unforgettable weekend of live music featuring top artists from around the world. Three stages, food trucks, art installations, and camping available. Get ready for the ultimate summer celebration!',
                'organizer': created_users[2],  # mike_jones
                'location': 'Zilker Park, Austin',
                'start_time': timezone.now() + timedelta(days=20),
                'end_time': timezone.now() + timedelta(days=22),
                'is_public': True
            },
            {
                'title': 'Startup Networking Night',
                'description': 'Connect with fellow entrepreneurs, investors, and mentors in a relaxed atmosphere. Perfect for founders looking to expand their network and explore collaboration opportunities.',
                'organizer': created_users[4],  # david_brown
                'location': 'WeWork Downtown, Seattle',
                'start_time': timezone.now() + timedelta(days=5),
                'end_time': timezone.now() + timedelta(days=5, hours=3),
                'is_public': True
            },
            {
                'title': 'Photography Workshop',
                'description': 'Learn professional photography techniques from industry experts. Covering composition, lighting, post-processing, and building your portfolio. Bring your camera and creativity!',
                'organizer': created_users[7],  # lisa_garcia
                'location': 'Art District Studio, Miami',
                'start_time': timezone.now() + timedelta(days=15),
                'end_time': timezone.now() + timedelta(days=15, hours=6),
                'is_public': True
            },
            {
                'title': 'Corporate Team Building Retreat',
                'description': 'Exclusive corporate event focused on team cohesion and leadership development. Activities include problem-solving challenges, outdoor adventures, and strategic planning sessions.',
                'organizer': created_users[3],  # sarah_wilson
                'location': 'Resort & Conference Center, Chicago',
                'start_time': timezone.now() + timedelta(days=30),
                'end_time': timezone.now() + timedelta(days=32),
                'is_public': False
            },
            {
                'title': 'Web Development Bootcamp',
                'description': 'Intensive 3-day bootcamp covering modern web development technologies including React, Node.js, and cloud deployment. Perfect for developers looking to upgrade their skills.',
                'organizer': created_users[6],  # alex_miller
                'location': 'Tech Hub, Denver',
                'start_time': timezone.now() + timedelta(days=25),
                'end_time': timezone.now() + timedelta(days=27, hours=6),
                'is_public': True
            },
            {
                'title': 'Marketing Masterclass',
                'description': 'Learn cutting-edge digital marketing strategies from industry leaders. Covering social media marketing, content strategy, SEO, and data analytics for modern marketers.',
                'organizer': created_users[5],  # emily_davis
                'location': 'Business Center, Boston',
                'start_time': timezone.now() + timedelta(days=8),
                'end_time': timezone.now() + timedelta(days=8, hours=5),
                'is_public': True
            },
            {
                'title': 'Community Charity Run',
                'description': 'Annual 5K charity run supporting local education initiatives. All fitness levels welcome. Post-race celebration with food, music, and community awards.',
                'organizer': created_users[0],  # john_doe
                'location': 'Central Park, New York',
                'start_time': timezone.now() + timedelta(days=12),
                'end_time': timezone.now() + timedelta(days=12, hours=3),
                'is_public': True
            },
            {
                'title': 'AI & Machine Learning Conference',
                'description': 'Explore the latest advancements in artificial intelligence and machine learning. Keynote speeches, technical workshops, and networking with AI researchers and practitioners.',
                'organizer': created_users[1],  # jane_smith
                'location': 'Convention Center, San Francisco',
                'start_time': timezone.now() + timedelta(days=35),
                'end_time': timezone.now() + timedelta(days=37),
                'is_public': True
            },
            {
                'title': 'Food & Wine Tasting Evening',
                'description': 'Indulge in exquisite culinary creations paired with fine wines from renowned vineyards. Limited seating for an intimate gastronomic experience.',
                'organizer': created_users[3],  # sarah_wilson
                'location': 'Rooftop Restaurant, Chicago',
                'start_time': timezone.now() + timedelta(days=18),
                'end_time': timezone.now() + timedelta(days=18, hours=4),
                'is_public': True
            }
        ]
        
        created_events = []
        for event_data in events_data:
            event = Event.objects.create(**event_data)
            created_events.append(event)
        
        self.stdout.write('Creating RSVPs...')
        
        # Create RSVPs
        status_choices = ['Going', 'Maybe', 'Not Going']
        for event in created_events:
            # Random users RSVP to each event (excluding the organizer)
            potential_attendees = [u for u in created_users if u != event.organizer]
            num_rsvps = random.randint(3, len(potential_attendees))
            
            for user in random.sample(potential_attendees, num_rsvps):
                RSVP.objects.create(
                    event=event,
                    user=user,
                    status=random.choice(status_choices)
                )
        
        self.stdout.write('Creating reviews...')
        
        # Create reviews for past events (events that have already happened)
        past_events = [e for e in created_events if e.start_time < timezone.now()]
        for event in past_events:
            # Random users who RSVP'd as "Going" review the event
            going_rsvps = RSVP.objects.filter(event=event, status='Going')
            for rsvp in random.sample(list(going_rsvps), min(3, len(going_rsvps))):
                review_comments = [
                    "Amazing event! Well organized and great content.",
                    "Fantastic experience. Would definitely attend again.",
                    "Good event overall, but could use better timing.",
                    "Excellent networking opportunities and valuable insights.",
                    "Great venue and speakers. Looking forward to next year!",
                    "Well worth the time and investment. Highly recommend.",
                    "Incredible atmosphere and very well managed.",
                    "Learned a lot and met some amazing people."
                ]
                
                Review.objects.create(
                    event=event,
                    user=rsvp.user,
                    rating=random.randint(4, 5),
                    comment=random.choice(review_comments)
                )
        
        # Create some mixed reviews for variety
        for event in created_events[:3]:
            going_rsvps = RSVP.objects.filter(event=event, status='Going')
            if going_rsvps.exists():
                for rsvp in random.sample(list(going_rsvps), min(2, len(going_rsvps))):
                    mixed_comments = [
                        "Good event but room for improvement in organization.",
                        "Decent content, but the venue was too crowded.",
                        "Some technical issues but overall positive experience.",
                        "Great speakers but poor time management."
                    ]
                    
                    Review.objects.create(
                        event=event,
                        user=rsvp.user,
                        rating=random.randint(3, 4),
                        comment=random.choice(mixed_comments)
                    )
        
        self.stdout.write(self.style.SUCCESS('Database successfully reset and populated with showcase data!'))
        
        # Display summary
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'Users created: {User.objects.count()}')
        self.stdout.write(f'Events created: {Event.objects.count()}')
        self.stdout.write(f'RSVPs created: {RSVP.objects.count()}')
        self.stdout.write(f'Reviews created: {Review.objects.count()}')
