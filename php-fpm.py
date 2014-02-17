#!/usr/bin/env python
# -*- encodig: utf-8 -*-
# pylint: disable=C0111,C0301,R0903

__VERSION__ = '0.1.1'

import requests
import json
import re
import subprocess

from blackbird.plugins import base

class ConcreteJob(base.JobBase):
    """
    This class is Called by "Executor".
    Get php-fpm's status,
    and send to specified zabbix server.
    """

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)

    def build_items(self):

         # ping item
        self._ping()

        # detect php-fpm version
        self._get_version()

        # get information from server-status
        self._get_status()

    def _enqueue(self, key, value):

        item = PhpfpmItem(
            key=key,
            value=value,
            host=self.options['hostname']
        )
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inserted to queue {key}:{value}'
            ''.format(key=item.key, value=item.value)
        )

    def _ping(self):
        """
        send ping item
        """

        self._enqueue('blackbird.php-fpm.ping', 1)
        self._enqueue('blackbird.php-fpm.version', __VERSION__)

    def _get_version(self):
        """
        detect php-fpm version

        $ php-fpm -v
        PHP N.N.N (fpm-fcgi) ...
        Copyright (c) ...
        Zend Engine ...
        """

        fpm_version = 'Unknown'

        try:
            output = subprocess.Popen([self.options['path'], '-v'],
                                      stdout=subprocess.PIPE).communicate()[0]
            match = re.match(r"^PHP (\S+)", output)
            if match:
                fpm_version = match.group(1)

        except OSError:
            self.logger.debug(
                'can not exec "{0} -v", failed to get php-fpm version'
                ''.format(self.options['path'])
            )

        self._enqueue('php-fpm.version', fpm_version)

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
            response = requests.get(url,
                                    timeout=self.options['timeout'],
                                    verify=False)
        except requests.ConnectionError:
            raise base.BlackbirdPluginError(
                'Can not connect to {url}'
                ''.format(url=url)
            )

        if response.status_code == 200:

            for (key, value) in json.loads(response.content).items():

                # ignore some keys
                if key == 'start time' or key == 'start since':
                    continue

                self._enqueue('php-fpm.stat[{0}]'.format(key.replace(' ', '_').lower()),
                              value)

        else:
            raise base.BlackbirdPluginError(
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
        self._data['key'] = self.key
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
            "port = integer(1, 65535, default=80)",
            "timeout = integer(0, 600, default=3)",
            "status_uri = string(default='/status')",
            "user = string(default=None)",
            "password = string(default=None)",
            "ssl = boolean(default=False)",
            "path = string(default='/usr/sbin/php-fpm')",
            "hostname = string(default={0})".format(self.detect_hostname()),
        )
        return self.__spec
