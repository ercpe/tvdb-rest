# -*- coding: utf-8 -*-

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
