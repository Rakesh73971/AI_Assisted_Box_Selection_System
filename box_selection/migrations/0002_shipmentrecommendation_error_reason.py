# Generated manually for error_reason field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("box_selection", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shipmentrecommendation",
            name="error_reason",
            field=models.TextField(blank=True, default=""),
        ),
    ]
