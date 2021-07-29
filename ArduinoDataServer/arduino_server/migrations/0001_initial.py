# Generated by Django 3.2.5 on 2021-07-27 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IntervalType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.IntegerField(choices=[(0, 'hourly'), (1, 'daily'), (2, 'weekly'), (3, 'monthly'), (4, 'annual')], help_text='This is the period or interval in which the summary should automatically summarise every new data entry.')),
                ('verbose_name', models.CharField(blank=True, help_text='You may give the interval a friendly name, otherwise an auto-generated name is used.', max_length=255, null=True)),
                ('unit_name', models.CharField(help_text="Name the unit that's being summarised, for instance 'KWh'.", max_length=255)),
                ('unit_fraction', models.FloatField(default=1, help_text="If you are doing an annual summary, you might want to use a different unit than the one from the data entries. If for instance, you are receiving KWh data, you could enter 0.001 and input 'MWh' in the 'unit name' field. Note that this fraction will be applied to ALL meters in the summary, so they should be outputting the same type of unit.")),
                ('backlog', models.IntegerField(default=0, help_text='Number of days to keep old entries for. If you create a new summary and have the necessary data entries, summaries will be created until this point in time.', verbose_name='Backlog')),
                ('force_recreate', models.BooleanField(default=False, help_text='If checked, this will force a one-time recreation of all summaries based on available data entries until the point in time that is according to the backlog number of days above. If you are creating a new interval or have changed the meters included in an interval, this is quite useful! Correcting data entries does not necessitate recreating a whole interval.')),
            ],
            options={
                'verbose_name': 'summary group',
                'verbose_name_plural': 'summary groups',
                'ordering': ('name', 'verbose_name'),
            },
        ),
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Give your meter a name, for instance 'Basement meter'", max_length=255)),
                ('is_counter', models.BooleanField(default=False, help_text='Indicates that the meter is an incremental counter, ie. that every time a new number is received, the difference from the previous number should be logged. If a number is smaller than the previous, the data server assumes that counting has been reset, for instance because the Arduino has rebooted. This does not affect the counting a summarising procedure.', verbose_name='is a counter')),
                ('description', models.TextField(blank=True)),
                ('unit_name', models.CharField(blank=True, help_text="Name the unit that's being summarised, for instance 'KWh'.", max_length=255, null=True)),
                ('unit_fraction', models.FloatField(default=1, help_text="If you are doing an annual summary, you might want to use a different unit than theone from the data entries. If for instance, you are receiving KWh data, you could enter 0.001 and input 'MWh' in the 'unit name' field. Note that this fraction will be applied to ALL meters in the summary, so they should be outputting the same type of unit.")),
                ('default_interval', models.ForeignKey(blank=True, help_text='This is the summary that will most likely be displayed in overviews.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='default_meter', to='arduino_server.intervaltype')),
            ],
            options={
                'verbose_name': 'meter',
                'verbose_name_plural': 'meters',
            },
        ),
        migrations.CreateModel(
            name='MeterType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'meter type',
                'verbose_name_plural': 'meter types',
            },
        ),
        migrations.CreateModel(
            name='MeterData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_point', models.FloatField()),
                ('diff', models.FloatField(blank=True, help_text='This field contains the difference (delta) from the last reading. It is used if the meter is an incremental counter. If you do not fill it out, it is filled out automatically', null=True)),
                ('created', models.DateTimeField()),
                ('meter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arduino_server.meter')),
            ],
            options={
                'verbose_name': 'data entry',
                'verbose_name_plural': 'data entries',
            },
        ),
        migrations.AddField(
            model_name='meter',
            name='meter_type',
            field=models.ForeignKey(help_text="Select a type of meter. For instance you could call all your electricity meters 'Electricity'. This looks good in the front-end!", on_delete=django.db.models.deletion.CASCADE, to='arduino_server.metertype'),
        ),
        migrations.AddField(
            model_name='intervaltype',
            name='meter_set',
            field=models.ManyToManyField(blank=True, help_text='Choose multiple meters if you want this to be a summary of multiple meters. Please note that this would require the units of these meters to be the same!', to='arduino_server.Meter'),
        ),
        migrations.CreateModel(
            name='Interval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.FloatField(blank=True, default=0, null=True)),
                ('average', models.FloatField(blank=True, default=0, null=True)),
                ('from_time', models.DateTimeField()),
                ('to_time', models.DateTimeField(editable=False)),
                ('data_entries', models.IntegerField(default=0)),
                ('interval_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arduino_server.intervaltype')),
            ],
            options={
                'verbose_name': 'summary',
                'verbose_name_plural': 'summaries',
                'unique_together': {('interval_type', 'from_time')},
            },
        ),
    ]
