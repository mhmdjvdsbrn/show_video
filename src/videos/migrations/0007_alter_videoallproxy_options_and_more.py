# Generated by Django 4.0.4 on 2022-05-24 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0006_video_timestamp_video_update_alter_video_state_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videoallproxy',
            options={'verbose_name': 'All Video', 'verbose_name_plural': 'All Videos'},
        ),
        migrations.AlterModelOptions(
            name='videopublishedproxy',
            options={'verbose_name': 'Published Video', 'verbose_name_plural': 'Published Videos'},
        ),
        migrations.RenameField(
            model_name='video',
            old_name='update',
            new_name='updated',
        ),
    ]
