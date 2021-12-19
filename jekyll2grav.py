#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import shutil
import frontmatter
import pytz
import re
import yaml

with open("config.yaml", "rt") as f:
    config = yaml.load(f)

print(repr(config))

SRCDIR = config["general"]["jekyll_dir"]
GRAVDIR = config["general"]["grav_dir"]

GRAV_TYPE = config["grav_defaults"]["item_type"]

# Translates Jekyll top level folders to GRAV (sorted)
FIRST_LEVEL = config["jekyll2grav_directories"]

DATEFORMAT_IN = "%Y-%m-%d %H:%M:%S %z"
DATEFORMAT_OUT = "%Y-%m-%d %H:%M:%S"

LOCAL_TIMEZONE = pytz.timezone(config["general"]["timezone"])

# Jekyll-tags that are considered to be categories, not tags
CATEGORIES = config["grav_categories"]


def replace_image(match):
    global target_path
    old_imgfile = match.group(2)
    old_imgfile = re.sub(r'\{\{ ?site\.url ?\}\}', SRCDIR, old_imgfile)
    img_name = os.path.basename(old_imgfile)
    new_imgfile = "{}/{}".format(target_path, img_name)
    print("Copying image {} to {} ...".format(old_imgfile, new_imgfile))
    shutil.copyfile(old_imgfile, new_imgfile)
    img_title = ""
    if match.group(3):
        img_title = match.group(3)
    new_string = "![{}]({}{})".format(match.group(1), img_name, img_title)
    return new_string


def convert_file(filepath):
    global target_path

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
        "category": list(config["grav_defaults"]["categories"]),
        "tag": list(config["grav_defaults"]["tags"]),
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

    # Generate new filepath
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
    target_path = newfilefolder

    # BODY HANDLING
    body = post.content

    # Handle highlights
    body = re.sub(r'\{% highlight( (\S+)) %\}', r'```\2', body)
    body = re.sub(r'\{% endhighlight %\}', r'```', body)

    # Handle assets?
    # Images OLD: ![alt text]({{ site.url }}/assets/blah.jpg "title")
    # Images NEW: ![alt text](blah.jpg "title")
    body = re.sub(r'!\[(.*?)\]\((.+?)( [\'"].+[\'"])?\)', replace_image, body)

    # FINISH BODY HANDLING
    post.content = body

    # Write to new location
    print("Writing {}...".format(newfilepath))
    frontmatter.dump(post, newfilepath)


# MAIN SCRIPT
num_converted = 0
for root, dirs, files in os.walk(SRCDIR):
    if root.split("/")[-1] in ["assets", "css", "images", "fonts", "javascripts", "_includes", "_layouts", SRCDIR]:
        continue
    for f in files:
        if f.split(".")[-1] != "md":
            continue
        filepath = "{}/{}".format(root, f)
        convert_file(filepath)
        num_converted += 1

print("Converted {} files.".format(num_converted))
