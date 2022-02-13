#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the Go Redirector. It uses short mnemonics as redirects to otherwise
long URLs. Few remember how to write in cursive, most people don't remember
common phone numbers, and just about everyone needs a way around bookmarks.
"""

__author__ = "Saul Pwanson <saul@pwanson.com>"
__credits__ = "Bill Booth, Bryce Bockman, treebird, Sean Smith, layertwo"

from go_helpers.config import cfg_urlSSO, cfg_urlEditBase
from go_helpers.helpers import getCurrentEditableUrl
import base64
import string
import urllib.request
import urllib.error
import urllib.parse
import cherrypy

__all__ = ['getSSOUsername']

def getSSOUsername(redirect=True):
    """
    If no SSO URL is specified then the 'testuser' is returned, otherwise returns an SSO username
    (or redirects to SSO to get it)
    :param redirect:
    :return: the SSO username
    """
    if cfg_urlSSO is None or cfg_urlSSO == 'None':
        return 'testuser'

    if cherrypy.request.base != cfg_urlEditBase:
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

        raise cherrypy.HTTPRedirect(cfg_urlSSO + urllib.parse.quote(redirect, safe=":/"))

    sso = urllib.parse.unquote(cherrypy.request.cookie["issosession"].value)
    session = list(map(base64.b64decode, string.split(sso, "-")))
    return session[0]
