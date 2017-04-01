import uuid as uuid4
from django.db import models
from website import models as user
from django.db.models.signals import post_save
from django.dispatch import receiver
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
)
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/user_{0}/{1}.jpg'.format(instance.id, instance.id)
def company_logo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/company_logos/user_{0}/{1}.jpg'.format(instance.id, instance.id)
class Profile(models.Model):
    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
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
    user = models.OneToOneField(user.MyUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=False)
    image = models.ImageField(upload_to=user_directory_path, default = 'images/default/default-profile.jpg', blank=True, null=False)
    position = models.CharField(max_length = 1, choices = POSITION, blank = True, null = False)
    interests = models.TextField(max_length=500, blank = True, null = False)
    skills = models.TextField(max_length=500, blank = True, null = False)
    courses = models.TextField(max_length=400, blank = True, null = False)
    # experience = []
    year = models.CharField(max_length = 2, choices = YEAR_IN_SCHOOL_CHOICES, blank = True, null = False)
    hours_week = models.CharField(max_length = 1, choices= HOURS_AVAILABLE, default='0')
    has_startup_exp = models.BooleanField(blank = True, default = False)
    has_funding_exp = models.BooleanField(blank = True, default = False)
    linkedin = models.URLField(null = False, blank = True)
    website = models.URLField(null = False, blank = True)
    github = models.URLField(null = False, blank = True)
    major = models.CharField(max_length = 4, choices=MAJORS, default = 'UND')
    # second_major = models.CharField()

    role = models.CharField(max_length = 4, choices = PRIMARY_ROLE, blank = True, null = False)
class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    company = models.CharField(max_length=40, blank=True, null = False)
    position = models.CharField(max_length=50, blank=True, null = False)
    start_date = models.DateField(blank=True, null = True)
    end_date = models.DateField(blank=True, null = True)
    description = models.TextField(max_length=500, blank=True,null=False)

class Founder(models.Model):
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
    user = models.OneToOneField(user.MyUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=company_logo_path, default = 'images/default/default-logo.jpg', blank=True, null=False)
    startup_name = models.CharField(max_length = 99)
    description = models.TextField(blank = True, null = False)
    website = models.URLField(blank = True, null = False)
    seeking = models.CharField(max_length = 1, choices = POSITION, blank = True, null = False)
    field = models.CharField(max_length = 4, choices = CATEGORY, blank = True, null = False)
class Job(models.Model):
    LEVELS = (
        ('FT', 'Full-time'),
        ('PT', 'Part-time'),
        ('IN', 'Intern')
    )
    founder = models.ForeignKey(Founder, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=40, blank=True, null=False)
    pay = models.CharField(max_length=40, blank=True, null=False)
    description = models.TextField(max_length=500, blank = True, null = False)
    level = models.CharField(max_length = 2, choices = LEVELS, default="FT")
@receiver(post_save, sender=user.MyUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_founder:
        Profile.objects.create(user=instance)
    elif created and instance.is_founder:
        Founder.objects.create(user=instance)

@receiver(post_save, sender=user.MyUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_founder:
        instance.founder.save()
    else:
        instance.profile.save()
