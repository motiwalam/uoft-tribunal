import itertools
from more_itertools import take
from dataclasses import dataclass
from urllib.parse import urljoin

import lxml.html
import requests

@dataclass
class CaseReport:
    title: str
    blurb: str
    caselink: str
    summarylink: str | None

def extract_casereports_html(html):
    for article in html.cssselect('article'):
        title = article.cssselect('h2 a div')[0].text
        blurb, *_ = article.cssselect('.field--name-field-search-snippet') + [None]
        caselink = article.cssselect('.case-link.view-report-link')[0]
        summarylink, *_ = article.cssselect('.case-link.view-case-summary-link') + [None]
        
        report = CaseReport(
            title=title,
            blurb=blurb.text if blurb is not None else None,
            caselink=caselink.attrib['href'],
            summarylink=summarylink.attrib['href'] if summarylink is not None else None
        )
        
        yield report

def extract_casereports(url):
    resp = requests.get(url)
    html = lxml.html.fromstring(resp.text)
    baseurl = urljoin(url, '.')
    html.make_links_absolute(baseurl)
    yield from extract_casereports_html(html)

def pageurls(baseurl):
    for pagenum in itertools.count(0):
        yield baseurl + f'&page={pagenum}'

def all_casereports(baseurl, maxpages):
    return itertools.chain.from_iterable(
        extract_casereports(u)
        for u in take(maxpages, pageurls(baseurl))
    )



