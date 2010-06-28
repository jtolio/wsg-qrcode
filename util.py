#!/usr/bin/env python
#
# see LICENSE file

from google.appengine.ext import db
import os

__all__ = ["generate_new_ident", "server_http_path_upper"]

_QRCODE_COUNTER = "qrc"
# discussion: it would be safe to increase the alphabet size to 38 using the
# characters . and -, as those two characters parse okay in URLs and are
# allowed characters in simple qrcode encoding. however, those are not standard
# characters in base38, so i'm just using base36
# this might be revisited
_BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _base36_encode_reversed_list(number):
    if not isinstance(number, (int, long)):
        raise TypeError("number must be integral")
    if number < 0:
        raise ValueError("number must be positive")
    if number < 36: return _BASE36_ALPHABET[number]
    data = []
    while number != 0:
        number, i = divmod(number, 36)
        data.append(_BASE36_ALPHABET[i])
    return data

def _base36_encode_reversed(number):
    return "".join(_base36_encode_reversed_list(number))

def _base36_encode(number):
    return "".join(reversed(_base36_encode_reversed_list(number)))

def _base36_decode(data):
    return int(data, 36)

class _DumbContentiousCounterClass(db.Model):
    """this class is totally stupid and sucks on app engine. single critical
    point and all that.
    """
    name = db.StringProperty(required=True)
    counter = db.IntegerProperty(required=True, default=0)

def generate_new_ident():
    """so, ideally, we generate idents that are as short as possible, but are
    unique. in other words, idents should be short to begin with and grow. this
    is easy if we just use some global counter and return it encoded in some
    large base, but global counters with atomic increment-and-return suck on app
    engine.

    a true solution would involve partitioning a counter into counter domains or
    something but that's hard.

    i'm returning least-significant-bit first to increase first-character
    entropy and hopefully balance binary lookup trees better
    """
    counter = _DumbContentiousCounterClass.get_or_insert(_QRCODE_COUNTER,
            name=_QRCODE_COUNTER)
    scope = {}
    def txn():
        counter.counter += 1
        scope[0] = counter.counter
        counter.put()
    db.run_in_transaction(txn)
    return _base36_encode_reversed(scope[0])

def server_http_path_upper():
    host = os.environ.get("HTTP_HOST").upper()
    if not host:
        host = os.environ["SERVER_NAME"].upper()
        if os.environ["SERVER_PORT"] != "80":
            host += ":%s" % os.environ["SERVER_PORT"]
    return "HTTP://" + host
