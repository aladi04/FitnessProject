from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required

from .models import Member, Admin
from .forms import MemberForm, AdminForm
from .forms import SignupForm, VerifyCodeForm
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
User = get_user_model()


def landing_page(request):
    """Render the landing page for non-authenticated users."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')


def dashboard(request):
    """Render the dashboard for authenticated users."""

    context = {
        'upcoming_events': [],
        'active_challenges': [],
        'recent_posts': [],
    }
    return render(request, 'home.html', context)


@require_POST
def logout_view(request):
    """Log the user out and redirect to the homepage."""
    logout(request)
    return redirect('landing')

# Custom signup form for Member model


class MemberCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    # Add fitness fields
    age = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 25'})
    )
    gender = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Gender'),
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
            ('Prefer not to say', 'Prefer not to say')
        ]
    )
    height = forms.FloatField(
        required=False,
        min_value=50,
        max_value=250,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 175.5'})
    )
    weight = forms.FloatField(
        required=False,
        min_value=20,
        max_value=500,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g., 70.5'})
    )

    class Meta:
        model = Member
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                  'age', 'gender', 'height', 'weight')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = 'member'

        # Save fitness fields
        user.age = self.cleaned_data['age']
        user.gender = self.cleaned_data['gender']
        user.height = self.cleaned_data['height']
        user.weight = self.cleaned_data['weight']

        if commit:
            user.save()
        return user


def signup(request):
    """Signup view using custom MemberCreationForm."""
    if request.method == 'POST':
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            # Save the user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # inactive until verification
            code = str(random.randint(100000, 999999))
            user.verification_code = code
            user.save()  # save to generate user.id

            # Send verification email
            send_mail(
                'Your FitnessApp Verification Code',
                f'Use this code to verify your account: {code}',
                'harzalifarah@gmail.com',  # make sure it's a verified sender
                [user.email],
                fail_silently=False,
            )

            return redirect('verify_code', user_id=user.id)
    else:
        form = MemberCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


def verify_code_view(request, user_id):
    user = get_object_or_404(Member, id=user_id)
    if request.method == "POST":
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code == user.verification_code:
                user.email_verified = True
                user.is_active = True
                user.verification_code = ""
                user.save()
                messages.success(request, "Your email is verified! You can now login.")
                return redirect('login')
            else:
                messages.error(request, "Invalid verification code.")
    else:
        form = VerifyCodeForm()
    return render(request, 'accounts/verify_code.html', {'form': form})

def user_login(request):
    """Custom login view that works with Member model."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email (since USERNAME_FIELD should be email)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')

# ---- Simple guard for admin pages (temporary) ----


def admin_required(view_func):
    """
    Temporary decorator: checks if user is admin.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, "Admin access required.")
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper

# ---- Profile (view-only for a Member) ----


@login_required
def profile(request, user_id=None):
    # If no user_id provided, show current user's profile
    if user_id is None:
        member = request.user
    else:
        # Get the specific member
        member = get_object_or_404(Member, id=user_id)

    context = {
        'user': member,
    }
    return render(request, 'accounts/profile.html', context)

# ---- Admin Dashboard list ----


@admin_required
def admin_dashboard(request):
    admins = Admin.objects.all()
    members = Member.objects.all()
    return render(request, 'accounts/admin_dashboard.html', {'admins': admins, 'members': members})

# ---- Add Member ----


@admin_required
def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            # Hash password if provided
            raw_pw = form.cleaned_data.get('password')
            if raw_pw:
                from django.contrib.auth.hashers import make_password
                member.password = make_password(raw_pw)
            member.role = 'member'
            member.save()
            messages.success(request, f"Member {member.username} created.")
            return redirect('admin_dashboard')
    else:
        form = MemberForm()
    return render(request, 'accounts/admin_user_form.html', {'form': form, 'title': 'Add Member'})

# ---- Edit Member ----


@admin_required
def edit_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            m = form.save(commit=False)
            raw_pw = form.cleaned_data.get('password')
            if raw_pw:
                from django.contrib.auth.hashers import make_password
                m.password = make_password(raw_pw)
            m.save()
            messages.success(request, f"{m.username} updated.")
            return redirect('admin_dashboard')
    else:
        form = MemberForm(instance=member)
    return render(request, 'accounts/admin_user_form.html', {'form': form, 'title': 'Edit Member'})

# ---- Delete Member ----


@admin_required
@require_POST
def delete_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.delete()
    messages.success(request, "Member deleted.")
    return redirect('admin_dashboard')

# ---- Add/Edit/Delete Admin ----


@admin_required
def add_admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            raw_pw = form.cleaned_data.get('password')
            if raw_pw:
                from django.contrib.auth.hashers import make_password
                admin.password = make_password(raw_pw)
            admin.role = 'admin'
            admin.save()
            messages.success(request, "Admin created.")
            return redirect('admin_dashboard')
    else:
        form = AdminForm()
    return render(request, 'accounts/admin_user_form.html', {'form': form, 'title': 'Add Admin'})


@admin_required
def edit_admin(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    if request.method == 'POST':
        form = AdminForm(request.POST, instance=admin)
        if form.is_valid():
            a = form.save(commit=False)
            raw_pw = form.cleaned_data.get('password')
            if raw_pw:
                from django.contrib.auth.hashers import make_password
                a.password = make_password(raw_pw)
            a.save()
            messages.success(request, "Admin updated.")
            return redirect('admin_dashboard')
    else:
        form = AdminForm(instance=admin)
    return render(request, 'accounts/admin_user_form.html', {'form': form, 'title': 'Edit Admin'})


@admin_required
@require_POST
def delete_admin(request, pk):
    admin = get_object_or_404(Admin, pk=pk)
    admin.delete()
    messages.success(request, "Admin deleted.")
    return redirect('admin_dashboard')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        member = request.user  # This should be your Member instance

        # Update basic fields
        member.first_name = request.POST.get('first_name', '')
        member.last_name = request.POST.get('last_name', '')
        member.email = request.POST.get('email', '')

        # Update fitness fields with validation
        age = request.POST.get('age', '')
        member.age = int(age) if age and age.isdigit() else None

        member.gender = request.POST.get('gender', '')

        height = request.POST.get('height', '')
        member.height = float(height) if height else None

        weight = request.POST.get('weight', '')
        member.weight = float(weight) if weight else None

        member.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return redirect('profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('profile')


@login_required
def deactivate_account(request):
    if request.method == 'POST':
        request.user.is_active = False
        request.user.save()
        messages.info(request, 'Your account has been deactivated.')
        return redirect('logout')
    return redirect('profile')


@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.info(request, 'Your account has been permanently deleted.')
        return redirect('landing')
    return redirect('profile')
