# thumbor-memcached

[![Build Status](https://travis-ci.org/thumbor-community/thumbor-memcached.svg)](https://travis-ci.org/thumbor-community/thumbor-memcached)

thumbor-memcached provides storages using memcached as a backend.

## Installing

Before installing, make sure both `memcached` and `libmemcached are installed and accessible to python.

## Configuration

```
# MEMCACHED STORAGE OPTIONS
MEMCACHE_STORAGE_SERVERS=['localhost:5555']  # List of memcached servers to use for keys
STORAGE_EXPIRATION_SECONDS=120  # Expiration of entries in the memcached storage
```

## Usage

Using it is as simple as configuring it in your thumbor.conf file:

```
# thumbor.conf
STORAGE = 'thumbor_memcached.storage'
```

## Versions

This projects uses the following versioning scheme:

`<thumbor major>.<memcached plugin major>.<memcached plugin minor>`
