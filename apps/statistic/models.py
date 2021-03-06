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
from django.db import models
from auth.models import CustomUser as User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

class BaseShareStatistic(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        abstract = True

class EmailShareStatistic(BaseShareStatistic):
    pass
    
class TweeterShareStatistic(BaseShareStatistic):
    pass

class FBShareStatistic(BaseShareStatistic):
    pass

class VideoHit(models.Model):
    video = models.ForeignKey('videos.Video', db_index=True)
    datetime = models.DateTimeField(db_index=True)

class VideoHitsPerDay(models.Model):
    video = models.ForeignKey('videos.Video')
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (('video', 'date'),)

class VideoHitsPerMonth(models.Model):
    video = models.ForeignKey('videos.Video', db_index=True)
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField()
    
    class Meta:
        unique_together = (('video', 'date'),)

class SubtitleView(models.Model):
    subtitle_language = models.ForeignKey('subtitles.SubtitleLanguage',
                                          db_index=True)
    datetime = models.DateTimeField(db_index=True)

class SubtitleViewsPerDay(models.Model):
    subtitle_language = models.ForeignKey('subtitles.SubtitleLanguage',
                                          db_index=True)
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField()
    
    class Meta:
        unique_together = (('subtitle_language', 'date'),)

class SubtitleViewsPerMonth(models.Model):
    subtitle_language = models.ForeignKey('subtitles.SubtitleLanguage',
                                          db_index=True)
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField()
    
    class Meta:
        unique_together = (('subtitle_language', 'date'),)

class LastHitCountMigration(models.Model):
    """Tracks the last time we migrated hit counts to their aggregate
    tables.
    """
    TYPE_CHOICES = [
        ('V', 'Video Hit'),
        ('S', 'Subtitle View'),
    ]
    type = models.CharField(primary_key=True, max_length=1,
                            choices=TYPE_CHOICES)
    date = models.DateField(db_index=True)
