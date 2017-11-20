"""
owtf.api.handlers.targets
~~~~~~~~~~~~~~~~~~~~~~

"""

from flask import Flask, Blueprint
from flask_restful import Resource

from owtf.exceptions import InvalidTargetReference
from owtf.api.factory import app, api


targets = Blueprint('targets', __name__, url_prefix='/targets/')
api.init_app(targets)


class TargetConfigHandler(Resource):
    def get(self, target_id=None):
        try:
            # If no target_id, means /target is accessed with or without filters
            if not target_id:
                # Get all filter data here, so that it can be passed
                filter_data = dict(self.request.arguments)
                self.write(self.get_component("target").get_target_config_dicts(filter_data))
            else:
                self.write(self.get_component("target").get_target_config_by_id(target_id))
        except InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    def post(self, target_id=None):
        if (target_id) or (not self.get_argument("target_url", default=None)):  # How can one post using an id xD
            raise tornado.web.HTTPError(400)
        try:
            self.get_component("target").add_targets(dict(self.request.arguments)["target_url"])
            self.set_status(201)  # Stands for "201 Created"
        except exceptions.DBIntegrityException as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(409)
        except exceptions.UnresolvableTargetException as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(409)

    def put(self, target_id=None):
        return self.patch(target_id)

    def patch(self, target_id=None):
        if not target_id or not self.request.arguments:
            raise tornado.web.HTTPError(400)
        try:
            patch_data = dict(self.request.arguments)
            self.get_component("target").update_target(patch_data, ID=target_id)
        except InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)

    def delete(self, target_id=None):
        if not target_id:
            raise tornado.web.HTTPError(400)
        try:
            self.get_component("target").delete_target(ID=target_id)
        except InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)


class TargetConfigSearchHandler(Resource):
    def get(self):
        try:
            filter_data = dict(self.request.arguments)
            filter_data["search"] = True
            self.write(self.get_component("target").search_target_configs(filter_data=filter_data))
        except exceptions.InvalidParameterType:
            raise tornado.web.HTTPError(400)


class TargetSeverityChartHandler(Resource):
    def get(self):
        try:
            self.write(self.get_component("target").get_targets_by_severity_count())
        except exceptions.InvalidParameterType as e:
            raise tornado.web.HTTPError(400)


api.add_resource(TargetConfigHandler, '/?([0-9]+)?/?$')
api.add_resource(TargetConfigSearchHandler, '/search/?$')
api.add_resource(TargetSeverityChartHandler, '/metrics/?$')