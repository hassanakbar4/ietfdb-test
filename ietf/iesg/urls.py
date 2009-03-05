# Copyright The IETF Trust 2007, All Rights Reserved

# Portion Copyright (C) 2008 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
# 
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
# 
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from django.conf.urls.defaults import patterns
from django.conf import settings
from ietf.iesg import views
from ietf.iesg.models import TelechatMinutes
from ietf.idtracker.models import BallotInfo

#urlpatterns = patterns('django.views.generic.list_detail',
#     (r'^lastcall/$', 'object_list', {
#	     'queryset': InternetDraft.objects.all() }),
#)

queryset = TelechatMinutes.objects.all()
telechat_detail = {
    'queryset': queryset,
    'date_field': 'telechat_date',
}
telechat_archive = dict(telechat_detail, allow_empty=True)

queryset_ann = BallotInfo.objects.all()

urlpatterns = patterns('django.views.generic.date_based',
	(r'^telechat/$', 'archive_index', telechat_archive),
	(r'^telechat/y/(?P<year>\d{4})/$', 'archive_year', telechat_archive),
	(r'^telechat/y/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', telechat_archive),
)

urlpatterns += patterns('django.views.generic.list_detail',
	(r'^telechat/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset }),
	(r'^ann/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_ann, 'template_name':"iesg/ballotinfo_detail.html" }),
)

urlpatterns += patterns('',
        (r'^agenda/$', views.telechat_agenda),                        
        (r'^ann/ind/$',views.inddocs),
        (r'^ann/(?P<cat>[^/]+)/$',views.wgdocs),
)

if settings.SERVER_MODE != 'production':
    urlpatterns += patterns('',
        (r'^agenda/(?P<date>\d{4}-\d\d-\d\d)/$', views.telechat_agenda),                        
    )
