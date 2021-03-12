from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _

from speshalgram.accounts.models import Subscription, User


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        widgets = {
            'description': Textarea()
        }


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = (
        (_('Personal info'), {
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'description',
                'avatar',
                'is_opened',
            )
        }),
        (_('Password'), {
            'classes': ('collapse',),
            'fields': ('password',)
        }),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions',
            ),
        }),
        (_('Important dates'), {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined')
        }),
    )


class SubscriptionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'follower', 'follows_to'
        )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
