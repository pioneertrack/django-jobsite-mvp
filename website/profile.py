from django.db import models
from website import models as user
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django import forms
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.core.files.storage import FileSystemStorage
from custom_storages import MediaStorage
from django.contrib.staticfiles.templatetags.staticfiles import static

HOURS_AVAILABLE = (
    ('0', '1 - 5'),
    ('1', '5 - 10'),
    ('2', '10 - 15'),
    ('3', '15 - 20'),
    ('4', '20+'),
)
POSITION = (
    ('0', 'Partnership'),
    ('1', 'Paid'),
    ('2', 'Unpaid'),
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
    ('GR', 'Master\'s'),
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
    ('5', 'Not Looking'),
)


class FixJustInTime:

    def on_content_required(self, file):
        try:
            file.generate()
        except:
            pass

    def on_existence_required(self, file):
        try:
            file.generate()
        except:
            pass


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
            return val
        if isinstance(self.storage, MediaStorage):
            try:
                if self.storage.exists(val):
                    return val
            except Exception:
                pass
            return self.default
        if isinstance(self.storage, FileSystemStorage):
            last_char = ''
            if self.storage.location[-1] != '/': last_char = '/'
            try:
                if self.storage.exists(self.storage.location + last_char + val):
                    return val
            except Exception:
                pass
            return self.default


def user_directory_path(instance, filename):
    return 'images/user_images/user_{0}/image_{1}.jpg'.format(instance.user.id, instance.user.id)


def company_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/user_images/user_{0}/logo_{1}.jpg'.format(instance.user.id, instance.user.id)


class Profile(models.Model):
    user = models.OneToOneField(user.MyUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFit(100, 100, False)],
                                     format='PNG',
                                     options={'quality': 100})
    image_thumbnail_large = ImageSpecField(source='image',
                                           processors=[ResizeToFit(300, 300, False)],
                                           format='PNG',
                                           options={'quality': 100})
    bio = models.TextField(verbose_name='Bio', max_length=500)
    positions = ChoiceArrayField(models.CharField(choices=POSITIONS, max_length=1, default='0'))
    role = models.CharField(max_length=4, choices=PRIMARY_ROLE)
    skills = models.TextField(verbose_name='Skills', max_length=500)
    year = models.CharField(verbose_name='Cal Affiliation', max_length=4, choices=YEAR_IN_SCHOOL_CHOICES)

    interests = models.TextField(verbose_name='Interests', max_length=500, blank=True, null=False)
    courses = models.TextField(verbose_name='Courses', max_length=400, blank=True, null=False)
    alt_email = models.EmailField(max_length=255, db_index=True, null=True, blank=True)
    hours_week = models.CharField(verbose_name='Hours per Week', max_length=1, choices=HOURS_AVAILABLE, blank=True)
    has_startup_exp = models.BooleanField(verbose_name='Startup Experience', blank=True, default=False)
    has_funding_exp = models.BooleanField(verbose_name='Funding Experience', blank=True, default=False)
    mentor = models.BooleanField(verbose_name='Willing to mentor', default=False)
    linkedin = models.URLField(verbose_name='Linkedin', null=False, blank=True)
    website = models.URLField(verbose_name='Website', null=False, blank=True)
    github = models.URLField(verbose_name='Github', null=False, blank=True)
    major = models.CharField(verbose_name='Major', max_length=5, choices=MAJORS, blank=True)

    is_filled = models.BooleanField(verbose_name='You profile not filled', null=False, default=False)

    def __str__(self):
        return self.user.email

    def get_positions_display(self):
        choices = self._meta.get_field('positions').base_field.choices
        display = []
        for item in self.positions:
            display.append(choices.__getitem__(int(item))[1])
        return display

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if '5' in self.positions:
            self.positions = ['5']
        super(Profile, self).save(force_insert, force_update, using, update_fields)

    def check_is_filled(self, save=True):
        if len(self.bio) > 0 and (len(self.skills) > 0 or self.experience_set.count() > 0) and (
                self.positions != []) and (
                not self.role is '') and (
                not self.year is ''):
            self.is_filled = True
        else:
            self.is_filled = False
        if save:
            self.save()

    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return static('images/default/profile.jpg')

    def image_thumbnail_url(self):
        if self.image_thumbnail and hasattr(self.image_thumbnail, 'url'):
            return self.image_thumbnail.url
        else:
            return static('images/default/profile.jpg')

    def image_thumbnail_large_url(self):
        if self.image_thumbnail_large and hasattr(self.image_thumbnail_large, 'url'):
            # and os.path.isfile(self.image_thumbnail_large.):

            return self.image_thumbnail_large.url
        else:
            return static('images/default/profile.jpg')


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    company = models.CharField(verbose_name='Company', max_length=40, blank=True, null=False)
    position = models.CharField(verbose_name='Position', max_length=50, blank=True, null=False)
    start_date = models.DateField(verbose_name='Start Date', blank=True, null=True)
    description = models.TextField(verbose_name='Description', max_length=500, blank=True, null=False)
    currently_working = models.BooleanField(default=False)
    end_date = models.DateField(verbose_name='End Date', default=timezone.now, null=True, blank=True)


class Founder(models.Model):
    user = models.OneToOneField(user.MyUser, on_delete=models.CASCADE)
    logo = CustomImageField(upload_to=company_logo_path, blank=True, null=True)
    logo_thumbnail = ImageSpecField(source='logo',
                                    processors=[ResizeToFit(100, 100, False)],
                                    format='PNG',
                                    options={'quality': 100},
                                    )
    logo_thumbnail_large = ImageSpecField(source='logo',
                                          processors=[ResizeToFit(300, 300, False)],
                                          format='PNG',
                                          options={'quality': 100},
                                          )
    startup_name = models.CharField(verbose_name='Startup Name', max_length=99)
    stage = models.CharField(verbose_name='Stage', max_length=1, choices=STAGE)
    employee_count = models.IntegerField(verbose_name='Employees')
    description = models.TextField(verbose_name='Description')
    field = models.CharField(verbose_name='Field', max_length=4, choices=CATEGORY)

    alt_email = models.EmailField(max_length=255, db_index=True, null=True, blank=True)
    display_funding = models.BooleanField(blank=True, default=False)
    website = models.URLField(verbose_name='Website', blank=True, null=False)
    facebook = models.URLField(verbose_name='Facebook', blank=True, null=False)
    is_filled = models.BooleanField(verbose_name='You startup profile not filled', null=False, default=False)

    def __str__(self):
        return self.user.email

    def check_is_filled(self, save=True):
        if len(self.description) > 0 and (not self.logo is None) and (len(self.startup_name) > 0) and (
                not self.stage is '') and (not self.employee_count is None) and (len(self.description) > 0) and (
                not self.field is ''):
            self.is_filled = True
        else:
            self.is_filled = False
        if save:
            self.save()

    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        else:
            return static('images/default/logo.jpg')

    def logo_thumbnail_url(self):
        if self.logo_thumbnail and hasattr(self.logo_thumbnail, 'url'):
            return self.logo_thumbnail.url
        else:
            return static('images/default/logo.jpg')

    def logo_thumbnail_large_url(self):
        if self.logo_thumbnail_large and hasattr(self.logo_thumbnail_large, 'url'):
            return self.logo_thumbnail_large.url
        else:
            return static('images/default/logo.jpg')


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
    description = models.TextField(verbose_name='Description', blank=True, null=False)
    level = models.CharField(verbose_name='Level', max_length=2, choices=LEVELS, default="FT")
    created_at = models.DateTimeField(auto_now_add=True)


class Connection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(user.MyUser, verbose_name='Sender', null=True, related_name='sender')
    receiver = models.ForeignKey(user.MyUser, verbose_name='Receiver', null=True, related_name='receiver')
    to_startup = models.BooleanField(verbose_name='Receiver is startup', default=False)
    feedback = models.BooleanField(verbose_name='Feedback', default=False)
    message = models.TextField(verbose_name='Message', null=True)
