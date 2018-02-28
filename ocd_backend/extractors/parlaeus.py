import json

from dateutil.parser import parse
from ocd_backend.extractors import BaseExtractor, HttpRequestMixin
from ocd_backend.log import get_source_logger

log = get_source_logger('extractor')


class ParlaeusMeetingsExtractor(BaseExtractor, HttpRequestMixin):
    """
    A meetings extractor for the Parlaeus API.
    """

    def __init__(self, *args, **kwargs):
        super(ParlaeusMeetingsExtractor, self).__init__(*args, **kwargs)
        self.base_url = self.source_definition['base_url']
        self.rid = self.source_definition['session_id']

    def run(self):
        resp = self.http_session.get(
            '%s?rid=%s&fn=agenda_list&since=%s&until=%s' % (
                self.base_url,
                self.rid,
                parse(self.source_definition['start_date']).strftime("%Y%m%d"),
                parse(self.source_definition['end_date']).strftime("%Y%m%d"),
            )
        )
        resp.raise_for_status()

        json_data = resp.json()
        meetings = json_data.get('list')

        for meeting in meetings:
            # todo test for last_change before processing

            if not meeting['agid']:
                log.error("The value for 'agid' seems to be empty, skipping")
                continue

            resp = self.http_session.get(
                '%s?rid=%s&fn=agenda_detail&agid=%s' % (
                    self.base_url,
                    self.rid,
                    meeting['agid'],
                )
            )
            resp.raise_for_status()

            meeting_data = resp.json()
            yield 'application/json', json.dumps(meeting_data['agenda'])


class ParlaeusMeetingitemsExtractor(ParlaeusMeetingsExtractor, HttpRequestMixin):
    """
    A meetingitems extractor for the Parlaeus API.
    """

    def run(self):
        resp = self.http_session.get(
            '%s?rid=%s&fn=agenda_list' % (
                self.base_url,
                self.rid,
            )
        )
        resp.raise_for_status()

        json_data = resp.json()
        meetings = json_data.get('list')

        for meeting in meetings:
            # todo test for last_change before processing

            resp = self.http_session.get(
                '%s?rid=%s&fn=agenda_detail&agid=%s' % (
                    self.base_url,
                    self.rid,
                    meeting['agid'],
                )
            )
            resp.raise_for_status()

            meeting_data = resp.json()

            for meeting_item in meeting_data['agenda']['points']:
                meeting_item['parent'] = meeting_data['agenda']['agid']
                yield 'application/json', json.dumps(meeting_item)
