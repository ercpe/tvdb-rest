# -*- coding: utf-8 -*-
import pytest
import mock

from tvdbrest.client import TVDB


@pytest.fixture
def tvdb():
    tvdb = TVDB("myusername", "myuserkey", "myapikey")
    tvdb.jwttoken = "test-token"
    return tvdb


class TestBase(object):

    def api_response_mock(self, json):
        m = mock.MagicMock()
        m.status_code = 200
        m.json = mock.Mock(return_value=json)
        return m
    
    def api_response_404_mock(self):
        m = mock.MagicMock()
        m.status_code = 404
        return m
