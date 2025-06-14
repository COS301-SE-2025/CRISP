# Generated by Django 4.2.21 on 2025-05-27 10:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0002_crispuser_failed_login_attempts_crispuser_is_locked_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('trust_level', models.PositiveSmallIntegerField(default=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ThreatFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('feed_type', models.CharField(choices=[('stix_taxii', 'STIX/TAXII'), ('misp', 'MISP'), ('custom', 'Custom'), ('internal', 'Internal')], max_length=20)),
                ('url', models.URLField(blank=True)),
                ('api_key', models.CharField(blank=True, max_length=512)),
                ('is_active', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='crispuser',
            options={'verbose_name': 'CRISP User', 'verbose_name_plural': 'CRISP Users'},
        ),
        migrations.CreateModel(
            name='IndicatorOfCompromise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('ip', 'IP Address'), ('domain', 'Domain'), ('url', 'URL'), ('hash', 'File Hash'), ('email', 'Email'), ('other', 'Other')], max_length=10)),
                ('value', models.CharField(max_length=512)),
                ('description', models.TextField(blank=True)),
                ('severity', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('review', 'Under Review')], default='active', max_length=10)),
                ('source', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_iocs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Indicator of Compromise',
                'verbose_name_plural': 'Indicators of Compromise',
                'indexes': [models.Index(fields=['type'], name='auth_api_in_type_7a6c07_idx'), models.Index(fields=['value'], name='auth_api_in_value_f54d52_idx'), models.Index(fields=['severity'], name='auth_api_in_severit_5e075b_idx'), models.Index(fields=['status'], name='auth_api_in_status_b8983d_idx')],
                'unique_together': {('type', 'value')},
            },
        ),
    ]
