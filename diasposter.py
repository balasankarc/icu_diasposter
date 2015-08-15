#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 Balasankar C <balasankarc@autistici.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# .
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# .
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import diaspy
from lxml import etree
from datetime import datetime
import urllib2
import wget
import os
import shutil
import argparse


def getphotos(date):
    ''' Download photos from specified date '''
    text = {}
    day = date.day
    month = date.month
    year = date.year
    try:
        url = "http://chaluunion.com/day/%s/%s/%s" % (day, month, year)
        print "Getting Page"
        page = urllib2.urlopen(url)
        print "Connection established. Reading page"
        pagecontenthtml = page.read()
    except Exception, e:
        pagecontenthtml = e.partial
    print "Parsing"
    tree = etree.HTML(pagecontenthtml)
    exp = '//div[contains(@class,"post-type-photo")]/div[contains(@class,"post-content")]/a/img/@src'
    exp1 = '//div[contains(@class,"post-type-photo")]/div[contains(@class,"post-content")]/a/img/@alt'
    folder_name = './%s_%s_%s' % (day, month, year)
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    posts = tree.xpath(exp)
    credits = tree.xpath(exp1)
    for post in posts:
        pos = posts.index(post)
        fname = post[len(post) - post[::-1].index('/'):]
        text[fname] = credits[pos]
        if os.path.isfile(folder_name + "/uploaded/" + fname) or os.path.isfile(folder_name+"/"+fname):
            continue
        else:
            wget.download(post, out=folder_name)
    return text


def postphotos(date, podurl, uname, pwd, text):
    '''Post photost to diaspora pod'''
    day = date.day
    month = date.month
    year = date.year
    folder_name = '%s_%s_%s' % (day, month, year)       # Categorize posts per day
    c = diaspy.connection.Connection(pod=podurl, username=uname, password=pwd)
    c.login()
    stream = diaspy.streams.Stream(c)
    if not os.path.isdir(os.path.join(folder_name, "uploaded")):
        os.mkdir(os.path.join(folder_name, "uploaded"))
    filelist = os.listdir(folder_name)
    filelist.remove('uploaded')
    print filelist
    os.chdir("./" + folder_name)            # TODO: diaspy doesn't support relative paths, somehow.
    for filename in filelist:
        try:
            f = "./" + filename
            print f
            postid = stream._photoupload(filename=f)
            txt = text[filename] + "\n#icu"
            stream.post(photos=postid, text=txt)
            shutil.move(filename, 'uploaded/' + filename)   # Move uploaded posts so they won't be repeated
        except UnicodeEncodeError, e:
            print e
            shutil.move(filename, 'uploaded/' + filename)
        except Exception, e:
            print e
            continue
    os.chdir("../")                         # Change back to original directory after work

    # def cleanphotos(date):
    #   day = date.day
    #   month = date.month
    #   year = date.year
    #   folder_name = '%s_%s_%s' % (day, month, year)
    #   if os.path.isdir(os.path.join('./', folder_name, "uploaded")):
    #       shutil.rmtree(os.path.join('./', folder_name, "uploaded"))
    #   if len(os.listdir(folder_name)) == 0:
    #       os.rmtree(folder_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Publish ICU posts to Diaspora')
    parser.add_argument("pod", help="Specify the pod")
    parser.add_argument("username", help="Specify the username")
    parser.add_argument("password", help="Specify the password")
    args = parser.parse_args()
    pod = args.pod
    uname = args.username
    pwd = args.password
    print pod, uname, pwd
    date = datetime.now()
    print "Downloading Photos"
    text = getphotos(date)
    print "Uploading Photos"
    postphotos(date, pod, uname, pwd, text)
