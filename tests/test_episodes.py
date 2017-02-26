# -*- coding: utf-8 -*-

import mock
import pytest

from tests.base import TestBase, tvdb
from tvdbrest.client import TVDB, Unauthorized, NotFound, Episode


class TestEpisodesAPI(TestBase):

    @mock.patch('tvdbrest.client.requests.request')
    def test_get_episode(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_mock({
            "data": {
                "id": 1,
            }
        })

        episode = tvdb.episode_details(1)
        assert episode
        assert isinstance(episode, Episode)
        assert episode.id == 1
    
    @mock.patch('tvdbrest.client.requests.request')
    def test_episodes_does_not_exist(self, request_method_mock, tvdb):
        request_method_mock.return_value = self.api_response_404_mock()
        
        with pytest.raises(NotFound):
            tvdb.episode_details(1)

