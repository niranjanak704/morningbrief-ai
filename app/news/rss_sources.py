"""
RSS feed sources for The Hindu.

The Hindu publishes a section-level RSS feed for most of its site sections,
using the pattern:

    https://www.thehindu.com/<section-path>/feeder/default.rss

For example, the Editorial section's feed lives at:
    https://www.thehindu.com/opinion/editorial/feeder/default.rss

IMPORTANT (please read):
This project's sandbox could not reach thehindu.com directly to test every
single URL below end-to-end, but the "<section>/feeder/default.rss" pattern
itself IS confirmed live (verified against the Editorial feed above at the
time this project was built).

Before you rely on this project daily, run:
    python -m app.news.collector
once, with an internet connection, and check the console output. If any
feed below returns zero articles or an error, open the matching section
page on https://www.thehindu.com in your browser, look for the RSS icon
(usually in the page footer or via view-source search for "feeder"), and
update the URL here. This file is the ONLY place you need to edit.
"""

RSS_FEEDS = {
    "NATIONAL": "https://www.thehindu.com/news/national/feeder/default.rss",
    "INTERNATIONAL": "https://www.thehindu.com/news/international/feeder/default.rss",
    "BUSINESS": "https://www.thehindu.com/business/feeder/default.rss",
    "SCI-TECH": "https://www.thehindu.com/sci-tech/feeder/default.rss",
    "SPORT": "https://www.thehindu.com/sport/feeder/default.rss",
    "EDITORIAL": "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
}
