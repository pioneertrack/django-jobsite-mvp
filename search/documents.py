from django_elasticsearch_dsl import DocType, Index, fields
from website.profile import Profile, Founder, Job
from django.conf import settings
from elasticsearch_dsl import analyzer, tokenizer


if hasattr(settings, 'PRODUCTION') and settings.PRODUCTION:
    people_index_name = 'people'
else:
    people_index_name = 'dev_people'

people = Index(people_index_name)
people.settings(
    number_of_shards=1,
    number_of_replicas=0,
)


@people.doc_type
class PeopleDocument(DocType):
    user = fields.ObjectField(properties={
        'is_active': fields.BooleanField(),
        'is_individual': fields.BooleanField(),
        'is_account_disabled': fields.BooleanField(),
        'first_name': fields.StringField(),
        'last_name': fields.StringField(),
    })
    experience_set = fields.NestedField(properties={
        'company': fields.StringField(),
        'position': fields.StringField(),
        'description': fields.TextField(),
    })
    positions = fields.StringField()

    image = fields.StringField(attr="image_to_string")

    major_display = fields.StringField(attr="get_major_display")

    major = fields.StringField(
        attr="major",
        analyzer=analyzer(
            'standard_major',
            tokenizer="standard",
            filter=["standard"]
        )
    )

    year_display = fields.StringField(attr="get_year_display")

    year = fields.StringField(
        attr="year",
        analyzer=analyzer(
            'standard_year',
            tokenizer="standard",
            filter=["standard"]
        )
    )

    role = fields.StringField(
        attr="role",
        analyzer=analyzer(
            'standard_role',
            tokenizer="standard",
            filter=["standard"]
        )
    )

    class Meta:
        model = Profile
        fields = [
            'id',
            'hours_week',
            'has_startup_exp',
            'has_funding_exp',
            'bio',
            'skills',
            'interests',
            'courses',
        ]