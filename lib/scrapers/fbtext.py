from tornado import gen
from facebook import GraphAPI

from lib.config import CONFIG
from .lib.utils import facebook_paginate
from .lib.basescraper import BaseScraper


class FBTextScraper(BaseScraper):
    name = 'fbtext'

    @property
    def num_posts_per_user(self):
        if CONFIG['_mode'] == 'prod':
            return 2000
        return 100

    def message_filter(self, data):
        pfiltered = []
        lfiltered = []
        for i in data:
            if 'message' in i:
                pfiltered.append({'text': i['message'],
                                  'creation_date': i['created_time']})
            if 'link' in i:
                lfiltered.append(i['link'])
        return pfiltered, lfiltered

    @gen.coroutine
    def scrape(self, user_data):
        try:
            oauth = user_data.services['facebook']['access_token']
        except KeyError:
            return False
        graph = GraphAPI(access_token=oauth)
        data = {
            "text": [],
            "links": []
        }

        posts = []
        posts_blob = yield facebook_paginate(
            graph.get_connections(
                'me',
                'posts',
                fields='message, link, created_time'
            ),
            max_results=self.num_posts_per_user
        )
        posts, links = self.message_filter(posts_blob)

        # To do comments we'd have to go through the different posts and look
        # Scraping the person's feed is another option, but we get more garbage
        data['text'] = posts
        data['links'] = links
        return data
