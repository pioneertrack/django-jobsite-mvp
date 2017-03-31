from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from website.models import MyUser
from website.forms import NewRegistrationForm
from website.profile import Profile
from website.profile import Founder
# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class FounderInline(admin.StackedInline):
    model = Founder
    can_delete = False
    verbose_name_plural = 'Founder'
    fk_name = 'user'

class MyUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # add_form = NewRegistrationForm
    inlines = (ProfileInline, FounderInline)
    list_select_related = ('profile', )
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_founder', 'is_active', 'is_admin', 'get_year')
    list_filter = ('is_admin','is_active', 'is_founder',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'is_founder', 'password1', 'password2', 'is_admin', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(MyUserAdmin, self).get_inline_instances(request, obj)

    def get_year(self, instance):
        return instance.profile.year
    get_year.short_description = 'Year'

admin.site.register(MyUser, MyUserAdmin)
admin.site.unregister(Group)
