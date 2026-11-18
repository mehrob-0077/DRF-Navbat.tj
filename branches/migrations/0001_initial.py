from django.db import migrations, models
import django.db.models.deletion


def move_branch_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='organizations', model='branch').update(app_label='branches')


def restore_branch_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='branches', model='branch').update(app_label='organizations')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('places', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Branch',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=150)),
                        ('address', models.CharField(max_length=255)),
                        ('schedule', models.JSONField(default=dict)),
                        ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='places.place')),
                    ],
                        options={'db_table': 'organizations_branch'},
                ),
            ],
        ),
        migrations.RunPython(move_branch_content_type, restore_branch_content_type),
    ]
