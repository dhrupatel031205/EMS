# Event Management System

A Django-based event management system that allows users to create, manage, and RSVP to events.

## Features

- **User Authentication**: Registration, login, and profile management
- **Event Management**: Create, edit, and delete events
- **RSVP System**: Users can RSVP to events with status (Going/Maybe/Not Going)
- **Profile Management**: User profiles with organized events and RSVPs
- **Event Discovery**: Browse public events with search and filtering
- **Validation**: Form validation for dates, locations, and required fields

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Run the server:
   ```bash
   python manage.py runserver
   ```

## Usage

- Visit `/` to view events
- Register/login to create events and RSVP
- Access profile page to view organized events and RSVPs
- Create events with proper validation for dates and location

## API Endpoints

- `/api/events/` - Event CRUD operations
- `/api/rsvps/` - RSVP management
- `/api/reviews/` - Event reviews

## Technologies

- Django 4.x
- Django REST Framework
- SQLite Database
- Bootstrap 5
- HTML/CSS/JavaScript