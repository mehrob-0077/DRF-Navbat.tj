from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def move_queue_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='organizations', model='queueslot').update(app_label='queues')


def restore_queue_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='queues', model='queueslot').update(app_label='organizations')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('branches', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='QueueSlot',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('appointment_date', models.DateField()),
                        ('appointment_time', models.TimeField()),
                        ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                        ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='branches.branch')),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                    ],
                    options={'db_table': 'organizations_queueslot'},
                ),
            ],
        ),
        migrations.RunPython(move_queue_content_type, restore_queue_content_type),
    ]
