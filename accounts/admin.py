from django.contrib import admin
from .models import ActivityLog, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user_id', 'user', 'user_type', 'phone_number', 'created_at')
    list_filter = ('user_type', 'created_at')
    search_fields = ('user__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

    def get_user_id(self, obj):
        return obj.user.id
    get_user_id.short_description = 'User ID'
    get_user_id.admin_order_field = 'user__id'

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username',)
    readonly_fields = ('timestamp',)
