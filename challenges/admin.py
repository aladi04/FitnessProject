from django.contrib import admin
from .models import Challenge, Score, Participant

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_by', 'status', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__username')
    ordering = ('-start_date',)
    readonly_fields = ('created_by',)  # Admin user will be auto-assigned in the view
    list_display_links = ('title',)
    date_hierarchy = 'start_date'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # When creating a new challenge, set created_by to the admin user
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Allow any active staff user to see and perform CRUD for challenges
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'points', 'date_scored')
    list_filter = ('challenge', 'date_scored')
    search_fields = ('user__username', 'challenge__title')
    ordering = ('-date_scored',)
    readonly_fields = ('date_scored',)
    actions = ['delete_selected']
    list_display_links = ('user', 'challenge')

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'joined_at', 'is_active')
    list_filter = ('is_active', 'challenge')
    search_fields = ('user__username', 'challenge__title')
    readonly_fields = ('joined_at',)
    list_display_links = ('user', 'challenge')

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff