from django_elasticsearch_dsl import DocType, Index, fields
from website.profile import Profile, Founder, Job

people = Index('people')
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

    class Meta:
        model = Profile
        fields = [
            'id',
            'year',
            'major',
            'role',
            'has_startup_exp',
            'has_funding_exp',
            'bio',
            'skills',
            'interests',
            'courses',
        ]