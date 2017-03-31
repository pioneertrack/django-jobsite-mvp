# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-26 09:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import website.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(help_text='Must be a @berkeley.edu email', max_length=255, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=25)),
                ('last_name', models.CharField(max_length=40)),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('first_login', models.BooleanField(default=True)),
                ('is_founder', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', website.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Founder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, default='images/default/default-logo.jpg', upload_to='images/startups/')),
                ('startup_name', models.CharField(max_length=99)),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('hours_wanted', models.CharField(blank=True, choices=[('0', '0 - 5'), ('1', '5 - 10'), ('2', '10 - 15'), ('3', '15 - 20'), ('4', '20+')], max_length=1)),
                ('seeking', models.CharField(blank=True, choices=[('0', 'Partnership'), ('1', 'Paid')], max_length=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('image', models.ImageField(blank=True, default='images/default/default-profile.jpg', upload_to='images/False/profile_picture/')),
                ('position', models.CharField(blank=True, choices=[('0', 'Partnership'), ('1', 'Paid')], max_length=1)),
                ('interests', models.TextField(blank=True)),
                ('skills', models.TextField(blank=True)),
                ('year', models.CharField(blank=True, choices=[('FR', 'Freshman'), ('SO', 'Sophomore'), ('JR', 'Junior'), ('SR', 'Senior'), ('GR', 'Graduate')], max_length=2)),
                ('hours_week', models.CharField(blank=True, choices=[('0', '0 - 5'), ('1', '5 - 10'), ('2', '10 - 15'), ('3', '15 - 20'), ('4', '20+')], max_length=1)),
                ('has_startup_exp', models.BooleanField(default=False)),
                ('has_funding_exp', models.BooleanField(default=False)),
                ('linkedin', models.URLField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('role', models.CharField(blank=True, choices=[('MARK', 'Marketing'), ('BIZ', 'Business/Administration'), ('PM', 'Product Manager'), ('CS', 'Software engineer'), ('HARD', 'Hardware engineer'), ('IOS', 'Mobile developer'), ('CONS', 'Consultant'), ('HR', 'Human resources')], max_length=4)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
