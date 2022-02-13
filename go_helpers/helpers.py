
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the Go Redirector. It uses short mnemonics as redirects to otherwise
long URLs. Few remember how to write in cursive, most people don't remember
common phone numbers, and just about everyone needs a way around bookmarks.
"""

__author__ = "Saul Pwanson <saul@pwanson.com>"
__credits__ = "Bill Booth, Bryce Bockman, treebird, Sean Smith, layertwo"

__all__ = ['deampify', 'escapeascii', 'today', 'escapekeyword', 'prettyday', 'prettytime',
           'makeList', 'canonicalUrl', 'getDictFromCookie', 'sanitary', 'byClicks',
           'getCurrentEditableUrl', 'getCurrentEditableUrlQuoted']

from config import cfg_urlEditBase
import datetime
import re
import string
import time
import urllib.request
import urllib.error
import urllib.parse
import cherrypy
import jinja2
import html


def deampify(s):
    """Replace '&amp;'' with '&'."""
    return s.replace("&amp;", "&")


def escapeascii(s):
    return html.escape(s)

"""
Moved into the LinkDatabase class.
def randomlink():
    return random.choice([x for x in list(g_db.linksById.values()) if not x.isGenerative() and x.usage()])
"""

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
    redurl = cfg_urlEditBase + cherrypy.request.path_info
    if cherrypy.request.query_string:
        redurl += "?" + cherrypy.request.query_string

    return redurl


def getCurrentEditableUrlQuoted():
    return urllib.parse.quote(getCurrentEditableUrl(), safe=":/")
