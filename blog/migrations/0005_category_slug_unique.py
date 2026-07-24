from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_populate_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
