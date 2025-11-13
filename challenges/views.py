from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Challenge, Participant, Score
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q


def index(request):
    """Render the challenges index page.

    - Shows all challenges by default (status=all).
    - Supports ?q= for searching title/description and ?status=active|upcoming|done|all
    - Attaches per-challenge: joined (bool), leaderboard (top 3), user_rank (int or None)
    - Challenges include a `status` property on the model.
    """
    # Filters: search (q) and status (all|active|upcoming|done)
    now = timezone.now()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')  # default: show all challenges

    # select_related for created_by to avoid extra queries in template
    qs = Challenge.objects.select_related('created_by').all()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(created_by__username__icontains=q)
        )

    if status == 'active':
        qs = qs.filter(start_date__lte=now, end_date__gte=now, is_active=True)
    elif status == 'upcoming':
        qs = qs.filter(start_date__gt=now, is_active=True)
    elif status == 'done':
        qs = qs.filter(Q(end_date__lt=now) | Q(is_active=False))
    # else 'all' -> no extra filtering

    # order by start_date descending (most recent/soonest first)
    challenges = qs.order_by('-start_date')
    # Attach per-challenge helper data to avoid dict lookups in template
    for ch in challenges:
        # attach top-3 leaderboard entries (list of dicts {'user': User, 'points': float})
        ch.leaderboard = ch.get_leaderboard(top=3)
        ch.user_rank = ch.get_user_rank(request.user) if request.user.is_authenticated else None
        ch.joined = Participant.objects.filter(challenge=ch, user=request.user).exists() if request.user.is_authenticated else False

    # Also provide a short list of upcoming challenges (for a separate UI block)
    upcoming_challenges = Challenge.objects.filter(start_date__gt=now, is_active=True).order_by('start_date')[:5]
    for ch in upcoming_challenges:
        ch.leaderboard = ch.get_leaderboard(top=5)
        ch.user_rank = ch.get_user_rank(request.user) if request.user.is_authenticated else None
        ch.joined = Participant.objects.filter(challenge=ch, user=request.user).exists() if request.user.is_authenticated else False

    context = {
        'challenges': challenges,
        'upcoming_challenges': upcoming_challenges,
        'q': q,
        'status': status,
    }
    return render(request, 'challenges/index.html', context)


@login_required
@require_POST
def join_challenge(request, challenge_id):
    """Handle a POST request to join a challenge.

    Named `join_challenge` to match the URLconf in `challenges/urls.py`.
    """
    ch = get_object_or_404(Challenge, pk=challenge_id)
    # Only allow joining active challenges
    if ch.status != 'active':
        messages.error(request, "You can only join challenges that are currently active.")
        return redirect('challenge-list')

    participant, created = Participant.objects.get_or_create(user=request.user, challenge=ch)
    if created:
        messages.success(request, f"You joined '{ch.title}'. You can now submit scores.")
    else:
        messages.info(request, f"You're already joined in '{ch.title}'.")
    return redirect('challenge-list')


@login_required
def submit_score(request, challenge_id):
    """Allow a user to submit (or update) their score for a challenge."""
    ch = get_object_or_404(Challenge, pk=challenge_id)
    # Ensure participant exists
    Participant.objects.get_or_create(user=request.user, challenge=ch)

    if request.method == 'POST':
        points_raw = request.POST.get('points')
        try:
            points = float(points_raw)
        except (TypeError, ValueError):
            messages.error(request, 'Please provide a valid numeric score.')
            return redirect('challenge-submit', challenge_id=ch.id)

        score, created = Score.objects.update_or_create(
            user=request.user,
            challenge=ch,
            defaults={'points': points}
        )
        messages.success(request, 'Your score has been submitted.')
        return redirect('challenge-list')

    # GET -> render a simple form
    return render(request, 'challenges/submit_score.html', {'challenge': ch})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Challenge, Participant, Score
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q


def index(request):
    """Render the challenges index page.

    - Shows all challenges by default (status=all).
    - Supports ?q= for searching title/description and ?status=active|upcoming|done|all
    - Attaches per-challenge: joined (bool), leaderboard (top 3), user_rank (int or None)
    - Challenges include a `status` property on the model.
    """
    # Filters: search (q) and status (all|active|upcoming|done)
    now = timezone.now()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')  # default: show all challenges

    # select_related for created_by to avoid extra queries in template
    qs = Challenge.objects.select_related('created_by').all()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(created_by__username__icontains=q)
        )

    if status == 'active':
        qs = qs.filter(start_date__lte=now, end_date__gte=now, is_active=True)
    elif status == 'upcoming':
        qs = qs.filter(start_date__gt=now, is_active=True)
    elif status == 'done':
        qs = qs.filter(Q(end_date__lt=now) | Q(is_active=False))
    # else 'all' -> no extra filtering

    # order by start_date descending (most recent/soonest first)
    challenges = qs.order_by('-start_date')
    # Attach per-challenge helper data to avoid dict lookups in template
    for ch in challenges:
        # attach top-3 leaderboard entries (list of dicts {'user': User, 'points': float})
        ch.leaderboard = ch.get_leaderboard(top=3)
        ch.user_rank = ch.get_user_rank(request.user) if request.user.is_authenticated else None
        ch.joined = Participant.objects.filter(challenge=ch, user=request.user).exists() if request.user.is_authenticated else False

    # Also provide a short list of upcoming challenges (for a separate UI block)
    upcoming_challenges = Challenge.objects.filter(start_date__gt=now, is_active=True).order_by('start_date')[:5]
    for ch in upcoming_challenges:
        ch.leaderboard = ch.get_leaderboard(top=5)
        ch.user_rank = ch.get_user_rank(request.user) if request.user.is_authenticated else None
        ch.joined = Participant.objects.filter(challenge=ch, user=request.user).exists() if request.user.is_authenticated else False

    context = {
        'challenges': challenges,
        'upcoming_challenges': upcoming_challenges,
        'q': q,
        'status': status,
    }
    return render(request, 'challenges/index.html', context)


@login_required
@require_POST
def join_challenge(request, challenge_id):
    """Handle a POST request to join a challenge.

    Named `join_challenge` to match the URLconf in `challenges/urls.py`.
    """
    ch = get_object_or_404(Challenge, pk=challenge_id)
    # Only allow joining active challenges
    if ch.status != 'active':
        messages.error(request, "You can only join challenges that are currently active.")
        return redirect('challenge-list')

    participant, created = Participant.objects.get_or_create(user=request.user, challenge=ch)
    if created:
        messages.success(request, f"You joined '{ch.title}'. You can now submit scores.")
    else:
        messages.info(request, f"You're already joined in '{ch.title}'.")
    return redirect('challenge-list')


@login_required
def submit_score(request, challenge_id):
    """Allow a user to submit (or update) their score for a challenge."""
    ch = get_object_or_404(Challenge, pk=challenge_id)
    # Ensure participant exists
    Participant.objects.get_or_create(user=request.user, challenge=ch)

    if request.method == 'POST':
        points_raw = request.POST.get('points')
        try:
            points = float(points_raw)
        except (TypeError, ValueError):
            messages.error(request, 'Please provide a valid numeric score.')
            return redirect('challenge-submit', challenge_id=ch.id)

        score, created = Score.objects.update_or_create(
            user=request.user,
            challenge=ch,
            defaults={'points': points}
        )
        messages.success(request, 'Your score has been submitted.')
        return redirect('challenge-list')

    # GET -> render a simple form
    return render(request, 'challenges/submit_score.html', {'challenge': ch})
