# thumbor-memcached

[![Build Status](https://travis-ci.org/thumbor-community/thumbor-memcached.svg)](https://travis-ci.org/thumbor-community/thumbor-memcached)

thumbor-memcached provides storages using memcached as a backend.

## Installing

Before installing, make sure both `memcached` and `libmemcached are installed and accessible to python.

    $ pip install thumbor-memcached

## Configuration

This config represents the options to store the incoming file.

```
# MEMCACHED STORAGE OPTIONS
MEMCACHE_STORAGE_SERVERS = ['localhost:5555']  # List of memcached servers to use for keys
STORAGE_EXPIRATION_SECONDS = 120  # Expiration of entries in the memcached storage
```

Thumbor also allows storing the processed image independent of the incoming image.

```
MEMCACHE_ITEM_SIZE_MAX = 1048576                          # 1024 * 1024 bytes which is the default item_size_max
MEMCACHE_SKIP_STORAGE_EXCEEDING_ITEM_SIZE_MAX = False     # Not skipping can throw TooBig error
RESULT_STORAGE_EXPIRATION_SECONDS = 120
RESULT_STORAGE_STORES_UNSAFE = True
```

## Usage

Using it is as simple as configuring it in your thumbor.conf file:

```
# thumbor.conf
STORAGE = 'thumbor_memcached.storage'
RESULT_STORAGE = 'thumbor_memcached.result_storage'
```

## Things to note

- `STORAGE` is used to cache the original incoming image, and `RESULT_STORAGE` is used to cache the processed thumbor image.
- By default Memcached has hard limit on `item_size_max` of [1024 * 1024 Bytes](https://github.com/memcached/memcached/commit/bed5f9bba1a02ae7176a9082cfadbd7a0d194bba). This can be changed on startup.
- The auto-discovery feature of AWS ElastiCache based Memcached is not part of the Memcached protocol standard, and hence it is not supported by the underlying `pylibmc` and `libmemcached` libraries.

## Versions

This projects uses the following versioning scheme:

`<thumbor major>.<memcached plugin major>.<memcached plugin minor>`
