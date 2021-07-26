#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import frontmatter
import pytz
import re

SRCDIR="jekyll"
GRAVDIR="grav/user/pages"

GRAV_TYPE="item"

# Translates Jekyll top level folders to GRAV (sorted)
FIRST_LEVEL = {
    "know-how": "03.know-how",
    "misc": "04.misc",
    "reviews": "05.reviews",
    "software": "06.software"
}

DATEFORMAT_IN="%Y-%m-%d %H:%M:%S %z"
DATEFORMAT_OUT="%Y-%m-%d %H:%M:%S"

LOCAL_TIMEZONE=pytz.timezone("Europe/Berlin")

# Jekyll-tags that are considered to be categories, not tags
CATEGORIES=["know-how", "development", "review", "hacking", "hardware", "software", "miscellaneous"]

def convert_file(filepath):
    print("Loading {}...".format(filepath))
    post = frontmatter.load(filepath)

    # work metadata like post is a dict (post["title"])
    if "language" in post:
        language = post["language"]
    else:
        language = "en"

    date_created = datetime.strptime(post["created"], DATEFORMAT_IN).astimezone(LOCAL_TIMEZONE)
    date_updated = datetime.strptime(post["updated"], DATEFORMAT_IN).astimezone(LOCAL_TIMEZONE)

    post["date"] = date_created.strftime(DATEFORMAT_OUT)
    post["modified_date"] = date_created.strftime(DATEFORMAT_OUT)


    post["taxonomy"] = {
        "category": ["wiki"],
        "tag": []
    }

    for t in post["tags"]:
        if t in CATEGORIES:
            post["taxonomy"]["category"].append(t)
        else:
            post["taxonomy"]["tag"].append(t)

    post["visible"] = True

    for x in ["language", "layout", "created", "tags", "toc", "updated"]:
        if x in post:
            del post[x]

    print(repr(post.metadata))

    # Handle highlights
    body = post.content
    body = re.sub(r'\{% highlight( (\S+)) %\}', r'```\2', body)
    body = re.sub(r'\{% endhighlight %\}', r'```', body)
    post.content = body

    # Handle assets?


    # Generate new filepath and write
    pathparts = filepath.split("/")
    pathparts[0] = GRAVDIR
    pathparts[1] = FIRST_LEVEL[pathparts[1]]
    filename = pathparts[-1]
    newfoldername = filename[11:-3]    # strip date and extension
    pathparts[-2] = newfoldername
    pathparts[-1] = "{}.{}.md".format(GRAV_TYPE, language)
    newfilefolder = "/".join(pathparts[:-1])
    newfilepath = "/".join(pathparts)
    print("Creating {}...".format(newfilefolder))
    os.makedirs(newfilefolder, exist_ok=True)
    print("Writing {}...".format(newfilepath))
    frontmatter.dump(post, newfilepath)

for root, dirs, files in os.walk(SRCDIR):
    if root.split("/")[-1] in ["assets", "css", "images", "fonts", "javascripts", "_includes", "_layouts", SRCDIR]:
        continue
    for f in files:
        if f.split(".")[-1] != "md":
            continue
        filepath = "{}/{}".format(root, f)
        convert_file(filepath)
