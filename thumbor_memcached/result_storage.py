#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import hashlib
import sys
from datetime import datetime
from json import loads, dumps

import pylibmc

from thumbor.result_storages import BaseStorage
from tornado.concurrent import return_future
from thumbor.utils import logger


LOG_PREFIX = 'MEMCACHE_RESULT_STORAGE'

class Storage(BaseStorage):

    def __init__(self, context):
        BaseStorage.__init__(self, context)

        self.storage = pylibmc.Client(
            self.context.config.MEMCACHE_STORAGE_SERVERS,
            binary=True,
            behaviors={
                'tcp_nodelay': True,
                'no_block': True,
                'ketama': True
            }
        )

    def get_hash(self, msg):
        '''
        :rettype: string
        '''
        msg = msg.encode('utf-8', 'replace')
        return hashlib.sha1(msg).hexdigest()

    def result_key_for(self, url):
        '''
        :rettype: string
        '''
        return self.get_hash('thumbor-result-%s' % url)

    def timestamp_key_for(self, url):
        '''
        :rettype: string
        '''
        return self.get_hash('thumbor-result-timestamp-%s' % url)

    def item_size_max(self):
        '''
        Memcache default is 1MB.
        https://github.com/memcached/memcached/commit/bed5f9bba1a02ae7176a9082cfadbd7a0d194bba

        :rettype: int
        '''
        return self.context.config.MEMCACHE_ITEM_SIZE_MAX

    def skip_storage(self):
        '''
        :rettype: bool
        '''
        return self.context.config.MEMCACHE_SKIP_STORAGE_EXCEEDING_ITEM_SIZE_MAX

    def content_size_exceeded_max(self, content_bytes):
        '''
        `sys.getsizeof` works great for this use case because we have a byte
        sequence, and not a recursive nested structure. The unit of Memcache
        `item_size_max` is also bytes.

        :rettype: tuple(bool, int)
        '''
        content_size = sys.getsizeof(content_bytes)
        if content_size > self.item_size_max():
            return (True, content_size)

        return (False, content_size)

    def put(self, content_bytes):
        '''
        Save the `bytes` under a key derived from `path` in Memcache.

        :return: A string representing the content path if it is stored.
        :rettype: string or None
        '''
        derived_path = self.context.request.url
        over_max, content_size = self.content_size_exceeded_max(content_bytes)

        logger.debug('[{log_prefix}] content size in bytes: {size}'
            ' | is over max? {over_max} | skip storage? {skip}'.format(
            log_prefix=LOG_PREFIX, size=content_size, over_max=over_max,
            skip=self.skip_storage()))

        if (over_max and self.skip_storage()):
            # Short-circuit the storage when configured to skip large items
            logger.debug('[{log_prefix}] skipping storage: {content_size} '
                           'exceeds item_size_max of {max_size}'.format(
                           log_prefix=LOG_PREFIX, content_size=content_size,
                           max_size=self.item_size_max()))
            return None

        self.storage.set(
            self.timestamp_key_for(derived_path), datetime.utcnow(),
            time=self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS
        )
        self.storage.set(
            self.result_key_for(derived_path), content_bytes,
            time=self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS
        )

        return derived_path

    @return_future
    def get(self, callback):
        '''
        Gets an item based on the path.
        '''
        derived_path = self.context.request.url
        logger.debug('[{log_prefix}]: get.derived_path: {path}'.format(
            log_prefix=LOG_PREFIX, path=derived_path))
        callback(self.storage.get(self.result_key_for(derived_path)))

    def last_updated(self):
        '''
        This is used only when SEND_IF_MODIFIED_LAST_MODIFIED_HEADERS is eet.

        :return: A DateTime object
        :rettype: datetime.datetime
        '''
        derived_path = self.context.request.url
        timestamp_key = self.timestamp_key_for(derived_path)

        if self.exists(self.timestamp_key_for, derived_path):
            return self.storage.get(timestamp_key)

        return None

    def exists(self, key_for, path):
        '''
        Check if a key for a path exists in Memcache.

        :rettype: bool
        '''
        return self.storage.get(key_for(path)) is not None
