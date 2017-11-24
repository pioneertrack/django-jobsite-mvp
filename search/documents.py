from django_elasticsearch_dsl import DocType, Index, fields
from website.profile import Profile, Founder, Job, Experience
from website.models import MyUser
from django.conf import settings
from elasticsearch_dsl import analyzer, tokenizer

# Profile search document
people_index_name = 'people'
if hasattr(settings, 'ELASTIC_PREFIX') and settings.ELASTIC_PREFIX:
    people_index_name = settings.ELASTIC_PREFIX + '_' + people_index_name

# Startup search document
startup_index_name = 'startup'
if hasattr(settings, 'ELASTIC_PREFIX') and settings.ELASTIC_PREFIX:
    startup_index_name = settings.ELASTIC_PREFIX + '_' + startup_index_name

# Job search document
job_index_name = 'job'
if hasattr(settings, 'ELASTIC_PREFIX') and settings.ELASTIC_PREFIX:
    job_index_name = settings.ELASTIC_PREFIX + '_' + job_index_name

people = Index(people_index_name)
people.settings(
    number_of_shards=1,
    number_of_replicas=0,
)

startup = Index(startup_index_name)
startup.settings(
    number_of_shards=1,
    number_of_replicas=0,
)

job = Index(job_index_name)
job.settings(
    number_of_shards=1,
    number_of_replicas=0,
)

leave_default = analyzer(
        'leave_default',
        tokenizer="standard",
        filter=["standard"]
)

@people.doc_type
class PeopleDocument(DocType):
    user = fields.ObjectField(properties={
        'is_active': fields.BooleanField(),
        'is_individual': fields.BooleanField(),
        'is_account_disabled': fields.BooleanField(),
        'first_name': fields.StringField(),
        'last_name': fields.StringField(),
        'last_activity': fields.DateField(attr='last_activity.date')
    })
    experience_set = fields.NestedField(properties={
        'company': fields.StringField(),
        'position': fields.StringField(),
        'description': fields.TextField(),
    })
    positions = fields.StringField()
    image = fields.StringField(attr='image_url')
    # image_thumbnail = fields.StringField(attr='image_thumbnail_url')
    get_positions_display = fields.StringField(attr='get_positions_display')
    get_major_display = fields.StringField(attr='get_major_display')
    get_year_display = fields.StringField(attr='get_year_display')
    get_role_display = fields.StringField(attr='get_role_display')
    get_hours_week_display = fields.StringField(attr='get_hours_week_display')

    major = fields.StringField(attr='major', analyzer=leave_default)
    year = fields.StringField(attr='year', analyzer=leave_default)
    role = fields.StringField(attr='role', analyzer=leave_default)

    class Meta:
        model = Profile
        ignore_signals = False
        related_models = [MyUser, Experience]
        fields = [
            'is_filled',
            'hours_week',
            'has_startup_exp',
            'has_funding_exp',
            'bio',
            'skills',
            'interests',
            'courses',
            'mentor'
        ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, MyUser):
            if hasattr(related_instance, 'profile'):
                return related_instance.profile
        if isinstance(related_instance, Experience):
            return related_instance.profile


@startup.doc_type
class StartupDocument(DocType):
    user = fields.ObjectField(properties={
        'is_active': fields.BooleanField(),
        'is_founder': fields.BooleanField(),
        'is_account_disabled': fields.BooleanField(),
        'first_name': fields.StringField(),
        'last_name': fields.StringField(),
        'last_activity': fields.DateField(attr='last_activity.date')
    })
    job_set = fields.NestedField(properties={
        'title': fields.StringField(),
        'description': fields.StringField(),
        'level': fields.StringField(attr='get_level_display'),
        'pay': fields.StringField(attr='get_pay_display')
    })
    logo = fields.StringField(attr='logo_url')
    # logo_thumbnail = fields.StringField(attr='logo_thumbnail_url')
    get_stage_display = fields.StringField(attr='get_stage_display')
    get_field_display = fields.StringField(attr='get_field_display')
    stage = fields.StringField(attr='stage', analyzer=leave_default)
    field = fields.StringField(attr='field', analyzer=leave_default)

    class Meta:
        model = Founder
        related_models = [MyUser, Job]
        fields = [
            'startup_name',
            'description',
            'is_filled',
            'employee_count'
        ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, MyUser):
            if hasattr(related_instance, 'founder'):
                return related_instance.founder
        if isinstance(related_instance, Job):
            return related_instance.founder


@job.doc_type
class JobDocument(DocType):
    founder = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'startup_name': fields.StringField(),
        'description': fields.StringField(),
        'logo': fields.StringField(attr='logo_url'),
        # 'logo_thumbnail': fields.StringField(attr='logo_thumbnail_url'),
        'is_filled': fields.BooleanField(),
        'field': fields.StringField(attr='field', analyzer=leave_default),
        'user': fields.ObjectField(properties={
            'is_active': fields.BooleanField(),
            'is_account_disabled': fields.BooleanField(),
            'last_activity': fields.DateField(attr='last_activity.date')
        })
    })
    get_pay_display = fields.StringField(attr='get_pay_display')
    get_level_display = fields.StringField(attr='get_level_display')

    pay = fields.StringField(attr='pay', analyzer=leave_default)
    level = fields.StringField(attr='level', analyzer=leave_default)

    class Meta:
        model = Job
        related_models = [Founder, MyUser]
        fields = [
            'title',
            'description'
        ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, MyUser):
            if hasattr(related_instance, 'founder'):
                return related_instance.founder.job_set.all()
        if isinstance(related_instance, Founder):
            return related_instance.job_set.all()
