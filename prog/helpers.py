

import base64
import datetime
import random
import re
import string
import time
import urllib.request
import urllib.error
import urllib.parse
from enum import Enum

import cherrypy
import jinja2
import html

from prog.config import config

__all__ = ["deampify", "escapekeyword", "randomlink", "today", 'escapeascii', 'prettyday',
           'prettytime', 'makeList', 'canonicalUrl', 'getCurrentEditableUrl', 'getCurrentEditableUrlQuoted', 'sanitary',
           'byClicks', 'getCurrentEditableUrlQuoted', 'getSSOUsername']


def deampify(s):
    """Replace '&amp;'' with '&'."""
    return s.replace("&amp;", "&")


def escapeascii(s):
    return html.escape(s)


def randomlink(g_db):
    return random.choice([x for x in list(g_db.linksById.values()) if not x.isGenerative() and x.usage()])

def today():
    return datetime.date.today().toordinal()


def escapekeyword(kw):
    return urllib.parse.quote_plus(kw, safe="/")


def prettyday(d):
    if d < 10:
        return 'never'

    s = today() - d
    if s < 1:
        return 'today'
    elif s < 2:
        return 'yesterday'
    elif s < 60:
        return '%d days ago' % s
    else:
        return '%d months ago' % (s / 30)


def prettytime(t):
    if t < 100000:
        return 'never'

    dt = time.time() - t
    if dt < 24*3600:
        return 'today'
    elif dt < 2 * 24*3600:
        return 'yesterday'
    elif dt < 60 * 24*3600:
        return '%d days ago' % (dt / (24 * 3600))
    else:
        return '%d months ago' % (dt / (30 * 24*3600))


def makeList(s):
    if isinstance(s, str):
        return [s]
    elif isinstance(s, list):
        return s
    else:
        return list(s)


def canonicalUrl(url):
    if url:
        m = re.search(r'href="(.*)"', jinja2.utils.urlize(url))
        if m:
            return m.group(1)

    return url


def getDictFromCookie(cookiename):
    if cookiename not in cherrypy.request.cookie:
        return {}

    return dict(urllib.parse.parse_qsl(cherrypy.request.cookie[cookiename].value))


sanechars = string.ascii_lowercase + string.digits + "-."


def sanitary(s):
    s = s.lower()
    for a in s[:-1]:
        if a not in sanechars:
            return None

    if s[-1] not in sanechars and s[-1] != "/":
        return None

    return s


def byClicks(links):
    return sorted(links, key=lambda L: (-L.recentClicks, -L.totalClicks))


def getCurrentEditableUrl():
    redurl = config.urleditbase + cherrypy.request.path_info
    if cherrypy.request.query_string:
        redurl += "?" + cherrypy.request.query_string

    return redurl


def getCurrentEditableUrlQuoted():
    return urllib.parse.quote(getCurrentEditableUrl(), safe=":/")


def getSSOUsername(redirect=True):
    """
    If no SSO URL is specified then the 'testuser' is returned, otherwise returns an SSO username
    (or redirects to SSO to get it)
    :param redirect:
    :return: the SSO username
    """
    if config.url_sso is None or config.url_sso == 'None':
        return 'testuser'

    if cherrypy.request.base != config.urleditbase:
        if not redirect:
            return None
        if redirect is True:
            redirect = getCurrentEditableUrl()
        elif redirect is False:
            raise cherrypy.HTTPRedirect(redirect)

    if "issosession" not in cherrypy.request.cookie:
        if not redirect:
            return None
        if redirect is True:
            redirect = cherrypy.url(qs=cherrypy.request.query_string)

        raise cherrypy.HTTPRedirect(config.urlssoO + urllib.parse.quote(redirect, safe=":/"))

    sso = urllib.parse.unquote(cherrypy.request.cookie["issosession"].value)
    session = list(map(base64.b64decode, sso.split("-")))
    return session[0]
