#!/usr/bin/python

import sys, os, re, datetime

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path = [ basedir ] + sys.path

from ietf import settings
settings.USE_DB_REDESIGN_PROXY_CLASSES = False

from django.core import management
management.setup_environ(settings)

from redesign import unaccent
from redesign.person.models import *
from redesign.group.models import *
from redesign.name.models import *
from redesign.name.utils import name
from redesign.importing.utils import old_person_to_email, clean_email_address
from ietf.idtracker.models import IESGLogin, AreaDirector, IDAuthor, PersonOrOrgInfo, WGChair, WGEditor, WGSecretary, WGTechAdvisor, ChairsHistory, Role as OldRole, Acronym, IRTFChair


# assumptions:
#  - groups have been imported

# PersonOrOrgInfo/PostalAddress/EmailAddress/PhoneNumber are not
# imported, although some information is retrieved from those

# imports IESGLogin, AreaDirector, WGEditor, WGChair, IRTFChair,
# WGSecretary, WGTechAdvisor, NomCom chairs from ChairsHistory,
#
# also imports persons from IDAuthor, announcement originators from
# Announcements

# FIXME: should probably import Role

area_director_role = name(RoleName, "ad", "Area Director")
inactive_area_director_role = name(RoleName, "ex-ad", "Ex-Area Director", desc="Inactive Area Director")
chair_role = name(RoleName, "chair", "Chair")
editor_role = name(RoleName, "editor", "Editor")
secretary_role = name(RoleName, "secr", "Secretary")
techadvisor_role = name(RoleName, "techadv", "Tech Advisor")

# helpers for creating the objects
def get_or_create_email(o, create_fake):
    email = old_person_to_email(o.person)
    if not email:
        if create_fake:
            email = u"unknown-email-%s-%s" % (o.person.first_name, o.person.last_name)
            print ("USING FAKE EMAIL %s for %s %s %s" % (email, o.person.pk, o.person.first_name, o.person.last_name)).encode('utf-8')
        else:
            print ("NO EMAIL FOR %s %s %s %s %s" % (o.__class__, o.pk, o.person.pk, o.person.first_name, o.person.last_name)).encode('utf-8')
            return None
    
    e, _ = Email.objects.select_related("person").get_or_create(address=email)
    if not e.person:
        n = u"%s %s" % (o.person.first_name, o.person.last_name)
        asciified = unaccent.asciify(n)
        aliases = Alias.objects.filter(name__in=(n, asciified))
        if aliases:
            p = aliases[0].person
        else:
            p = Person.objects.create(id=o.person.pk, name=n, ascii=asciified)
            # FIXME: fill in address?
            
            Alias.objects.create(name=n, person=p)
            if asciified != n:
                Alias.objects.create(name=asciified, person=p)
        
        e.person = p
        e.save()

    return e

# WGEditor
for o in WGEditor.objects.all():
    acronym = Acronym.objects.get(acronym_id=o.group_acronym_id).acronym
    print "importing WGEditor", acronym, o.person

    email = get_or_create_email(o, create_fake=True)
    group = Group.objects.get(acronym=acronym)

    Role.objects.get_or_create(name=editor_role, group=group, email=email)

# WGSecretary
for o in WGSecretary.objects.all():
    acronym = Acronym.objects.get(acronym_id=o.group_acronym_id).acronym
    print "importing WGSecretary", acronym, o.person

    email = get_or_create_email(o, create_fake=True)
    group = Group.objects.get(acronym=acronym)

    Role.objects.get_or_create(name=secretary_role, group=group, email=email)

# WGTechAdvisor
for o in WGTechAdvisor.objects.all():
    acronym = Acronym.objects.get(acronym_id=o.group_acronym_id).acronym
    print "importing WGTechAdvisor", acronym, o.person

    email = get_or_create_email(o, create_fake=True)
    group = Group.objects.get(acronym=acronym)

    Role.objects.get_or_create(name=techadvisor_role, group=group, email=email)

# WGChair
for o in WGChair.objects.all():
    # there's some garbage in this table, so wear double safety belts
    try:
        acronym = Acronym.objects.get(acronym_id=o.group_acronym_id).acronym
    except Acronym.DoesNotExist:
        print "SKIPPING WGChair with unknown acronym id", o.group_acronym_id
        continue

    try:
        person = o.person
    except PersonOrOrgInfo.DoesNotExist:
        print "SKIPPING WGChair", acronym, "with invalid person id", o.person_id
        continue
    
    if acronym in ("apples", "apptsv", "usac", "null", "dirdir"):
        print "SKIPPING WGChair", acronym, o.person
        continue

    print "importing WGChair", acronym, o.person

    email = get_or_create_email(o, create_fake=True)
    group = Group.objects.get(acronym=acronym)

    Role.objects.get_or_create(name=chair_role, group=group, email=email)

# IRTFChair
for o in IRTFChair.objects.all():
    acronym = o.irtf.acronym.lower()
    print "importing IRTFChair", acronym, o.person

    email = get_or_create_email(o, create_fake=True)
    group = Group.objects.get(acronym=acronym)

    Role.objects.get_or_create(name=chair_role, group=group, email=email)

# NomCom chairs
nomcom_groups = list(Group.objects.filter(acronym__startswith="nomcom").exclude(acronym="nomcom"))
for o in ChairsHistory.objects.filter(chair_type=OldRole.NOMCOM_CHAIR):
    print "importing NOMCOM chair", o
    for g in nomcom_groups:
        if ("%s/%s" % (o.start_year, o.end_year)) in g.name:
            break

    email = get_or_create_email(o, create_fake=False)
    
    Role.objects.get_or_create(name=chair_role, group=g, email=email)

# IESGLogin
for o in IESGLogin.objects.all():
    print "importing IESGLogin", o.id, o.first_name, o.last_name
    
    if not o.person:
        persons = PersonOrOrgInfo.objects.filter(first_name=o.first_name, last_name=o.last_name)
        if persons:
            o.person = persons[0]
        else:
            print "NO PERSON", o.person_id
            continue

    email = get_or_create_email(o, create_fake=False)
    if not email:
        continue

    user, _ = User.objects.get_or_create(username=o.login_name)
    email.person.user = user
    email.person.save()

    # current ADs are imported below
    if o.user_level == IESGLogin.SECRETARIAT_LEVEL:
        if not Role.objects.filter(name=secretary_role, email=email):
            Role.objects.create(name=secretary_role, group=Group.objects.get(acronym="secretariat"), email=email)
    elif o.user_level == IESGLogin.INACTIVE_AD_LEVEL:
        if not Role.objects.filter(name=inactive_area_director_role, email=email):
            # connect them directly to the IESG as we don't really know where they belong
            Role.objects.create(name=inactive_area_director_role, group=Group.objects.get(acronym="iesg"), email=email)
    
# AreaDirector
for o in AreaDirector.objects.all():
    if not o.area:
        print "NO AREA", o.person, o.area_id
        continue
    
    print "importing AreaDirector", o.area, o.person
    email = get_or_create_email(o, create_fake=False)
    
    area = Group.objects.get(acronym=o.area.area_acronym.acronym)

    if area.state_id == "active":
        role_type = area_director_role
    else:
         # can't be active area director in an inactive area
        role_type = inactive_area_director_role
    
    r = Role.objects.filter(name__in=(area_director_role, inactive_area_director_role),
                            email=email)
    if r and r[0].group == "iesg":
        r[0].group = area
        r[0].name = role_type
        r[0].save()
    else:
        Role.objects.get_or_create(name=role_type, group=area, email=email)


# Announcement persons
for o in PersonOrOrgInfo.objects.filter(announcement__announcement_id__gte=1).distinct():
    print "importing Announcement originator", o.person_or_org_tag, o.first_name.encode('utf-8'), o.last_name.encode('utf-8')

    o.person = o # satisfy the get_or_create_email interface
    
    email = get_or_create_email(o, create_fake=False)
    
# IDAuthor persons
for o in IDAuthor.objects.all().order_by('id').select_related('person').iterator():
    print "importing IDAuthor", o.id, o.person_id, o.person.first_name.encode('utf-8'), o.person.last_name.encode('utf-8')
    email = get_or_create_email(o, create_fake=True)

    # we may also need to import email address used specifically for
    # the document
    addr = clean_email_address(o.email() or "")
    if addr and addr.lower() != email.address.lower():
        try:
            e = Email.objects.get(address=addr)
            if e.person != email.person or e.active != False:
                e.person = email.person
                e.active = False
                e.save()
        except Email.DoesNotExist:
            Email.objects.create(address=addr, person=email.person, active=False)
    
