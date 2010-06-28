#!/usr/bin/env python
#
# see LICENSE file

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util as webapputil
import util, models, constants

class Request(webapp.RequestHandler):
    def write(self, template_name, data={}, ext="html"):
        if ext == "xml":
            self.response.headers["Content-Type"] = "text/xml; charset=utf-8"
        else:
            self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write(template.render(
                "templates/%s.%s" % (template_name, ext), data))
    def s404(self):
        self.error(404)
        self.write("404")
    def s500(self, error_msg=""):
        self.error(500)
        self.write("500", {"error_msg": error_msg})
    def get(self, *args, **kwargs): self.s404()
    def post(self, *args, **kwargs): self.s404()
    def put(self, *args, **kwargs): self.s404()
    def head(self, *args, **kwargs): self.s404()
    def options(self, *args, **kwargs): self.s404()
    def delete(self, *args, **kwargs): self.s404()
    def trace(self, *args, **kwargs): self.s404()
    def handle_exception(self, exception, debug_mode):
        if debug_mode:
            webapp.RequestHandler.handle_exception(self, exception, debug_mode)
        else:
            self.s500(str(exception))

class NewQRCode(Request):
    def post(self):
        url = self.request.get("url", "")
        if not url:
            return self.write("badqrcode", {"error_msg": "missing url!"})
        new_ident = util.generate_new_ident()
        try:
            qrcode = models.QRCode(ident=new_ident, key_name=new_ident,
                    action=constants.VISIT_URL_ACTION, target_url=url)
            qrcode.put()
        except Exception, e:
            return self.write("badqrcode", {"error_msg": str(e)})
        self.write("newqrcode", {"qrcode": qrcode})

class MainPage(Request):
    def get(self): self.write("main")

class CatchAll(Request): pass

class QRCodeRequest(Request):
    def get(self, code):
        qrcode = models.QRCode.get_by_key_name(code)
        if qrcode is None:
            return self.s404()
        if qrcode.action == constants.VISIT_URL_ACTION:
            if not qrcode.target_url: return self.s500("URL field missing!")
            return self.redirect(qrcode.target_url)
        else:
            return self.s500("unknown action: %d" % qrcode.action)

def main():
    webapputil.run_wsgi_app(webapp.WSGIApplication([
            (r'/L/([A-Z0-9]+)', QRCodeRequest),
            (r'/', MainPage),
            (r'/new', NewQRCode),
            (r'.*', CatchAll),
        ], debug=False))


if __name__ == '__main__':
    main()
