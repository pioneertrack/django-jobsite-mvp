from django.db import models
from website import models as user
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django import forms
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.core.files.storage import FileSystemStorage
from custom_storages import MediaStorage

HOURS_AVAILABLE = (
    ('0', '0 - 5'),
    ('1', '5 - 10'),
    ('2', '10 - 15'),
    ('3', '15 - 20'),
    ('4', '20+'),
)
POSITION = (
    ('0', 'Partnership'),
    ('1', 'Paid'),
    ('NONE', 'Other',)
)
STAGE = (
    ('0', 'Idea'),
    ('1', 'Prototype'),
    ('2', 'Incorporated'),
    ('3', 'Generating Revenue'),
    ('4', 'Seed'),
    ('5', 'Series A'),
    ('6', 'Series B'),
    ('7', 'Series C'),
)
FUNDING_ROUNDS = (
    ('0', 'Seed'),
    ('1', 'Series A'),
    ('2', 'Series B'),
    ('3', 'Series C'),
)
YEAR_IN_SCHOOL_CHOICES = (
    ('FR', 'Freshman'),
    ('SO', 'Sophomore'),
    ('JR', 'Junior'),
    ('SR', 'Senior'),
    ('GR', 'Graduate'),
    ('PH', 'PhD'),
    ('PD', 'Post-Doc'),
    ('AL', 'Alumni'),
    ('FC', 'Faculty'),
    ('NONE', 'Other')
)
MAJORS = (
    ('EECS', 'Electrical Engineering and Computer Science'),
    ('IEOR', 'Industrial Engineering and Operations Research'),
    ('ECON', 'Economics'),
    ('AMATH', 'Applied Math'),
    ('CHEM', 'Chemistry'),
    ('PHYS', 'Physics'),
    ('MECH', 'Mechanical Engineering'),
    ('BIOE', 'Bioengineering'),
    ('CS', 'Computer Science'),
    ('STAT', 'Statistics'),
    ('HAAS', 'Business'),
    ('PH', 'Public Health'),
    ('MCB', 'MCB'),
    ('BIO', 'Biology'),
    ('UND', 'Undecided'),
    ('NONE', 'Other')
)
PRIMARY_ROLE = (
    ('MARK', 'Marketing'),
    ('BIZ', 'Business/Administration'),
    ('SALE', 'Sales'),
    ('DES', 'Design'),
    ('PM', 'Product Manager'),
    ('CS', 'Software engineer'),
    ('HARD', 'Hardware engineer'),
    ('IOS', 'Mobile developer'),
    ('CONS', 'Consulting'),
    ('HR', 'Human resources'),
    ('NONE', 'Other')
)
CATEGORY = (
    ('EDUC', 'Education'),
    ('TECH', 'Technology'),
    ('RE', 'Retail'),
    ('HEAL', 'Health Care'),
    ('ECOM', 'E-Commerce'),
    ('MARK', 'Marketplaces'),
    ('FIN', 'Finance'),
    ('HARD', 'Hardware'),
    ('MANG', 'Management/Consulting'),
    ('LEG', 'Legal'),
    ('MED', 'Medical'),
    ('HOUS', 'Real Estate'),
    ('AUTO', 'Automotive'),
    ('ENER', 'Energy'),
    ('MACH', 'Machinery'),
    ('ENV', 'Environmental'),
    ('NONE', 'Other')
)
LEVELS = (
    ('FT', 'Full-time'),
    ('PT', 'Part-time'),
    ('IN', 'Intern'),
    ('CT', 'Contract')
)
POSITIONS = (
    ('0', 'Partnership'),
    ('1', 'Intern'),
    ('2', 'Part-Time'),
    ('3', 'Full-Time'),
    ('4', 'Contract'),
)


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.

    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.
    """

    def formfield(self, **kwargs):
        defaults = {
            'widget': forms.CheckboxSelectMultiple,
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)


class CustomImageField(models.ImageField):
    def from_db_value(self, value, expression, connection, context):
        val = self.to_python(value)
        if val == self.default:
            return val;
        if isinstance(self.storage, MediaStorage):
            if self.storage.exists(val):
                return val;
            return self.default
        if isinstance(self.storage, FileSystemStorage):
            last_char = '';
            if self.storage.location[-1] != '/': last_char = '/'
            if self.storage.exists(self.storage.location + last_char + val):
                return val;
            return self.storage.location + last_char + self.default


def user_directory_path(instance, filename):
    return 'images/user_{0}/{1}.jpg'.format(instance.id, instance.id)


def company_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/company_logos/user_{0}/{1}.jpg'.format(instance.id, instance.id)


class Profile(models.Model):
    role = models.CharField(max_length = 4, choices = PRIMARY_ROLE, default='NONE', blank = True, null = False)
    user = models.OneToOneField(user.MyUser, on_delete=models.CASCADE)
    bio = models.TextField(verbose_name='Bio', max_length=500, blank=True, null=False)
    image = CustomImageField(upload_to=user_directory_path, default='images/default/default-profile.jpg', blank=True,
                              null=False)
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFit(100, 100, False)],
                                      format='PNG',
                                      options={'quality': 100})
    image_thumbnail_large = ImageSpecField(source='image',
                                      processors=[ResizeToFit(300, 300, False)],
                                      format='PNG',
                                      options={'quality': 100})
    interests = models.TextField(verbose_name='Interests', max_length=500, blank=True, null=False)
    skills = models.TextField(verbose_name='Skills', max_length=500, blank=True, null=False)
    courses = models.TextField(verbose_name='Courses', max_length=400, blank=True, null=False)
    alt_email = models.EmailField(max_length=255, db_index=True, null=True, blank=True)
    year = models.CharField(verbose_name='Year', max_length=4, choices=YEAR_IN_SCHOOL_CHOICES, default='NONE',
                            blank=True, null=False)
    hours_week = models.CharField(verbose_name='Hours per Week', max_length=1, choices=HOURS_AVAILABLE, default='0')
    has_startup_exp = models.BooleanField(verbose_name='Startup Experience', blank=True, default=False)
    has_funding_exp = models.BooleanField(verbose_name='Funding Experience', blank=True, default=False)
    linkedin = models.URLField(verbose_name='Linkedin', null=False, blank=True)
    website = models.URLField(verbose_name='Website', null=False, blank=True)
    github = models.URLField(verbose_name='Github', null=False, blank=True)
    major = models.CharField(verbose_name='Major', max_length=5, choices=MAJORS, default='UND')
    role = models.CharField(max_length=4, choices=PRIMARY_ROLE, default='NONE', blank=True, null=False)
    positions = ChoiceArrayField(models.CharField(choices=POSITIONS, max_length=1, default='0'), default=['0'])

    def __getattr__(self, item):
        if item != 'image':
            return super(Profile, self).__getattr__(item)
        if item == 'image':
            if item == 'image':
                image = super(Profile, self).__getattr__(item)
                return image

    def __str__(self):
        return self.user.email


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    company = models.CharField(verbose_name='Company', max_length=40, blank=True, null=False)
    position = models.CharField(verbose_name='Position', max_length=50, blank=True, null=False)
    start_date = models.DateField(verbose_name='Start Date', blank=True, null=True)
    description = models.TextField(verbose_name='Description', max_length=500, blank=True, null=False)
    currently_working = models.BooleanField(default=False)
    end_date = models.DateField(verbose_name='End Date', default=timezone.now, null=True)


class Founder(models.Model):
    user = models.OneToOneField(user.MyUser, on_delete=models.CASCADE)
    logo = CustomImageField(upload_to=company_logo_path, default='images/default/default-logo.jpg', blank=True,
                             null=False)
    logo_thumbnail = ImageSpecField(source='logo',
                                      processors=[ResizeToFit(100, 100, False)],
                                      format='PNG',
                                      options={'quality': 100})
    logo_thumbnail_large = ImageSpecField(source='logo',
                                      processors=[ResizeToFit(300, 300, False)],
                                      format='PNG',
                                      options={'quality': 100})
    startup_name = models.CharField(verbose_name='Startup Name', max_length=99)
    description = models.TextField(verbose_name='Description', blank=True, null=False)
    alt_email = models.EmailField(max_length=255, db_index=True, null=True, blank=True)
    stage = models.CharField(verbose_name='Stage', max_length=1, choices=STAGE, default='0')
    employee_count = models.IntegerField(verbose_name='Employees', default=1)
    display_funding = models.BooleanField(blank=True, default=False)
    website = models.URLField(verbose_name='Website', blank=True, null=False)
    facebook = models.URLField(verbose_name='Facebook', blank=True, null=False)
    field = models.CharField(verbose_name='Field', max_length=4, choices=CATEGORY, blank=True, null=False)

    def __str__(self):
        return self.user.email



class Funding(models.Model):
    founder = models.ForeignKey(Founder, on_delete=models.CASCADE, null=True)
    stage = models.CharField(verbose_name='Stage', max_length=1, choices=FUNDING_ROUNDS, default='0', null=True)
    raised = models.IntegerField(verbose_name='Raised', default=0)

    def __str__(self):
        return self.founder.user.email


class Job(models.Model):
    founder = models.ForeignKey(Founder, on_delete=models.CASCADE, null=True)
    title = models.CharField(verbose_name='Job Title', max_length=40, blank=True, null=False)
    pay = models.CharField(verbose_name='Pay', max_length=5, choices=POSITION, default='1')
    description = models.TextField(verbose_name='Description', max_length=500, blank=True, null=False)
    level = models.CharField(verbose_name='Level', max_length=2, choices=LEVELS, default="FT")
    created_date = models.DateTimeField(default=timezone.now)


@receiver(post_save, sender=user.MyUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_individual:
        Profile.objects.create(user=instance)
    if created and instance.is_founder:
        Founder.objects.create(user=instance)
