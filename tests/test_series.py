# -*- coding: utf-8 -*-

import mock
import pytest

from tests.base import TestBase, tvdb
from tvdbrest.client import TVDB, Unauthorized, NotFound, Series


class TestSeriesAPI(TestBase):

    @mock.patch('tvdbrest.client.requests.request')
    def test_get_series(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_mock({
            "data": {
                "id": 1,
            }
        })

        series = tvdb.series(1)
        assert series
        assert isinstance(series, Series)
        assert series.id == 1
    
    @mock.patch('tvdbrest.client.requests.request')
    def test_get_series_does_not_exist(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_404_mock()
        
        with pytest.raises(NotFound):
            tvdb.series(42)
