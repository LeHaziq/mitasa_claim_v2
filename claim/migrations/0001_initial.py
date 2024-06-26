# Generated by Django 5.0.4 on 2024-06-26 17:03

import claim.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_name', models.CharField(max_length=200)),
                ('program_start_date', models.DateTimeField()),
                ('program_end_date', models.DateTimeField()),
                ('program_mode', models.CharField(choices=[('', ''), ('Online', 'Online'), ('Physical', 'Physical')], default='', max_length=10)),
                ('program_location', models.TextField()),
                ('program_letter_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('claim_month', models.IntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], default=0)),
                ('claim_year', models.IntegerField(default=2024)),
                ('work_hours', models.IntegerField(default=0)),
                ('work_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('travel_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('travel_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('accommodation_choice', models.IntegerField(choices=[(0, 'Online'), (1, 'Provided'), (2, 'Not provided')], default=0)),
                ('accommodation_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('accommodation_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('meal_choice', models.IntegerField(choices=[(0, ''), (1, 'Provided'), (2, 'Not provided')], default=0)),
                ('meal_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('meal_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('toll_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('toll_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('parking_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('parking_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('plane_ticket_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('plane_ticket_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('other_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('other_file', models.FileField(blank=True, null=True, upload_to=claim.models.user_directory_path)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('claimer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Claim_Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Approved_Claim',
            fields=[
                ('claim', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='claim.claim')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('receipt', models.FileField(blank=True, null=True, upload_to=claim.models.claim_directory_path)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rejected_Claim',
            fields=[
                ('claim', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='claim.claim')),
                ('reason', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='claim',
            name='claim_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='claim.claim_status'),
        ),
    ]
