import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # noqa: F401,F403

# For a project page this is https://yourname.github.io/yourrepo
# For a user page (repo named yourname.github.io) drop the path part.
SITEURL = "https://sgolev.github.io"
RELATIVE_URLS = False

FEED_ALL_RSS = "feeds/all.rss.xml"
FEED_ALL_ATOM = "feeds/all.atom.xml"

GOATCOUNTER_CODE = "sgolev"

DELETE_OUTPUT_DIRECTORY = True
