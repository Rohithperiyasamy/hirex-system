from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('Hr', '0006_interviewschedule_assigned_hr'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewschedule',
            name='iot_violations',
            field=models.TextField(
                blank=True, null=True,
                help_text='JSON list of IoT violation events from Raspberry Pi camera'
            ),
        ),
    ]
