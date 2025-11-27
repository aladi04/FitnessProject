from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
	"""Render the nutrition (meals) index page (login required)."""
	return render(request, 'nutrition/index.html', {})
