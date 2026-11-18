from django.db import migrations


def rename_permissions(apps, old_app, old_model, new_app, new_model):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    old_type = ContentType.objects.filter(app_label=old_app, model=old_model).first()
    new_type = ContentType.objects.filter(app_label=new_app, model=new_model).first()
    if old_type and new_type and old_type.pk != new_type.pk:
        raise RuntimeError('Both old and new Place content types exist.')
    if old_type:
        old_type.app_label = new_app
        old_type.model = new_model
        old_type.save(update_fields=['app_label', 'model'])
        content_type = old_type
    else:
        content_type = new_type
    if content_type:
        for old_code, new_code in (
            ('add_organization', 'add_place'),
            ('change_organization', 'change_place'),
            ('delete_organization', 'delete_place'),
            ('view_organization', 'view_place'),
        ):
            old_permission = Permission.objects.filter(content_type=content_type, codename=old_code).first()
            new_permission = Permission.objects.filter(content_type=content_type, codename=new_code).first()
            if old_permission and new_permission and old_permission.pk != new_permission.pk:
                raise RuntimeError('Both old and new Place permissions exist.')
            if old_permission:
                old_permission.codename = new_code
                old_permission.name = old_permission.name.replace('organization', 'place')
                old_permission.save(update_fields=['codename', 'name'])


def forward(apps, schema_editor):
    rename_permissions(apps, 'organizations', 'organization', 'places', 'place')


def backward(apps, schema_editor):
    rename_permissions(apps, 'places', 'place', 'organizations', 'organization')


class Migration(migrations.Migration):
    dependencies = [
        ('places', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [migrations.RunPython(forward, backward)]
