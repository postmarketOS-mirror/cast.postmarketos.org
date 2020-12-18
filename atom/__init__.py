from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, \
    register_namespace
from flask import Response


class FeedEntry:
    def __init__(self, content, title, url, content_type, updated, files,
                 chapters):
        self.content = content
        self.title = title
        self.url = url
        self.content_type = content_type
        self.updated = updated
        self.files = files
        self.chapters = chapters

    def generate(self, feed):
        top = SubElement(feed, 'item')

        title_elem = SubElement(top, "title")
        title_elem.text = self.title

        id_elem = SubElement(top, 'guid')
        id_elem.set('isPermaLink', "false")
        id_elem.text = self.url

        updated_elem = SubElement(top, 'pubDate')
        updated_elem.text = self.updated.isoformat()

        link_elem = SubElement(top, 'link')
        link_elem.text = self.url

        for file in self.files:
            enc_elem = SubElement(top, 'enclosure')
            enc_elem.set('url', file[1])
            enc_elem.set('type', file[0])
            enc_elem.set('length', str(file[2]))

        it_et = SubElement(top, 'itunes:episodeType')
        it_et.text = 'full'
        it_author = SubElement(top, 'itunes:author')
        it_author.text = 'postmarketOS'
        it_ex = SubElement(top, 'itunes:explicit')
        it_ex.text = 'no'

        chapters = SubElement(top, 'podcast:chapters')
        chapters.set('url', self.chapters)
        chapters.set('type', "application/json+chapters")

        content_elem = SubElement(top, 'content')
        content_elem.set('type', self.content_type)
        content_elem.text = self.content
        content_elem = SubElement(top, 'itunes:summary')
        content_elem.text = self.content


class AtomFeed:
    def __init__(self, title=None, url=None, author=None, icon=None,
                 feed_url=None, cover_url=None, summary=None):
        self.title = title
        self.url = url
        self.author = author
        self.icon = icon
        self.feed_url = feed_url
        self.entries = []
        self.summary = summary
        self.cover_url = cover_url
        self.last_updated = None

    def add(self, content, title, url, updated, content_type=None, files=None,
            chapters=None):
        if files is None:
            files = []
        if content_type is None:
            content_type = 'html'

        updated = updated.replace(tzinfo=timezone.utc)

        if self.last_updated is None:
            self.last_updated = updated
        elif updated > self.last_updated:
            self.last_updated = updated

        self.entries.append(
            FeedEntry(content, title, url, content_type, updated, files,
                      chapters))

    def get_response(self):
        register_namespace('', 'http://www.w3.org/2005/Atom')
        register_namespace('podcast',
                           'https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/1.0.md')
        register_namespace('itunes',
                           'http://www.itunes.com/dtds/podcast-1.0.dtd')

        rss = Element('rss')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        rss.set('xmlns:podcast',
                'https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/1.0.md')
        rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
        rss.set("version", "2.0")
        top = SubElement(rss, "channel")
        title_elem = SubElement(top, "title")
        title_elem.text = self.title

        atom_link = SubElement(top, 'atom:link')
        atom_link.set('href', self.feed_url)
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

        updated_elem = SubElement(top, 'lastBuildDate')
        updated_elem.text = self.last_updated.strftime(' %Y %H:%M:%S %z')

        link1_elem = SubElement(top, 'link')
        link1_elem.text = self.url

        it_type = SubElement(top, 'itunes:type')
        it_type.text = 'episodic'
        it_author = SubElement(top, 'itunes:author')
        it_author.text = 'postmarketOS'
        it_ex = SubElement(top, 'itunes:explicit')
        it_ex.text = 'no'

        image_elem = SubElement(top, 'image')
        image_url = SubElement(image_elem, 'url')
        image_url.text = self.cover_url
        image_title = SubElement(image_elem, 'title')
        image_title.text = self.title

        summary = SubElement(top, 'description')
        summary.text = self.summary

        for entry in self.entries:
            entry.generate(top)

        encoded = tostring(rss, xml_declaration=True, encoding='utf-8',
                           method='xml')
        return Response(encoded, mimetype='application/rss+xml')


if __name__ == '__main__':
    _test = AtomFeed(author='postmarketOS bloggers',
                     feed_url='https://example.com/feed.atom',
                     icon='https://example.com/icon.svg',
                     title='postmarketOS Blog',
                     url='https://example.com/blog/')

    _test.add(content='<h1>hi</h1>',
              content_type='html',
              title='test post',
              url='https://example.com/blog/test-post',
              updated=datetime.now())

    print(_test.get_response().response)
