#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the Go Redirector. It uses short mnemonics as redirects to otherwise
long URLs. Few remember how to write in cursive, most people don't remember
common phone numbers, and just about everyone needs a way around bookmarks.
"""

__author__ = "Saul Pwanson <saul@pwanson.com>"
__credits__ = "Bill Booth, Bryce Bockman, treebird, Sean Smith, layertwo"

from go_helpers.config import *
from go_helpers.helpers import *
from go_helpers.sso import getSSOUsername
import datetime
import os
import pickle
import random
import re
import string
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import cherrypy
import jinja2
import shutil



class Root:
    def redirect(self, url, status=307):
        cherrypy.response.status = status
        cherrypy.response.headers["Location"] = url

    def undirect(self):
        raise cherrypy.HTTPRedirect(cherrypy.request.headers.get("Referer", "/"))

    def notfound(self, msg):
        return env.get_template("notfound.html").render(message=msg)

    def redirectIfNotFullHostname(self, scheme=None):
        if scheme is None:
            scheme = cherrypy.request.scheme

        # redirect to our full hostname to get the user's cookies
        if cherrypy.request.scheme != scheme or cherrypy.request.base.find(cfg_hostname) < 0:
            fqurl = scheme + "://" + cfg_hostname
            fqurl += cherrypy.request.path_info
            if cherrypy.request.query_string:
                fqurl += "?" + cherrypy.request.query_string
            raise cherrypy.HTTPRedirect(fqurl)

    def redirectToEditLink(self, **kwargs):
        if "linkid" in kwargs:
            url = "/_edit_/%s" % kwargs["linkid"]
            del kwargs["linkid"]
        else:
            url = "/_add_"

        return self.redirect(url + "?" + urllib.parse.urlencode(kwargs))

    def redirectToEditList(self, listname, **kwargs):
        baseurl = "/_editlist_/%s?" % escapekeyword(listname)
        return self.redirect(baseurl + urllib.parse.urlencode(kwargs))

    @cherrypy.expose
    def robots_txt(self):
        # Specifically for the internal GSA
        return open("robots.txt").read()

    @cherrypy.expose
    def favicon_ico(self):
        cherrypy.response.headers["Cache-control"] = "max-age=172800"
        return self.redirect(cfg_urlFavicon, status=301)

    @cherrypy.expose
    def lucky(self):
        luckylink = random.choice(g_db.getNonFolders())
        luckylink.clicked()
        return self.redirect(deampify(luckylink.url()))

    @cherrypy.expose
    def index(self, **kwargs):
        self.redirectIfNotFullHostname()

        if "keyword" in kwargs:
            return self.redirect("/" + kwargs["keyword"])

        return env.get_template('index.html').render(now=today())

    @cherrypy.expose
    def default(self, *rest, **kwargs):
        self.redirectIfNotFullHostname()

        keyword = rest[0]
        rest = rest[1:]

        forceListDisplay = False

        if keyword[0] == ".":  # force list page instead of redirect
            if keyword == ".me":
                username = getSSOUsername()
                self.redirect("." + username)
            forceListDisplay = True
            keyword = keyword[1:]

        if rest:
            keyword += "/"
        elif forceListDisplay and cherrypy.request.path_info[-1] == "/":
            # allow go/keyword/ to redirect to go/keyword but go/.keyword/
            #  to go to the keyword/ index
            keyword += "/"

        # try it as a list
        try:
            ll = g_db.getList(keyword, create=False)
        except InvalidKeyword as e:
            return self.notfound(str(e))

        if not ll:  # nonexistent list
            # check against all special cases
            matches = []
            for R in list(g_db.regexes.values()):
                matches.extend([(R, L, genL) for L, genL in R.matches(keyword)])

            if not matches:
                kw = sanitary(keyword)
                if not kw:
                    return self.notfound("No match found for '%s'" % keyword)

                # serve up empty fake list
                return env.get_template('list.html').render(L=ListOfLinks(0), keyword=kw)
            elif len(matches) == 1:
                R, L, genL = matches[0]  # actual regex, generated link
                R.clicked()
                L.clicked()
                return self.redirect(deampify(genL.url()))
            else:  # len(matches) > 1
                LL = ListOfLinks(-1)  # -1 means non-editable
                LL.links = [genL for R, L, genL in matches]
                return env.get_template('list.html').render(L=LL, keyword=keyword)

        listtarget = ll.getDefaultLink()

        if listtarget and not forceListDisplay:
            ll.clicked()
            listtarget.clicked()
            return self.redirect(deampify(listtarget.url()))

        tmplList = env.get_template('list.html')
        return tmplList.render(L=ll, keyword=keyword)

    @cherrypy.expose
    def special(self):
        LL = ListOfLinks(-1)
        LL.name = "Smart Keywords"
        LL.links = g_db.getSpecialLinks()

        env.globals['g_db'] = g_db
        return env.get_template('list.html').render(L=LL, keyword="special")

    @cherrypy.expose
    def _login_(self, redirect=""):
        if redirect:
            return self.redirect(redirect)
        return self.undirect()

    @cherrypy.expose
    def me(self):
        username = getSSOUsername()
        return self.redirect(username)

    @cherrypy.expose
    def _link_(self, linkid):
        link = g_db.getLink(linkid)
        if link:
            link.clicked()
            return self.redirect(link.url(), status=301)

        cherrypy.response.status = 404
        return self.notfound("Link %s does not exist" % linkid)

    @cherrypy.expose
    def _add_(self, *args, **kwargs):
        # _add_/tag1/tag2/tag3
        link = Link()
        link.lists = [g_db.getList(listname, create=False) or ListOfLinks(0, listname) for listname in args]
        return env.get_template("editlink.html").render(L=link, returnto=(args and args[0] or None), **kwargs)

    @cherrypy.expose
    def _edit_(self, linkid, **kwargs):
        link = g_db.getLink(linkid)
        if link:
            return env.get_template("editlink.html").render(L=link, **kwargs)

        # edit new link
        return env.get_template("editlink.html").render(L=Link(), **kwargs)

    @cherrypy.expose
    def _editlist_(self, keyword, **kwargs):
        K = g_db.getList(keyword, create=False)
        if not K:
            K = ListOfLinks()
        return env.get_template("list.html").render(L=K, keyword=keyword)

    @cherrypy.expose
    def _setbehavior_(self, keyword, **kwargs):
        K = g_db.getList(keyword, create=False)

        if "behavior" in kwargs:
            K._url = kwargs["behavior"]

        return self.redirectToEditList(keyword)

    @cherrypy.expose
    def _delete_(self, linkid, returnto=""):

        g_db.deleteLink(g_db.getLink(linkid))

        return self.redirect("/." + returnto)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def _modify_(self, **kwargs):
        username = getSSOUsername()

        linkid = kwargs.get("linkid", "")
        title = escapeascii(kwargs.get("title", ""))
        lists = kwargs.get("lists", [])
        url = kwargs.get("url", "")
        otherlists = kwargs.get("otherlists", "")

        returnto = kwargs.get("returnto", "")

        # remove any whitespace/newlines in url
        url = "".join(url.split())

        if type(lists) not in [tuple, list]:
            lists = [lists]

        lists.extend(otherlists.split())

        if linkid:
            link = g_db.getLink(linkid)
            if link._url != url:
                g_db._changeLinkUrl(link, url)
            link.title = title

            newlistset = []
            for listname in lists:
                if "{*}" in url:
                    if listname[-1] != "/":
                        listname += "/"
                try:
                    newlistset.append(g_db.getList(listname, create=True))
                except:
                    return self.redirectToEditLink(error="invalid keyword '%s'" % listname, **kwargs)

            for LL in newlistset:
                if LL not in link.lists:
                    LL.addLink(link)

            for LL in [x for x in link.lists]:
                if LL not in newlistset:
                    LL.removeLink(link)
                    if not LL.links:
                        g_db.deleteList(LL)

            link.lists = newlistset

            link.editedBy(username)

            g_db.save()

            return self.redirect("/." + returnto)

        if not lists:
            return self.redirectToEditLink(error="delete links that have no lists", **kwargs)

        if not url:
            return self.redirectToEditLink(error="URL required", **kwargs)

        # if url already exists, redirect to that link's edit page
        if url in g_db.linksByUrl:
            link = g_db.linksByUrl[url]

            # only modify lists; other fields will only be set if there
            # is no original

            combinedlists = set([x.name for x in link.lists]) | set(lists)

            fields = {'title': link.title or title,
                      'lists': " ".join(combinedlists),
                      'linkid': str(link.linkid)
                      }

            return self.redirectToEditLink(error="found identical existing URL; confirm changes and re-submit", **fields)

        link = g_db.addLink(lists, url, title, username)

        g_db.save()
        return self.redirect("/." + returnto)

    @cherrypy.expose
    def _internal_(self, *args, **kwargs):
        # check, toplinks, special, dumplist
        return env.get_template(args[0] + ".html").render(**kwargs)

    @cherrypy.expose
    def toplinks(self, n="100"):
        return env.get_template("toplinks.html").render(n=int(n))

    @cherrypy.expose
    def variables(self):
        return env.get_template("variables.html").render()

    @cherrypy.expose
    def help(self):
        return env.get_template("help.html").render()

    @cherrypy.expose
    def _override_vars_(self, **kwargs):
        cherrypy.response.cookie["variables"] = urllib.parse.urlencode(kwargs)
        cherrypy.response.cookie["variables"]["max-age"] = 10 * 365 * 24 * 3600

        return self.redirect("variables")

    @cherrypy.expose
    def _set_variable_(self, varname="", value=""):
        if varname and value:
            g_db.variables[varname] = value
            g_db.save()

        return self.redirect("/variables")


env = jinja2.Environment(loader=jinja2.FileSystemLoader("./html"))


def main():
    cherrypy.config.update({'server.socket_host': '::',
                            'server.socket_port': cfg_port,
                            'request.query_string_encoding': "latin1",
                            })

    cherrypy.https = s = cherrypy._cpserver.Server()
    if cfg_sslEnabled:
        s.socket_host = '::'
        s.socket_port = 443
        s.ssl_certificate = cfg_sslCertificate
        s.ssl_private_key = cfg_sslPrivateKey
        s.subscribe()

    # checkpoint the database every 60 seconds
    cherrypy.process.plugins.BackgroundTask(60, lambda: g_db.save()).start()

    file_path = os.getcwd().replace("\\", "/")
    conf = {'/images': {"tools.staticdir.on": True, "tools.staticdir.dir": file_path + "/images"},
            '/css': {"tools.staticdir.on": True, "tools.staticdir.dir": file_path + "/css"},
            '/js': {"tools.staticdir.on": True, "tools.staticdir.dir": file_path + "/js"}}
    print("Cherrypy conf: %s" % conf)
    cherrypy.quickstart(Root(), "/", config=conf)


if __name__ == "__main__":

    g_db = LinkDatabase.load()

    if "import" in sys.argv:
        g_db._import("newterms.txt")

    elif "export" in sys.argv:
        g_db._export("newterms.txt")

    elif "dump" in sys.argv:
        g_db._dump(sys.stdout)

    else:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("./html"))
        env.filters['time_t'] = prettytime
        env.filters['int'] = int
        env.filters['escapekeyword'] = escapekeyword

        env.globals["enumerate"] = enumerate
        env.globals["sample"] = random.sample
        env.globals["len"] = len
        env.globals["min"] = min
        env.globals["str"] = str
        env.globals["list"] = makeList
        env.globals.update(globals())
        main()
