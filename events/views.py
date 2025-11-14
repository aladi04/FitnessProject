from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q,Sum, F
from django.db.models.functions import Coalesce
from .models import Event, Booking
from .forms import EventSearchForm, BookingForm, BookingUpdateForm

def event_list(request):
    # .filter() to get only UPCOMING events but we can use .all() instead to fetch all events 
    events = Event.objects.filter(date__gte=timezone.now())

    # annotate total booked and available seats so we can order by `available`
    events = events.annotate(
        total_booked=Coalesce(Sum('bookings__participants'), 0)
    ).annotate(
        available=F('capacity') - F('total_booked')
    )

    # search form handling
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

    # --- Sorting support ---
    # whitelist of allowed sort fields (map friendly name -> model/annotated field)
    allowed_sorts = {
        'date': 'date',
        'title': 'title',
        'location': 'location',
        'capacity': 'capacity',
        'created': 'created_at',
        'available': 'available',   # annotated field
    }

    sort = request.GET.get('sort', 'date')
    direction = request.GET.get('dir', 'asc')  # 'asc' or 'desc'

    sort_field = allowed_sorts.get(sort, 'date')  # fallback to date
    if direction == 'desc':
        order_by = f'-{sort_field}'
    else:
        order_by = sort_field

    events = events.order_by(order_by)

    context = {
        'events': events,
        'form': form,
        'search_query': request.GET.get('search', ''),
        'location_query': request.GET.get('location', ''),
        'current_sort': sort,
        'current_dir': direction,
        'allowed_sorts': allowed_sorts,  # helpful for template
    }
    return render(request, 'events/event_list.html', context)




@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_booking = None
    
    if request.user.is_authenticated:
        user_booking = Booking.objects.filter(
            user=request.user,
            event=event
        ).first()
    
    if request.method == 'POST':
        if user_booking:
            messages.warning(request, 'You have already booked this event.')
            return redirect('event-detail', pk=pk)
        
        form = BookingForm(request.POST, event=event, user=request.user)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.event = event
                booking.user = request.user
                booking.save()
                messages.success(request, f'Successfully booked "{event.title}" for {booking.participants} participant(s)!')
                return redirect('booking-history')
            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(event=event, user=request.user)
    
    context = {
        'event': event,
        'form': form,
        'user_booking': user_booking,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related('event')

    # Sorting for bookings: whitelist
    allowed_bsorts = {
        'booked_at': 'booked_at',
        'updated_at': 'updated_at',
        'participants': 'participants',
        'event_date': 'event__date',
        'event_title': 'event__title',
    }
    sort = request.GET.get('sort', 'event_date')
    direction = request.GET.get('dir', 'asc')

    sort_field = allowed_bsorts.get(sort, 'event__date')
    if direction == 'desc':
        order_by = f'-{sort_field}'
    else:
        order_by = sort_field

    # Separate upcoming and past bookings and apply ordering
    upcoming_bookings = bookings.filter(event__date__gte=timezone.now()).order_by(order_by)
    past_bookings = bookings.filter(event__date__lt=timezone.now()).order_by(order_by)

    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'current_sort': sort,
        'current_dir': direction,
        'allowed_bsorts': allowed_bsorts,
    }
    return render(request, 'events/booking_history.html', context)

@login_required
def update_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BookingUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            try:
                updated_booking = form.save()
                messages.success(request, f'Booking updated to {updated_booking.participants} participant(s)!')
                return redirect('booking-history')
            except Exception as e:
                messages.error(request, f'Error updating booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingUpdateForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
    }
    return render(request, 'events/update_booking.html', context)

@login_required
def delete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    if request.method == 'POST':
        event_title = booking.event.title
        booking.delete()
        messages.success(request, f'Booking for "{event_title}" has been deleted.')
        return redirect('booking-history')
    
    context = {
        'booking': booking,
    }
    return render(request, 'events/delete_booking.html', context)