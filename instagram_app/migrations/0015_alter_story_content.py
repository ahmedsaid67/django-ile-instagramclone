# Generated by Django 4.0.5 on 2022-07-21 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram_app', '0014_alter_story_content_delete_storystream'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='content',
            field=models.ManyToManyField(blank=True, null=True, related_name='story', to='instagram_app.storypost'),
        ),
    ]