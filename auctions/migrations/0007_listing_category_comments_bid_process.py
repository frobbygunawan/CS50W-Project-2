# Generated by Django 4.0.3 on 2022-03-27 11:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_listing_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=500000)),
                ('comment_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_commenting', to=settings.AUTH_USER_MODEL)),
                ('commented_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_commented', to='auctions.listing')),
            ],
        ),
        migrations.CreateModel(
            name='Bid_process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField()),
                ('auctioned_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_status', to='auctions.listing')),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bid_winner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
