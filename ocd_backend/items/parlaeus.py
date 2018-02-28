from dateutil import parser
from hashlib import sha1
from ocd_backend.items.popolo import EventItem
from ocd_backend.extractors import HttpRequestMixin


class Meeting(EventItem, HttpRequestMixin):

    @staticmethod
    def get_meeting_id(identifier):
        hash_content = u'meeting-%s' % identifier
        return sha1(hash_content.decode('utf8')).hexdigest()

    def get_object_id(self):
        return self.get_meeting_id(self.original_item['agid'])

    def get_original_object_id(self):
        return unicode(self.original_item['agid'])

    def get_original_object_urls(self):
        return {"html": ""}

    def get_rights(self):
        return u'undefined'

    def get_collection(self):
        return unicode(self.source_definition['index_name'])

    def get_combined_index_data(self):
        combined_index_data = {}

        combined_index_data['id'] = unicode(self.get_object_id())
        combined_index_data['hidden'] = self.source_definition['hidden']
        combined_index_data['classification'] = u'Agenda'
        combined_index_data['location'] = self.original_item['location']

        combined_index_data['start_date'] = parser.parse(
            '%s %s' % (self.original_item['date'], self.original_item['time'])
        )

        combined_index_data['children'] = [
            MeetingItem.get_meetingitem_id(mi['apid']) for mi in self.original_item['points']
        ]

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []
        return u' '.join(text_items)


class MeetingItem(EventItem, HttpRequestMixin):

    @staticmethod
    def get_meetingitem_id(identifier):
        hash_content = u'meetingitem-%s' % identifier
        return sha1(hash_content.decode('utf8')).hexdigest()

    def get_object_id(self):
        return self.get_meetingitem_id(self.original_item['apid'])

    def get_original_object_id(self):
        return unicode(self.original_item['apid'])

    def get_original_object_urls(self):
        return {"html": ""}

    def get_rights(self):
        return u'undefined'

    def get_collection(self):
        return unicode(self.source_definition['index_name'])

    def get_combined_index_data(self):
        combined_index_data = {}

        combined_index_data['id'] = unicode(self.get_object_id())
        combined_index_data['hidden'] = self.source_definition['hidden']
        combined_index_data['classification'] = u'Agendapunt'

        combined_index_data['parent_id'] = unicode(Meeting.get_meeting_id(self.original_item['parent']))
        combined_index_data['name'] = self.original_item['title']

        if self.original_item.get('text'):
            combined_index_data['description'] = self.original_item['text']

        media_urls = []
        for doc in self.original_item.get('documents', []):
            media_urls.append(
                {
                    "url": "/v0/resolve/",
                    "note": doc['title'],
                    "original_url": doc['link']
                }
            )
        if media_urls:
            combined_index_data['media_urls'] = media_urls

        return combined_index_data

    def get_index_data(self):
        return {}

    def get_all_text(self):
        text_items = []
        return u' '.join(text_items)
