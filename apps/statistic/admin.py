# Amara, universalsubtitles.org
# 
# Copyright (C) 2013 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.
from django.contrib import admin
from django.db import models
from django.views.generic.list_detail import object_list
from kombu_backends.amazonsqs import SQSLoggingConnection

from statistic.log_methods import LogAdmin, LogFakeModel
from utils.celery_search_index import LogEntry

# add logging statistic display for SQS API usage
LogAdmin.register('SQS usage', SQSLoggingConnection.logger_backend)

admin.site.register(LogFakeModel, LogAdmin)


# add logging statistic for search index update
class LogEntryAdmin(admin.ModelAdmin):
    rmodel = LogEntry

    @classmethod
    def fake_model(cls):
        class LogEntryFakeModel(models.Model):

            class Meta:
                managed = False
                verbose_name = cls.rmodel._meta['verbose_name']
                verbose_name_plural =  cls.rmodel._meta['verbose_name_plural']

        return LogEntryFakeModel

    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        app_label = opts.app_label
        title = opts.verbose_name_plural

        qs = self.rmodel.objects.all()

        context = {
            'app_label': app_label,
            'title': title
        }
        return object_list(request, queryset=qs,
                           paginate_by=self.list_per_page,
                           template_name='statistic/log_entry_model_admin.html',
                           template_object_name='object',
                           extra_context=context)

    def has_change_permission(self, request, obj=None):
        return not bool(obj)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(LogEntryAdmin.fake_model(), LogEntryAdmin)
