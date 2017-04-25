#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import hashlib
import mock
import time
import traceback
from datetime import datetime
from unittest import TestCase

from preggy import expect
import pylibmc

from thumbor_memcached.result_storage import (
    Storage
)

class MemcacheStorageTestCase(TestCase):
    def setUp(self, *args, **kw):
        super(MemcacheStorageTestCase, self).setUp(*args, **kw)
        self.memcached = pylibmc.Client(
            ['localhost:5555'],
            binary=True,
            behaviors={
                'tcp_nodelay': True,
                'no_block': True,
                'ketama': True
            }
        )

        self.memcached.flush_all()

        self.request_url_fixture = 'https://wikipedia.org'
        self.context = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                RESULT_STORAGE_EXPIRATION_SECONDS=120,
            ),
            request=mock.Mock(
              url=self.request_url_fixture
            )
        )

    def test_can_create_storage(self):
        storage = Storage(self.context)
        expect(storage).not_to_be_null()

    def test_can_get_result_key_for_url(self):
        storage = Storage(self.context)
        url = 'http://www.globo.com/'
        expected = hashlib.sha1('thumbor-result-%s' % url).hexdigest()
        expect(storage.result_key_for(url)).to_equal(expected)

    def test_can_get_timestamp_key_for_url(self):
        storage = Storage(self.context)
        url = 'http://www.globo.com/'
        expected = hashlib.sha1('thumbor-result-timestamp-%s' % url).hexdigest()
        expect(storage.timestamp_key_for(url)).to_equal(expected)

    def test_can_put_data(self):
        storage = Storage(self.context)
        storage.put('test-data')
        data = self.memcached.get(storage.result_key_for(self.request_url_fixture))
        expect(data).to_equal('test-data')

    def test_can_write_less_than_item_size_max(self):
        storage = Storage(self.context)
        test_data = 'a' * (2**19)
        result_key = storage.result_key_for(self.request_url_fixture)
        stored_path = storage.put(test_data)
        expect(stored_path).to_equal(self.request_url_fixture)

        data = self.memcached.get(result_key)
        expect(data).to_equal(test_data)

    def test_can_not_write_more_than_item_size_max(self):
        storage = Storage(self.context)
        test_data = 'a' * (2 ** 20)
        try:
            storage.put(test_data)
            data = self.memcached.get(storage.result_key_for(self.request_url_fixture))
            raise AssertionError('should have thrown TooBig error')
        except Exception, err:
            trace = traceback.format_exc()
            expect('TooBig' in trace or 'TOO BIG' in trace).to_be_true()

    def test_can_default_item_size_max_from_config(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                MEMCACHE_ITEM_SIZE_MAX=(1024 * 1024)
            )
        )
        storage = Storage(ctx)
        expect(storage.item_size_max()).to_equal(1024 * 1024)

    def test_can_skip_storage_after_item_size_max(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                RESULT_STORAGE_EXPIRATION_SECONDS=120,
                MEMCACHE_ITEM_SIZE_MAX=(1024 * 1024),
                MEMCACHE_SKIP_STORAGE_EXCEEDING_ITEM_SIZE_MAX=True
            ),
            request=mock.Mock(
              url=self.request_url_fixture
            )
        )
        storage = Storage(ctx)
        test_data = 'a' * (2 ** 20)
        is_stored = storage.put(test_data)
        expect(is_stored).to_equal(None)

        does_exist = storage.exists(storage.result_key_for, self.request_url_fixture)
        expect(does_exist).to_be_false()

    def test_can_get_data(self):
        storage = Storage(self.context)
        self.memcached.set(storage.result_key_for(self.request_url_fixture), 'test-data')

        data = storage.get().result()
        expect(data).to_equal('test-data')

    def test_can_put_and_get_data(self):
        storage = Storage(self.context)
        storage.put('test-data')
        data = storage.get().result()
        expect(data).to_equal('test-data')

        does_exist = storage.exists(storage.result_key_for, self.request_url_fixture)
        expect(does_exist).to_be_true()

    def test_can_put_and_get_last_update_data(self):
        storage = Storage(self.context)
        test_data = 'a' * (2 ** 19)
        pre_test_time = datetime.utcnow()
        storage.put(test_data)
        post_test_time = datetime.utcnow()

        expect(pre_test_time < storage.last_updated() < post_test_time).to_be_true()
        data = storage.get().result()
        expect(data).to_equal(test_data)

    def test_can_not_retrieve_deleted_files(self):
        ctx = mock.Mock(
            config=mock.Mock(
                MEMCACHE_STORAGE_SERVERS=[
                    'localhost:5555',
                ],
                RESULT_STORAGE_EXPIRATION_SECONDS=120,
                MEMCACHE_ITEM_SIZE_MAX=(1024 * 1024),
                MEMCACHE_SKIP_STORAGE_EXCEEDING_ITEM_SIZE_MAX=True
            ),
            request=mock.Mock(
              url=self.request_url_fixture
            )
        )
        storage = Storage(ctx)
        storage.put('a')
        expect(storage.get().result()).to_equal('a')

        result_key = storage.result_key_for(self.request_url_fixture)
        timestamp_key = storage.timestamp_key_for(self.request_url_fixture)
        self.memcached.delete(result_key)
        self.memcached.delete(timestamp_key)

        expect(storage.get().result()).to_equal(None)
        expect(storage.last_updated()).to_equal(None)
