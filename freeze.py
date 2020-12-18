from flask_frozen import Freezer
from app import app, CAST_CONTENT_DIR, PAGE_CONTENT_DIR
from os import listdir

freezer = Freezer(app)
app.config['FREEZER_DESTINATION'] = 'public_html'
app.config['FREEZER_BASE_URL'] = 'https://cast.postmarketos.org/'


@freezer.register_generator
def episode():
    for f in listdir(CAST_CONTENT_DIR):
        slug = f.replace(".md", "")
        yield {'episode': slug}


@freezer.register_generator
def chapters():
    for f in listdir(CAST_CONTENT_DIR):
        slug = f.replace(".md", "")
        yield {'episode': slug}


@freezer.register_generator
def static_page():
    for f in listdir(PAGE_CONTENT_DIR):
        if 'index' in f:
            continue
        page = f[:-3]
        yield {'page': page}


if __name__ == '__main__':
    freezer.freeze()
