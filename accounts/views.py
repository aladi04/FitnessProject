from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.shortcuts import redirect


def landing_page(request):
    """Render the landing page for non-authenticated users."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')

def dashboard(request):
    """Render the dashboard for authenticated users."""
    if not request.user.is_authenticated:
        return redirect('landing')
    
    context = {
        'upcoming_events': [],
        'active_challenges': [],
        'recent_posts': [],
    }
    return render(request, 'home.html', context)


@login_required
def profile(request):
	"""Simple profile placeholder view for development."""
	return render(request, 'accounts/profile.html', {})


@require_POST
def logout_view(request):
	"""Log the user out and redirect to the homepage.

	This view accepts POST only for safety. The navbar logout button posts to this URL.
	"""
	logout(request)
	return redirect('home')


def signup(request):
	"""Signup view using Django's UserCreationForm.

	On successful POST the user is logged in and redirected to 'home'.
	This is a simple, low-risk implementation suitable for development.
	"""
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect('home')
	else:
		form = UserCreationForm()
	return render(request, 'registration/signup.html', {'form': form})
