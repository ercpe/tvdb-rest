# -*- coding: utf-8 -*-
import datetime

import mock

from tests.base import TestBase, tvdb
from tvdbrest.client import  Update


class TestUpdateAPI(TestBase):
    
    def test_updated(self, tvdb):
        tvdb._api_request = mock.MagicMock()
    
        tvdb.updates(123)
    
        tvdb._api_request.assert_called_with('get', '/updated/query?fromTime=123')

    @mock.patch('tvdbrest.client.requests.request')
    def test_updated_result(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_mock({
            "data": [{
                "id": 1,
                'lastUpdated': 123
            }]
        })

        updates = tvdb.updates(from_time=10)
        assert updates
        assert isinstance(updates, list) and all(isinstance(x, Update) for x in updates)
        assert len(updates) == 1

        get_series_mock = mock.MagicMock()
        tvdb.series = get_series_mock
        
        update = updates[0]
        update.series
        get_series_mock.assert_called_with(1)

    @mock.patch('tvdbrest.client.urlencode')
    def test_updated_with_datetimes(self, urlencode_mock, tvdb):
        tvdb._api_request = mock.MagicMock()

        dt = datetime.datetime(2017, 2, 26, 17, 00, 00, tzinfo=datetime.timezone.utc)
        tvdb.updates(dt)
        
        urlencode_mock.assert_called_with({
            'fromTime': 1488124800
        })

    @mock.patch('tvdbrest.client.urlencode')
    def test_updated_with_datetimes_to(self, urlencode_mock, tvdb):
        tvdb._api_request = mock.MagicMock()
    
        dt1 = datetime.datetime(2017, 2, 26, 17, 00, 00, tzinfo=datetime.timezone.utc)
        dt2 = datetime.datetime(2017, 2, 26, 18, 00, 00, tzinfo=datetime.timezone.utc)
        tvdb.updates(dt1, to_time=dt2)
    
        urlencode_mock.assert_called_with({
            'fromTime': 1488124800,
            'toTime': 1488128400
        })
