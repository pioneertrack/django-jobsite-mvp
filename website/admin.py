from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from website.models import MyUser
from website.forms import NewRegistrationForm
from website.profile import Profile, Experience
from website.profile import Founder, Funding, Job
from website.profile import Connection

from website.profile import STAGE, LEVELS, CATEGORY, PRIMARY_ROLE, MAJORS, YEAR_IN_SCHOOL_CHOICES, FUNDING_ROUNDS, POSITION, HOURS_AVAILABLE


# Classes for My Users (All users)
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
    list_display = ('email', 'first_name', 'last_name', 'is_individual', 'is_founder', 'is_active', 'is_admin',
                    'is_account_disabled', 'get_year', 'registered_at', 'last_login')
    list_filter = ('is_admin','is_active', 'is_founder', 'registered_at')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'is_individual', 'is_founder')}),
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


# Classes for Founders
class FundingInline(admin.TabularInline):
    model = Funding
    extra = 1


class FounderResource(resources.ModelResource):
    seed     = fields.Field(widget=widgets.ForeignKeyWidget(Funding), column_name='Seed')
    series_a = fields.Field(widget=widgets.ForeignKeyWidget(Funding), column_name='Series A')
    series_b = fields.Field(widget=widgets.ForeignKeyWidget(Funding), column_name='Series B')
    series_c = fields.Field(widget=widgets.ForeignKeyWidget(Funding), column_name='Series C')
    class Meta:
        model = Founder

        fields = ('user', 'seed', 'series_a', 'series_b', 'series_c', 'field',
                 'user__first_name', 'user__last_name', 'startup_name', 'facebook',
                 'description', 'stage', 'employee_count', 'website')

        export_order = ('user', 'user__first_name', 'user__last_name',
                        'startup_name', 'stage', 'field', 'description', 'employee_count',
                        'website', 'facebook', 'seed', 'series_a', 'series_b', 'series_c')

    def dehydrate_user(self, founder):
        return founder.user

    def dehydrate_seed(self, obj):
        fundings = Funding.objects.filter(founder=obj.id)
        for f in fundings:
            if int(f.stage) == 0:
                return f.raised
        return 0
    def dehydrate_series_a(self, obj):
        fundings = Funding.objects.filter(founder=obj.id)
        for f in fundings:
            if int(f.stage) == 1:
                return f.raised
        return 0
    def dehydrate_series_b(self, obj):
        fundings = Funding.objects.filter(founder=obj.id)
        for f in fundings:
            if int(f.stage) == 2:
                return f.raised
        return 0
    def dehydrate_series_c(self, obj):
        fundings = Funding.objects.filter(founder=obj.id)
        for f in fundings:
            if int(f.stage) == 3:
                return f.raised
        return 0

    def dehydrate_stage(self, founder):
        return STAGE[int(founder.stage)][1]

    def dehydrate_field(self, founder):
        cat_dict = dict(CATEGORY)
        return cat_dict.get(founder.field,'')

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
    list_display = ('user','startup_name','stage','field','employee_count', 'is_filled')
    list_filter = ('stage','field','is_filled')
    fieldsets = (
        (None,         {'fields': ['user','startup_name','logo','display_funding']}),
        ('Basic Info', {'fields': ['description','stage','employee_count','field']}),
        ('Contact',    {'fields': ['website','facebook']})
    )
    inlines = (FundingInline,)

    ordering = ('user', 'is_filled')

    resource_class = FounderResource
    pass


# Classes for positions
class JobResource(resources.ModelResource):
    class Meta:
        model = Job

        fields = ('founder', 'founder__startup_name', 'title', 'pay', 'description', 'level')

        export_order = ('founder__startup_name','title','pay','level','description')

    def dehydrate_founder(self, position):
        return position.founder.user

    def dehydrate_pay(self, position):
        return POSITION[int(position.pay)][1]

    def dehydrate_level(self, position):
        lev_dict = dict(LEVELS)
        return lev_dict.get(position.level,'')

    def get_export_headers(self):
        headers = []
        model_fields = self.Meta.model._meta.get_fields()
        for field in self.get_fields():
            header = ''
            if field.column_name == 'founder__startup_name':
                header = 'Startup Name'
            elif field.column_name == 'founder':
                header = 'Founder'
            else:
                header = next((x.verbose_name for x in model_fields if x.name == field.column_name), field.column_name)
            headers.append(header)
        return headers


class JobAdmin(ImportExportModelAdmin):
    list_display = ('founder','title','pay','level')
    list_filter = ('pay','level')

    ordering = ('founder',)

    resource_class = JobResource
    pass


# Classes for Connection emails
class ConnectionResource(resources.ModelResource):
    class Meta:
        model = Connection
        fields = ('created_at', 'receiver', 'sender', 'to_startup', 'message')
        export_order = ('receiver', 'sender')


class ConnectionAdmin(ImportExportModelAdmin):
    resource_class = ConnectionResource
    list_display = ('created_at', 'receiver', 'sender', 'to_startup')
    readonly_fields = ('created_at', 'receiver', 'sender', 'to_startup', 'message')
    ordering = ('created_at', 'sender', 'receiver')


# Classes for Users
class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 1


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile

        fields = ('user', 'user__first_name', 'user__last_name', 'bio',
                  'interests', 'skills', 'courses', 'year', 'hours_week',
                  'has_startup_exp', 'has_funding_exp', 'linkedin', 'website',
                  'github', 'major', 'role')

        export_order = ('user', 'user__first_name', 'user__last_name')

    def dehydrate_position(self, profile):
        if profile.position:
            return POSITION[int(profile.position)][1]
        return ''

    def dehydrate_hours_week(self, profile):
        return HOURS_AVAILABLE[int(profile.hours_week)][1]

    def dehydrate_year(self, profile):
        year_dict = dict(YEAR_IN_SCHOOL_CHOICES)
        return year_dict.get(profile.year,'')

    def dehydrate_major(self, profile):
        major_dict = dict(MAJORS)
        return major_dict.get(profile.major,'')

    def dehydrate_role(self, profile):
        role_dict = dict(PRIMARY_ROLE)
        return role_dict.get(profile.role,'')

    def dehydrate_has_startup_exp(self, profile):
        if profile.has_startup_exp:
            return 'yes'
        return 'no'

    def dehydrate_has_funding_exp(self, profile):
        if profile.has_funding_exp:
            return 'yes'
        return 'no'

    def dehydrate_user(self, profile):
        return profile.user.email

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
    list_display = ('user', 'major', 'year', 'hours_week', 'has_startup_exp', 'has_funding_exp', 'is_filled')
    list_filter = ('major','year','has_startup_exp','has_funding_exp', 'is_filled')
    fieldsets = (
        (None,         {'fields': ['user','bio','interests']}),
        ('School',     {'fields': ['year', 'role', 'major', 'courses']}),
        ('Work',       {'fields': ['hours_week', 'positions']}),
        ('Experience', {'fields': ['has_startup_exp','has_funding_exp','skills']}),
        ('Contact',    {'fields': ['linkedin','website','github']})
    )
    inlines = (ExperienceInline,)

    ordering = ('user', 'is_filled')

    resource_class = ProfileResource
    pass

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Founder, FounderAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Connection, ConnectionAdmin)
admin.site.unregister(Group)
