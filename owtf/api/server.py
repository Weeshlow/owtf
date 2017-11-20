"""
owtf.api.server
~~~~~~~~~~~~~~~~~~~~~

"""

import logging

from flask import Flask

from owtf.dependency_management.dependency_resolver import BaseComponent
from owtf.api import urls
from owtf.lib.owtf_process import OWTFProcess


class FileServer(object):
    def start(self):
        try:
            self.application = tornado.web.Application(
                handlers=urls.get_file_server_handlers(),
                template_path=config.get_val('INTERFACE_TEMPLATES_DIR'),
                debug=False,
                gzip=True
            )
            self.application.Core = self.get_component("core")
            self.server = tornado.httpserver.HTTPServer(self.application)
            fileserver_port = int(config.get_val("FILE_SERVER_PORT"))
            fileserver_addr = config.get_val("SERVER_ADDR")
            self.server.bind(fileserver_port, address=fileserver_addr)
            tornado.options.parse_command_line(
                args=['dummy_arg', '--log_file_prefix=%s' % db.config.get('FILE_SERVER_LOG'), '--logging=info'])
            self.server.start(1)
            # 'self.manage_cron' is an instance of class 'tornado.ioloop.PeriodicCallback',
            # it schedules the given callback to be called periodically.
            # The callback is called every 2000 milliseconds.
            self.manager_cron = tornado.ioloop.PeriodicCallback(self.worker_manager.manage_workers, 2000)
            self.manager_cron.start()
            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            logging.error(e)
            self.clean_up()

    def clean_up(self):
        """Properly stop any tornado callbacks."""
        self.manager_cron.stop()
