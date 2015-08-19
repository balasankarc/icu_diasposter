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
import urllib2
import wget
import os
import argparse


def getphotos(log):
    ''' Download photos'''
    text = {}
    try:
        url = "http://chaluunion.com/"
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
    folder_name = './images'
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    posts = tree.xpath(exp)
    credits = tree.xpath(exp1)
    for post in posts:
        print "\n", post
        pos = posts.index(post)
        fname = post[len(post) - post[::-1].index('/'):]
        text[fname] = credits[pos]
        if fname in log or fname in os.listdir(folder_name):
            print "Already downloaded"
            continue
        else:
            print "Downloading"
            wget.download(post, out=folder_name)
    return text


def postphotos(podurl, uname, pwd, text, log):
    '''Post photost to diaspora pod'''
    folder_name = 'images'
    imagefilelist = os.listdir(folder_name)
    filelist = [x for x in imagefilelist if x not in log]  # Skip the files already in log
    if len(filelist) == 0:
        return
    c = diaspy.connection.Connection(pod=podurl, username=uname, password=pwd)
    c.login()
    stream = diaspy.streams.Stream(c)
    os.chdir("./" + folder_name)  # TODO: diaspy doesn't support relative paths, somehow.
    for filename in filelist:
        if filename not in log:
            try:
                f = "./" + filename
                postid = stream._photoupload(filename=f)
                txt = text[filename] + "\n#icu"
                stream.post(photos=postid, text=txt)
                os.system("echo %s >> ../icu_poster.log" % filename)  # TODO use file operations
            except Exception, e:
                print e
                continue
    os.chdir("../")  # Change back to original directory after work


def clean():
    logfile = open('icu_poster.log', 'r')
    log = logfile.read()
    logfile.close()
    filelist = os.listdir("./images")
    print filelist
    for filename in filelist:
        if filename in log:
            os.remove("./images/%s" % filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Publish ICU posts to Diaspora')
    parser.add_argument("pod", help="Specify the pod")
    parser.add_argument("username", help="Specify the username")
    parser.add_argument("password", help="Specify the password")
    args = parser.parse_args()
    pod = args.pod
    uname = args.username
    pwd = args.password
    logfile = open('icu_poster.log', 'r')
    log = logfile.read()
    logfile.close()
    print "Downloading Photos"
    text = getphotos(log)
    print "Uploading Photos"
    postphotos(pod, uname, pwd, text, log)
    print "Cleaning Photos"
    clean()
