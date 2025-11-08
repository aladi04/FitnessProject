from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
	"""Render the workouts index page (login required)."""
	return render(request, 'workouts/index.html', {})
