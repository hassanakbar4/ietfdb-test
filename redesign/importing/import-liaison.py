#!/usr/bin/python

import sys, os, re, datetime, pytz

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path = [ basedir ] + sys.path

from ietf import settings
settings.USE_DB_REDESIGN_PROXY_CLASSES = False
settings.IMPORTING_FROM_OLD_SCHEMA = True

from django.core import management
management.setup_environ(settings)

from django.template.defaultfilters import slugify

from ietf.idtracker.models import AreaDirector, IETFWG, Acronym, IRTF
from ietf.liaisons.models import *
from redesign.person.models import *
from redesign.importing.utils import get_or_create_email, old_person_to_person
from redesign.name.models import *
from redesign.name.utils import name


# imports LiaisonDetail, OutgoingLiaisonApproval, Uploads

# todo: LiaisonStatementManager, LiaisonManagers, SDOAuthorizedIndividual

# assumptions:
#  - persons have been imported
#  - groups have been imported

purpose_mapping = {
    1: name(LiaisonStatementPurposeName, "action", "For action"),
    2: name(LiaisonStatementPurposeName, "comment", "For comment"),
    3: name(LiaisonStatementPurposeName, "info", "For information"),
    4: name(LiaisonStatementPurposeName, "response", "In response"),
    5: name(LiaisonStatementPurposeName, "other", "Other"),
    }

purpose_mapping[None] = purpose_mapping[3] # map unknown to "For information"

system_person = Person.objects.get(name="(System)")
obviously_bogus_date = datetime.date(1970, 1, 1)

bodies = {
    'IESG': Group.objects.get(acronym="iesg"),
    'IETF': Group.objects.get(acronym="ietf"),
    'IAB/ISOC': Group.objects.get(acronym="iab"),
    'IAB/IESG': Group.objects.get(acronym="iab"),
    'IAB': Group.objects.get(acronym="iab"),
    'IETF Transport Directorate': Group.objects.get(acronym="tsvdir"),
    'Sigtran': Group.objects.get(acronym="sigtran", type="wg"),
    'IETF RAI WG': Group.objects.get(acronym="rai", type="area"),
    'IETF Mobile IP WG': Group.objects.get(acronym="mobileip", type="wg"),
    }

def get_from_body(name):
    # the from body name is a nice case study in how inconsistencies
    # build up over time
    b = bodies.get(name)
    t = name.split()
    if not b and name.startswith("IETF"):
        if len(t) < 3 or t[2].lower() == "wg":
            b = lookup_group(acronym=t[1].lower(), type="wg")
        elif t[2].lower() in ("area", "ad"):
            print "inside AREA"
            b = lookup_group(acronym=t[1].lower(), type="area")
            if not b:
                b = lookup_group(name=u"%s %s" % (t[1], t[2]), type="area")

    if not b and name.endswith(" WG"):
        b = lookup_group(acronym=t[-2].lower(), type="wg")
                
    if not b:
        b = lookup_group(name=name, type="sdo")

    return b

for o in LiaisonDetail.objects.all().order_by("pk"):#[:10]:
    print "importing LiaisonDetail", o.pk

    try:
        l = LiaisonStatement.objects.get(pk=o.pk)
    except LiaisonStatement.DoesNotExist:
        l = LiaisonStatement(pk=o.pk)

    l.title = (o.title or "").strip()
    l.purpose = purpose_mapping[o.purpose_id]
    if o.purpose_text and not o.purpose and "action" in o.purpose_text.lower():
        o.purpose = purpose_mapping[1]
    l.body = (o.body or "").strip()
    l.deadline = o.deadline_date

    l.related_to_id = o.related_to_id # should not dangle as we process ids in turn

    def lookup_group(**kwargs):
        try:
            return Group.objects.get(**kwargs)
        except Group.DoesNotExist:
            return None

    l.from_name = o.from_body()
    l.from_body = get_from_body(l.from_name) # try to establish link
    continue
    
    l.to_body = o.to_raw_body
    l.to_name = o.to_raw_body
    l.to_contact = (o.to_poc or "").strip()

    l.reply_to = (o.replyto or "").strip()

    l.response_contact = (o.response_contact or "").strip()
    l.technical_contact = (o.technical_contact or "").strip()
    l.cc = (o.cc1 or "").strip()
    
    l.submitted = o.submitted_date
    l.submitted_by = old_person_to_person(o.person)
    l.modified = o.last_modified_date
    l.approved = o.approval and o.approval.approved and (o.approval.approval_date or l.modified or datetime.datetime.now())

    l.action_taken = o.action_taken
    
    #l.save()
