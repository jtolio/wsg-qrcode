#!/usr/bin/env python
#
# see LICENSE file

from google.appengine.ext import db
import urllib
from util import server_http_path_upper

class Owner(db.Model):
    user = db.UserProperty()

class QRCode(db.Model):
    ident = db.ByteStringProperty(required=True)
    owner = db.ReferenceProperty(Owner)

    action = db.IntegerProperty(required=True) # should be an action constant

    target_url = db.LinkProperty() # required if action == VISIT_URL_ACTION

    def url(self):
        return "%s/L/%s" % (server_http_path_upper(), self.ident)

    def url_encoded(self):
        return urllib.quote_plus(self.url())

    def error_correction_level(self):
        return "H"
