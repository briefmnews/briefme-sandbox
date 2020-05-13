import re
import tldextract
import urllib.request, urllib.error, urllib.parse

from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from bs4.builder._htmlparser import BeautifulSoupHTMLParser
from bs4.dammit import EntitySubstitution
from difflib import SequenceMatcher

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def handle_entityref(self, name):
    """To fix the semicolon add on unknown entities"""
    character = EntitySubstitution.HTML_ENTITY_TO_CHARACTER.get(name)

    if character is not None:
        data = character
    else:
        data = "&{name}".format(name=name)

    self.handle_data(data)


_NODE_CONVERSIONS = {
    "head": lambda node: "",
    "p": lambda node: "%s\n" % _convert(node),
    "text": lambda node: str(node),
    "li": lambda node: "* %s\n" % _convert(node),
    "a": lambda node: _convert_anchor(node),
}


def _convert_anchor(a):
    # Drop some attributes set by Google
    for attr in ("id", "class"):
        del a[attr]

    href = a.get("href", "").strip()

    if not href:
        return _convert(a)

    # Google gives us links served from a Google domain, with the real link
    # under the "q" parameter of the querystring
    if "?" in href:
        url = urlparse(href)
        query = parse_qs(url.query)
        q = query.get("q")

        if q:
            href = q[0]

    try:
        title = get_page_title(href)

    except Exception:
        title = ""

    a["href"] = href
    a["title"] = title

    return str(a)


def _convert(node):
    result = ""

    for child in node.children:
        tag = child.name if child.name is not None else "text"

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "br", "hr"):
            tag = "p"

        result += _NODE_CONVERSIONS.get(tag, _convert)(child)

    return result


def dehtmlify(html_text):
    BeautifulSoupHTMLParser.handle_entityref = handle_entityref
    soup = BeautifulSoup(html_text, "lxml")

    return _convert(soup)


def html_paragraphify(text):
    res = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        res.append("<p>%s</p>" % line)

    return res


def apply_func_to_dict(d, keys, func):
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            new_dict[k] = apply_func_to_dict(v, keys, func)
        elif isinstance(v, list):
            new_dict[k] = []
            for i in v:
                if isinstance(i, str):
                    if k in keys:
                        i = func(i)
                    new_dict[k].append(i)
                else:
                    new_dict[k].append(apply_func_to_dict(i, keys, func))
        else:
            if k in keys:
                v = func(v)
            new_dict[k] = v
    return new_dict


def add_target_blank_to_links(text):
    soup = BeautifulSoup(text, "html.parser")

    for link in soup.find_all("a"):
        link["target"] = "_blank"
        link["rel"] = "noopener"

    text = soup.body.decode_contents() if soup.body is not None else str(soup)
    return text


def get_page_title(url):
    """To get the page title

    @param url:  The url
    @type url:  str

    @return:  The title formatted
    @rtype :  str
    """
    url_validator = URLValidator()

    try:
        url_validator(url)
    except ValidationError:
        return "Url non valide"

    headers = {"User-Agent": "Mozilla/54.0"}
    url_request = urllib.request.Request(url, headers=headers)
    request = urllib.request.urlopen(url_request)

    if "text/html" in request.headers.get_content_type():
        soup = BeautifulSoup(request, "lxml")
        title = soup.title.text.strip()
    else:
        title = ""

    ext = tldextract.extract(url)
    domain = ext.domain

    if "|" in title:
        title = _format_title(title, domain, separator="|")
    else:
        title = _format_title(title, domain)

    multispace = re.compile(r"\s+", flags=re.UNICODE)

    title = multispace.sub(" ", title)

    return title


def _format_title(title, domain, separator="-"):

    title = title.strip()
    words = [word.strip() for word in title.split(" {} ".format(separator))]

    if separator not in title:
        name = _get_name(domain)
        title_formatted = "{name} | {title}".format(name=name, title=title)

    elif _get_name(domain) in words:
        name = _get_name(domain)
        words.remove(name)
        title = " | "
        title = title.join(words)
        title_formatted = "{name} | {title}".format(name=name, title=title)

    else:
        name = words.pop()
        matcher = SequenceMatcher(None, name.replace(" ", ""), domain)
        ratio = matcher.ratio()

        if ratio > 0.6:
            rest = " | ".join(words)
            title_formatted = "{name} | {rest}".format(name=name, rest=rest)
        else:
            title_formatted = title.replace(" - ", " | ")

    return title_formatted


def _get_name(domain):
    return domain
