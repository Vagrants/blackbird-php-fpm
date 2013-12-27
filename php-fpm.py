#!/usr/bin/env python
# -*- encodig: utf-8 -*-
"""
Get the php-fpm's "status"
"""

import requests
import json

from blackbird.plugins import base

class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executer".
    Get php-fpm's status,
    and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def _enqueue(self, item):
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=item.key, value=item.value)
        )

    def looped_method(self):

        # get information from server-status
        self._get_status()

    def _get_status(self):
        """
        get php-fpm status.
        only support json format.
        """

        if self.options['ssl']:
            method = 'https://'
        else:
            method = 'http://'
        url = (
            '{method}{host}:{port}{uri}?json'
            ''.format(
                method=method,
                host=self.options['host'],
                port=self.options['port'],
                uri=self.options['status_uri']
            )
        )

        try:
            response = requests.get(url)
        except requests.ConnectionError:
            self.logger.error(
                'Can not connect to {url}'
                ''.format(url=url)
            )
            return

        if response.status_code == 200:

            for (key, value) in json.loads(response.content).items():
                item = PhpfpmItem(
                    key=key.replace(' ', '_').lower(),
                    value=value,
                    host=self.options['hostname']
                )
                self._enqueue(item)

        else:
            self.logger.error(
                'Can not get status from {url} status:{status}'
                ''.format(url=url, status=response.status_code)
            )


class PhpfpmItem(base.ItemBase):
    """
    Enqued item.
    """

    def __init__(self, key, value, host):
        super(PhpfpmItem, self).__init__(key, value, host)

        self._data = {}
        self._generate()

    @property
    def data(self):
        return self._data

    def _generate(self):
        self._data['key'] = 'php-fpm.stat[{0}]'.format(self.key)
        self._data['value'] = self.value
        self._data['host'] = self.host
        self._data['clock'] = self.clock


class Validator(base.ValidatorBase):

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        """
        "user" and "password" in spec are
        for BASIC and Digest authentication.
        """
        self.__spec = (
            "[{0}]".format(__name__),
            "host = string(default='127.0.0.1')",
            "port = integer(0, 65535, default=80)",
            "status_uri = string(default='/status')",
            "user = string(default=None)",
            "password = string(default=None)",
            "ssl = boolean(default=False)",
            "hostname = string(default={0})".format(self.gethostname()),
        )
        return self.__spec
