from django.db import migrations


def create_branch_table(apps, schema_editor):
    Branch = apps.get_model('branches', 'Branch')
    if Branch._meta.db_table not in schema_editor.connection.introspection.table_names():
        schema_editor.create_model(Branch)


class Migration(migrations.Migration):
    dependencies = [
        ('branches', '0001_initial'),
        ('places', '0002_rename_place_permissions'),
    ]

    operations = [
        migrations.RunPython(create_branch_table, migrations.RunPython.noop),
    ]
