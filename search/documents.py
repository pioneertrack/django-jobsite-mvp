from django_elasticsearch_dsl import DocType, Index, fields
from website.models import MyUser
from website.profile import Profile, Founder, Job

people = Index('people')
people.settings(
    number_of_shards=1,
    number_of_replicas=0,
)


@people.doc_type
class PeopleDocument(DocType):
    user = fields.ObjectField(properties={
        'first_name': fields.StringField(),
        'last_name': fields.StringField(),
    })
    experience = fields.NestedField(properties={
        'company': fields.StringField(),
        'position': fields.StringField(),
        'description': fields.TextField(),
    })

    class Meta:
        model = Profile
        fields = [
            'majors',
            'bio',
            'skills',
            'interests',
            'courses',
        ]