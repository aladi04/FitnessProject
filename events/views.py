from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Event, Booking
from .forms import EventSearchForm, BookingForm

def event_list(request):
    events = Event.objects.filter(date__gte=timezone.now())
    form = EventSearchForm(request.GET or None)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        
        if search:
            events = events.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        if location:
            events = events.filter(location__icontains=location)
    
    context = {
        'events': events,
        'form': form,
        'search_query': request.GET.get('search', ''),
        'location_query': request.GET.get('location', ''),
    }
    return render(request, 'events/event_list.html', context)

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_booking = None
    
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            user=request.user,
            event=event,
            is_cancelled=False
        ).first()
    
    if request.method == 'POST':
        if user_booking:
            messages.warning(request, 'You have already booked this event.')
            return redirect('event-detail', pk=pk)
        
        # Check event availability
        if not event.is_available:
            messages.error(request, 'This event is fully booked.')
            return redirect('event-detail', pk=pk)
        
        # Check if event is in the future
        if event.date <= timezone.now():
            messages.error(request, 'Cannot book past events.')
            return redirect('event-detail', pk=pk)
        
        # Create the booking directly
        try:
            booking = Booking.objects.create(
                user=request.user,
                event=event
            )
            messages.success(request, f'Successfully booked "{event.title}"!')
            return redirect('booking-history')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('event-detail', pk=pk)
    
    # For GET requests, just show the form
    form = BookingForm()
    
    context = {
        'event': event,
        'form': form,
        'user_booking': user_booking,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related('event')
    
    # Separate active and cancelled bookings
    active_bookings = bookings.filter(is_cancelled=False, event__date__gte=timezone.now())
    past_bookings = bookings.filter(event__date__lt=timezone.now())
    cancelled_bookings = bookings.filter(is_cancelled=True)
    
    context = {
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'events/booking_history.html', context)

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if booking.is_cancelled:
        messages.warning(request, 'This booking is already cancelled.')
    elif booking.event.date <= timezone.now():
        messages.error(request, 'Cannot cancel booking for past events.')
    else:
        booking.cancel()
        messages.success(request, f'Booking for "{booking.event.title}" has been cancelled.')
    
    return redirect('booking-history')