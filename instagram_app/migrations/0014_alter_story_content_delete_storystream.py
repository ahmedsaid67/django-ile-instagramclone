# Generated by Django 4.0.5 on 2022-07-17 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram_app', '0013_remove_story_content_storypost_story_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='content',
            field=models.ManyToManyField(blank=True, null=True, to='instagram_app.storypost'),
        ),
        migrations.DeleteModel(
            name='StoryStream',
        ),
    ]
