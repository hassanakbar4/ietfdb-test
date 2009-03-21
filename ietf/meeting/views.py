# Copyright The IETF Trust 2007, All Rights Reserved

# Create your views here.
#import models
from django.shortcuts import render_to_response as render, get_object_or_404
from ietf.proceedings.models import Meeting, MeetingTime, WgMeetingSession, NonSession, MeetingVenue, IESGHistory, Proceeding, Switches
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
import datetime

def show_html_materials(request, meeting_num=None):
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_num)
    begin_date = proceeding.sub_begin_date
    cut_off_date = proceeding.sub_cut_off_date
    cor_cut_off_date = proceeding.c_sub_cut_off_date
    now = datetime.date.today()
    if now > cor_cut_off_date:
        return render("meeting/list_closed.html",{'meeting_num':meeting_num,'begin_date':begin_date, 'cut_off_date':cut_off_date, 'cor_cut_off_date':cor_cut_off_date})
    sub_began = 0
    if now > begin_date:
        sub_began = 1
    # List of WG sessions and Plenary sessions
    queryset_list = WgMeetingSession.objects.filter(Q(meeting=meeting_num, group_acronym_id__gte = -2, status_id=4), Q(irtf__isnull=True) | Q(irtf=0))
    queryset_irtf = WgMeetingSession.objects.filter(meeting=meeting_num, group_acronym_id__gte = -2, status_id=4, irtf__gt=0)
    queryset_interim = []
    queryset_training = []
    for item in list(WgMeetingSession.objects.filter(meeting=meeting_num)):
        if item.interim_meeting():
            item.interim=1
            queryset_interim.append(item)
        if item.group_acronym_id < -2:
            if item.slides():
                queryset_training.append(item)
    return object_list(request,queryset=queryset_list, template_name="meeting/list.html",allow_empty=True, extra_context={'meeting_num':meeting_num,'irtf_list':queryset_irtf, 'interim_list':queryset_interim, 'training_list':queryset_training, 'begin_date':begin_date, 'cut_off_date':cut_off_date, 'cor_cut_off_date':cor_cut_off_date,'sub_began':sub_began})

def current_materials(request):
    meeting = Meeting.objects.order_by('-meeting_num')[0]
    return HttpResponseRedirect( reverse(show_html_materials, args=[meeting.meeting_num]) )

def get_plenary_agenda(meeting_num, id):
    try:
        plenary_agenda_file = "/a/www/ietf/proceedings/%s" % WgMeetingSession.objects.get(meeting=meeting_num,group_acronym_id=id).agenda_file()
        try:
            f = open(plenary_agenda_file)
            plenary_agenda = f.read()
            f.close()
            return plenary_agenda
        except IOError:
             return "THE AGENDA HAS NOT BEEN UPLOADED YET"
    except WgMeetingSession.DoesNotExist:
        return "The Plenary has not been scheduled"

def html_agenda(request, num=None):
    if not num:
        num = list(Meeting.objects.all())[-1].meeting_num
    timeslots = MeetingTime.objects.filter(meeting=num).order_by("day_id", "time_desc")
    update = get_object_or_404(Switches,id=1)
    meeting=get_object_or_404(Meeting, meeting_num=num)
    venue = get_object_or_404(MeetingVenue, meeting_num=num)
    ads = list(IESGHistory.objects.filter(meeting=num))
    if not ads:
        ads = list(IESGHistory.objects.filter(meeting=str(int(num)-1)))
    ads.sort(key=(lambda item: item.area.area_acronym.acronym))
    plenaryw_agenda = get_plenary_agenda(num, -1)
    plenaryt_agenda = get_plenary_agenda(num, -2)
    return render("meeting/agenda.html",
        {"timeslots":timeslots, "update":update, "meeting":meeting, "venue":venue, "ads":ads,
            "ops_plenary_agenda":plenaryw_agenda, "tech_plenary_agenda":plenaryt_agenda, },
        RequestContext(request))

def text_agenda(request, num):
    timeslots = MeetingTime.objects.filter(meeting=num).order_by("day_id", "time_desc")
    update = get_object_or_404(Switches,id=1)
    meeting=get_object_or_404(Meeting, meeting_num=num)
    venue = get_object_or_404(MeetingVenue, meeting_num=num)
    ads = list(IESGHistory.objects.filter(meeting=num))
    if not ads:
        ads = list(IESGHistory.objects.filter(meeting=str(int(num)-1)))
    ads.sort(key=(lambda item: item.area.area_acronym.acronym))
    return HttpResponse(render_to_string("meeting/agenda.txt",
        {"timeslots":timeslots, "update":update, "meeting":meeting, "venue":venue, "ads":ads},
        RequestContext(request)), mimetype="text/plain")
    