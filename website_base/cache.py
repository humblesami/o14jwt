import odoo
import werkzeug
from odoo.http import root, DisableCacheMiddleware  # , Response, HttpRequest

class NewsDisableCacheMiddleware(DisableCacheMiddleware):
    def __call__(self, environ, start_response):
        def start_wrapped(status, headers):
            req = werkzeug.wrappers.Request(environ)
            root.setup_session(req)
            found_at = 0
            for header in headers:
                if header[0].lower() == 'cache-control':
                    headers.pop(found_at)
                    break
                found_at += 1
            start_response(status, headers)
        return self.app(environ, start_wrapped)


odoo.http.DisableCacheMiddleware.__call__ = NewsDisableCacheMiddleware.__call__
# odoo.http.HttpRequest.make_response = NewsHttpRequest.make_response
