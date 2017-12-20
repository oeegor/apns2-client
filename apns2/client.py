# coding: utf-8

import logging

from .notification import Notification
from .response import Response

from hyper.tls import init_context
from hyper import HTTP20Connection
import ujson


log = logging.getLogger("apns2")


MODE_PROD = "prod"
MODE_DEV = "dev"


class APNSClient(object):

    def __init__(self, mode: str, client_cert: str, password=None, proxy_host=None, proxy_port=None):
        if mode == MODE_PROD:
            self.host = "api.push.apple.com"
        elif mode == MODE_DEV:
            self.host = "api.development.push.apple.com"
        else:
            raise ValueError("invalid mode: {}".format(mode))

        self.conn = HTTP20Connection(
            host=self.host,
            port=443,
            secure=True,
            ssl_context=init_context(cert=client_cert, cert_password=password),
            proxy_host=proxy_host,
            proxy_port=proxy_port,
        )

    def get_headers(self, n: Notification, topic: str = None):
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if topic:
            headers["apns-topic"] = topic
        if n.apns_id:
            headers["apns-id"] = n.apns_id
        if n.collapse_id:
            headers["apns-collapse-id"] = n.collapse_id
        if n.priority:
            headers["apns-priority"] = n.priority
        if n.expiration:
            headers["apns-expiration"] = n.expiration
        return headers

    def push(self, n, device_token: str, topic: str = None) -> Response:
        url = "/3/device/{}".format(device_token)
        payload = n.payload.to_json()
        log.debug("Going to send payload: {}".format(payload))
        headers = self.get_headers(n, topic=topic)
        stream_id = self.conn.request(
            method="POST", url=url,
            body=payload, headers=headers,
        )
        apns_response = self.conn.get_response(stream_id=stream_id)

        apns_ids = apns_response.headers.get("apns-id")
        apns_id = apns_ids[0] if apns_ids else None

        response = Response(status_code=apns_response.status, apns_id=apns_id)

        if apns_response.status != 200:
            body = apns_response.read()
            apns_data = ujson.loads(body)
            response.timestamp = apns_data.get("timestamp")
            response.reason = apns_data["reason"]

        return response
