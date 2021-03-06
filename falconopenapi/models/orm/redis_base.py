# MIT License

# Copyright (c) 2016 Diogo Dutra

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from falconopenapi.router import Route
from falconopenapi.utils import build_validator
from falconopenapi.exceptions import ModelBaseError, JSONError
from falconopenapi.models.logger import ModelLoggerMetaMixin
from falconopenapi.models.orm.http import ModelOrmHttpMetaMixin
from falcon.errors import HTTPNotFound, HTTPMethodNotAllowed
from falcon import HTTP_CREATED, HTTP_NO_CONTENT, HTTP_METHODS
from falcon.responders import create_default_options
from jsonschema import ValidationError
from collections import defaultdict
from copy import deepcopy
from importlib import import_module
from concurrent.futures import ThreadPoolExecutor
import json
import os.path
import logging
import random


class ModelRedisBaseMeta(ModelLoggerMetaMixin, ModelOrmHttpMetaMixin):

    def __init__(cls, name, base_classes, attributes):
        cls._set_logger()

        if hasattr(cls, '__schema__'):
            cls._set_routes()
        else:
            cls._set_key()

    def _to_list(cls, objs):
        return objs if isinstance(objs, list) else [objs]

    def get_filters_names_key(cls):
        return cls.__key__ + '_filters_names'

    def get_key(cls, filters_names=None):
        if not filters_names or filters_names == cls.__key__:
            return cls.__key__

        return '{}_{}'.format(cls.__key__, filters_names)

    def get_instance_key(cls, instance, id_names=None):
        if isinstance(instance, dict):
            ids_ = [str(v) for v in ModelRedisBaseMeta.get_ids_values(cls, instance, id_names)]
        else:
            ids_ = [str(v) for v in cls.get_ids_values(instance, id_names)]

        return cls.__keys_separator__.decode().join(ids_).encode()

    def get_ids_values(cls, obj, keys=None):
        if keys is None:
            keys = cls.__id_names__

        return tuple([dict.get(obj, key) for key in sorted(keys)])



class ModelRedisBase(object):
    __session__ = None
    __authorizer__ = None
    __api__ = None
    __id_names__ = None

    def get_key(self, id_names=None):
        return type(self).get_instance_key(self, id_names)
