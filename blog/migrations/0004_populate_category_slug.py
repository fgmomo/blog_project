from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')

    for category in Category.objects.all():
        base_slug = slugify(category.name)
        slug = base_slug
        i = 1

        while Category.objects.filter(slug=slug).exclude(pk=category.pk).exists():
            i += 1
            slug = f"{base_slug}-{i}"

        category.slug = slug
        category.save(update_fields=['slug'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_category_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, noop),
    ]
