import logging
import time
import simplejson
import requests

from django.http import HttpResponse
from django.test.client import RequestFactory, Client
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from apps.videos.models import Video
from apps.testhelpers.views import _create_videos
from apps.subtitles import pipeline
from apps.teams.models import TeamMember
from babelsubs import load_from_file 
from teams.models import BillingRecord

from webdriver_testing.data_factories import UserFactory
from webdriver_testing.data_factories import TeamVideoFactory
from webdriver_testing.data_factories import VideoUrlFactory


class DataHelpers(object):
    def __init__(self):
        self.logger = logging.getLogger('test_steps')
        self.logger.setLevel(logging.INFO)


    def api_url(self, url_part):
        base_url = 'http://%s/' % Site.objects.get_current().domain
        self.logger.info(base_url)
        self.logger.info(url_part)
        if url_part.startswith('http'):
            return url_part
        elif url_part.startswith('/api2/partners'):
            return (base_url + url_part[1:])
        else:
            return (base_url + 'api2/partners/' + url_part)


    def make_request(self, api_user, request_type, url_part, **kwargs):
        s = requests.session()
        s.config['keep_alive'] = False
        url = self.api_url(url_part)
        self.logger.info(url)
        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-apikey': api_user.get_api_key(),
                    'X-api-username': api_user.username,
                  }
        r = getattr(s, request_type)(url, headers=headers, data=simplejson.dumps(kwargs))
        self.logger.info('RESP: %s - %s' %(r.status_code, r.content))
        return r

    def create_video(self, **kwargs):
        v = VideoUrlFactory.create(**kwargs)
        return v.video
           

    def super_user(self):
        superuser = UserFactory.build(is_partner=True, 
                                 is_staff=True, 
                                 is_superuser=True) 
        auth = dict(username=superuser.username, password='password')
        return auth


    def upload_subs(self, user, **kwargs):
        defaults = {'language_code': 'en',
                    'draft': open('apps/webdriver_testing/subtitle_data/'
                            'Timed_text.en.srt'),
                    'complete': 1
                    }
        defaults.update(kwargs)
        self.logger.info(defaults)
        c = Client()
        try:
            c.login(username=user.username, password='password')
        except:
            c.login(**self.super_user())
        response = c.post(reverse('videos:upload_subtitles'), defaults)
        self.logger.info('UPLOAD RESPONSE %s' % response)

    def add_subs(self, **kwargs):
        defaults = {
                    'language_code': 'en',
                    'complete': True, 
                    'visibility': 'public'
                   }
        defaults.update(kwargs)
        default_subs = ('apps/webdriver_testing/subtitle_data'
                       '/basic_subs.dfxp')
        s = defaults.get('subtitles', default_subs)
        
        subs = load_from_file(s, language=defaults['language_code'])
        sub_items = subs.to_internal()
        defaults['subtitles'] = sub_items
        v = pipeline.add_subtitles(**defaults)
        return v

    def create_video_with_subs(self, user, **kwargs ):
        """Create a video and subtitles.
    
        """
        video = self.create_video()
        kwargs['video'] = video
        self.add_subs(**kwargs)
        return video


    def create_several_team_videos_with_subs(self, team, teamowner, data=None):
        """Uses the helper data from the apps.videos.fixtures to create data.

           The test vidoes are then assigned to the specified team.
           Returns the list of video.
        """
        if not data:
            testdata = simplejson.load(open('apps/videos/fixtures/teams-list.json'))
        else:
            testdata = simplejson.load(open(data))
        videos = _create_videos(testdata, [])
        for video in videos:
            TeamVideoFactory.create(
                team=team, 
                video=video, 
                added_by=teamowner)
        return videos


    def create_videos_with_fake_subs(self, testdata=None):
        if testdata is None:
            testdata = simplejson.load(open('apps/videos/fixtures/teams-list.json'))
        else:
            testdata = simplejson.load(open(testdata))
        videos = _create_videos(testdata, [])
        return videos

    def complete_review_task(self, tv, status_code, assignee, note=None):
        """Complete the review task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        task = list(tv.task_set.incomplete_review().all())[0]
        task.assignee = assignee
        task.approved = status_code
        if note:
            task.body = note
        task.save()
        task.complete()

    def complete_approve_task(self, tv, status_code, assignee, note=None):
        """Complete the approve task, 20 for approve, 30 for reject.
 
        Making the assumtion that I have only 1 at a time.

        """
        task = list(tv.task_set.incomplete_approve().all())[0]
        task.assignee = assignee 
        task.approved = status_code
        if note:
            task.body = note
        task.save()
        task.complete()
