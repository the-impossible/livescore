# Generated by Django 4.2.1 on 2023-06-04 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
        ('scores_fixtures', '0011_goalscorers_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalscorers',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.team'),
        ),
    ]
