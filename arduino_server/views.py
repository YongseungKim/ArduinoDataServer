from datetime import datetime

import simplejson
from django.contrib import messages
from django.core.serializers import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse

from arduino_server import models, forms
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
import simplejson as json

# Create your views here.
def hello_world(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def render_to_response_and_add_context(template, c):
    meter_types = models.MeterType.objects.all().order_by("name")
    meters = models.Meter.objects.all()

    c.update({'meter_types': meter_types,
              'meters': meters, })

    # return render_to_response(template, c)


def render_and_add_context(request, template, context):
    meter_types = models.MeterType.objects.all().order_by("name")
    meters = models.Meter.objects.all()

    context.update({
        'meter_types': meter_types,
        'meters': meters,
    })

    return render(request, template, context)


def index(request):
    slideshow_meters = models.Meter.objects.exclude(default_interval=None).order_by('name')

    context = {'slideshow_meters': slideshow_meters, }
    # context = RequestContext(request, c)
    return render_and_add_context(request, "arduino_server/main.html", context)


def meter(request, meter_id):
    meter = get_object_or_404(models.Meter, id=meter_id)
    if request.method == 'POST':
        data_form = forms.MeterDataForm(request.POST)
        if data_form.is_valid():
            data = data_form.save(commit=False)
            data.meter = meter
            data.created = datetime.combine(data_form.cleaned_data['created_date'],
                                            data_form.cleaned_data['created_time'])

            request.session['created_date'] = data_form.cleaned_data['created_date']
            request.session['data_point'] = data_form.cleaned_data['data_point']

            data.save()  # db save
            messages.success(request, _(u"Data entry added and summaries updated!"))
            # return HttpResponseRedirect(reverse('arduino_server:arduino_server_meter', args=(meter.id,)))
            # return redirect('arduino_server/meter.html', meter.id)
            # return render(request, 'arduino_server/meter.html', {'arduino_server_meter': meter})
            return redirect('arduino_server:arduino_server_meter', meter.id)
    else:
        data_form = forms.MeterDataForm(
            initial={'created_date': request.session.get('created_date', datetime.now().date),
                     'created_time': datetime.now().time,
                     'data_point': request.session.get('data_point', None),
                     })

    context = {'meter': meter,
               'data_form': data_form,
               }

    # context = RequestContext(request, c)
    return render_and_add_context(request, "arduino_server/meter.html", context)
    # return render(request, template_name="arduino_server/meter.html", context=context)


def interval_json(request, interval_type_id, max_entries=24, hide_unfinished=0):

    interval_type = get_object_or_404(models.IntervalType, id=interval_type_id)
    intervals = models.Interval.objects.filter(interval_type=interval_type)

    from_date = request.GET.get('from_date', None)
    if from_date:
        from_date = datetime.strptime("%s 00:00" % from_date, "%Y-%m-%d %H:%M")
        intervals = intervals.filter(from_time__gte=from_date)

    to_date = request.GET.get('to_date', None)
    if to_date:
        to_date = datetime.strptime("%s 00:00" % to_date, "%Y-%m-%d %H:%M")
        intervals = intervals.filter(to_time__lte=to_date)

    intervals = intervals.order_by('-from_time')
    max_entries = max_entries or request.GET.get('entries', None)
    if max_entries:
        print('max_entries:', max_entries)
        print('type intervals', intervals)
        for interval in intervals:
            print('interval:', interval.from_time)

        intervals = intervals[:int(max_entries)]

    intervals.reverse()

    def get_google_date(datetimeobj):
        if interval_type.name == models.INTERVAL_HOURLY:
            return "Date(%d, %d, %d, %d, %d, %d, %d)" % (datetimeobj.year,
                                                         datetimeobj.month - 1,
                                                         datetimeobj.day,
                                                         datetimeobj.hour,
                                                         datetimeobj.minute,
                                                         datetimeobj.second + 1,
                                                         datetimeobj.microsecond / 1000)
        else:
            return "Date(%d, %d, %d)" % (datetimeobj.year,
                                         datetimeobj.month - 1,
                                         datetimeobj.day,)

    def get_google_label(from_time, to_time):
        if interval_type.name == models.INTERVAL_ANNUALLY:
            return "%d" % from_time.year
        elif interval_type.name == models.INTERVAL_HOURLY:
            from django.template.defaultfilters import date, time
            return "%s %s-%s" % (
                date(to_time, "DATE_FORMAT").title(), time(from_time, "TIME_FORMAT"), time(to_time, "TIME_FORMAT"))
        elif interval_type.name == models.INTERVAL_DAILY:
            from django.template.defaultfilters import date, time
            return "%s" % date(to_time, "DATE_FORMAT").title()
        elif interval_type.name == models.INTERVAL_WEEKLY:
            from django.template.defaultfilters import date, time
            return "%s - %s" % (date(from_time, "DATE_FORMAT").title(), date(from_time, "DATE_FORMAT").title())
        elif interval_type.name == models.INTERVAL_MONTHLY:
            from django.template.defaultfilters import date, time
            return "%s" % date(from_time, "F Y").title()
        return None

    # data = json.simplejson.dumps({
    data = simplejson.dumps({
        "cols": [
            {"id": "", "label": "", "pattern": "",
             "type": "datetime" if interval_type.name == models.INTERVAL_HOURLY else "date"},
            {"id": "", "label": interval_type.unit_name, "pattern": "", "type": "number"}
        ],
        "rows": [({"c": [{"v": get_google_date(i.to_time), 'f': get_google_label(i.from_time, i.to_time)},
                         {"v": i.total}]}) for i in intervals],
    })
    return HttpResponse(data, content_type='application/json')
