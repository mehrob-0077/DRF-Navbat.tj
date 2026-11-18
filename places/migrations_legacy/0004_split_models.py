from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0003_queueslot'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='QueueSlot'),
                migrations.DeleteModel(name='Branch'),
            ],
        ),
    ]
