# coding: utf-8

import ujson


MAX_PAYLOAD_LENGTH = 2048


class PayloadTooLargeError(Exception):
    def __init__(self, payload_size):
        super().__init__()
        self.payload_size = payload_size


class PayloadAlert(object):
    def __init__(
        self, body=None, action_loc_key=None, loc_key=None,
        loc_args=None, launch_image=None, title=None, title_loc_key=None,
        title_loc_args=None
    ):
        super().__init__()
        self.body = body
        self.title = title
        self.action_loc_key = action_loc_key
        self.loc_key = loc_key
        self.loc_args = loc_args
        self.launch_image = launch_image
        self.title_loc_key = title_loc_key
        self.title_loc_args = title_loc_args

    def dict(self):
        d = {}
        if self.body:
            d['body'] = self.body
        if self.action_loc_key:
            d['action-loc-key'] = self.action_loc_key
        if self.loc_key:
            d['loc-key'] = self.loc_key
        if self.loc_args:
            d['loc-args'] = self.loc_args
        if self.launch_image:
            d['launch-image'] = self.launch_image
        if self.title_loc_key:
            d['title-log-key'] = self.title_loc_key
        if self.title_loc_args:
            d['title-loc-args'] = self.title_loc_args

        return d


class Payload(object):
    def __init__(
        self, alert=None, badge=None, sound=None, category=None,
        custom=None, content_available=False, mutable_content=False,
    ):
        super().__init__()
        self.alert = alert
        self.badge = badge
        self.sound = sound
        self.category = category
        self.custom = custom or {}
        self.content_available = content_available
        self.mutable_content = mutable_content

    def dict(self):
        d = {}
        if self.alert:
            # Alert can be either a string or a PayloadAlert
            # object
            if isinstance(self.alert, PayloadAlert):
                d['alert'] = self.alert.dict()
            else:
                d['alert'] = self.alert
        if self.sound:
            d['sound'] = self.sound
        if self.badge is not None:
            d['badge'] = int(self.badge)
        if self.category:
            d['category'] = self.category

        if self.content_available:
            d.update({'content-available': 1})

        if self.mutable_content:
            d.update({'mutable-content': 1})

        d = {'aps': d}
        d.update(self.custom)
        return d

    def __repr__(self):
        attrs = ("alert", "badge", "sound", "category", "custom")
        args = ", ".join(["%s=%r" % (n, getattr(self, n)) for n in attrs])
        return "%s(%s)" % (self.__class__.__name__, args)

    def to_json(self) -> bytes:
        return ujson.dumps(self.dict())


class Notification(object):

    def __init__(
        self, payload: Payload,
        apns_id=None, collapse_id=None,
        expiration=None, priority=None,
    ):
        super().__init__()
        # An optional canonical UUID that identifies the notification. The canonical
        # form is 32 lowercase hexadecimal digits, displayed in five groups separated
        # by hyphens in the form 8-4-4-4-12. An example UUID is as follows:
        # 	123e4567-e89b-12d3-a456-42665544000
        # If you don't set this, a new UUID is created by APNs and returned in the
        # response.
        self.apns_id = apns_id

        # A string which allows a notification to be replaced by a new notification
        # with the same CollapseID.
        self.collapse_id = collapse_id

        # An optional time at which the notification is no longer valid and can be
        # discarded by APNs. If this value is in the past, APNs treats the
        # notification as if it expires immediately and does not store the
        # notification or attempt to redeliver it. If this value is left as the
        # default (ie, Expiration.IsZero()) an expiration header will not added to the
        # http request.
        self.expiration = expiration

        # The priority of the notification. Specify ether apns.PriorityHigh (10) or
        # apns.PriorityLow (5) If you don't set this, the APNs server will set the
        # priority to 10.
        self.priority = priority

        # A byte array containing the JSON-encoded payload of this push notification.
        # Refer to "The Remote Notification Payload" section in the Apple Local and
        # Remote Notification Programming Guide for more info.
        self.payload = payload
