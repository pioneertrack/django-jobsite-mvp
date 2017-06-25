from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from website.models import MyUser
from website.forms import NewRegistrationForm
from website.profile import Profile
from website.profile import Founder

from website.profile import STAGE, LEVELS, CATEGORY, PRIMARY_ROLE, MAJORS, YEAR_IN_SCHOOL_CHOICES, FUNDING_ROUNDS, POSITION, HOURS_AVAILABLE
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
        ('Permissions', {'fields': ('is_admin', 'is_active', 'is_founder')}),
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

class FounderResource(resources.ModelResource):
    class Meta:
        model = Founder

        fields = ('user__first_name', 'user__last_name', 'startup_name',
                 'description', 'stage', 'employee_count',
                 'website', 'facebook', 'field')

        export_order = ('user__first_name', 'user__last_name', 'startup_name')

    def dehydrate_stage(self, founder):
        return STAGE[int(founder.stage)][1]

    def dehydrate_field(self, founder):
        return CATEGORY[int(founder.field)][1]

    def get_export_headers(self):
        headers = []
        model_fields = self.Meta.model._meta.get_fields() + ProfileInline.model._meta.get_fields()
        for field in self.get_fields():
            header = ''
            if field.column_name == 'user__last_name':
                header = 'Last Name'
            elif field.column_name == 'user__first_name':
                header = 'First Name'
            else:
                header = next((x.verbose_name for x in model_fields if x.name == field.column_name), field.column_name)
            headers.append(header)
        return headers

class FounderAdmin(ImportExportModelAdmin):
    resource_class = FounderResource
    pass

class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile

        fields = ('user__first_name', 'user__last_name', 'bio', 'position',
                  'interests', 'skills', 'courses', 'year', 'hours_week',
                  'has_startup_exp', 'has_funding_exp', 'linkedin', 'website',
                  'github', 'major', 'role')

        export_order = ('user__first_name', 'user__last_name')

    def dehydrate_position(self, profile):
        return POSITION[int(profile.position)][1]

    def dehydrate_hours_week(self, profile):
        return HOURS_AVAILABLE[int(profile.hours_week)][1]

    def dehydrate_year(self, profile):
        return YEAR_IN_SCHOOL_CHOICES[int(profile.year)][1]

    def dehydrate_major(self, profile):
        return MAJORS[int(profile.major)][1]

    def dehydrate_role(self, profile):
        return PRIMARY_ROLE[int(profile.role)]

    def get_export_headers(self):
        headers = []
        model_fields = self.Meta.model._meta.get_fields() + ProfileInline.model._meta.get_fields()
        for field in self.get_fields():
            header = ''
            if field.column_name == 'user__last_name':
                header = 'Last Name'
            elif field.column_name == 'user__first_name':
                header = 'First Name'
            else:
                header = next((x.verbose_name for x in model_fields if x.name == field.column_name), field.column_name)
            headers.append(header)
        return headers

class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    pass

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Founder, FounderAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(Group)
