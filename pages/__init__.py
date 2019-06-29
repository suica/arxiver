from flask import Blueprint, render_template, request, redirect, after_this_request
from jinja2 import TemplateNotFound

pages = Blueprint('pages', __name__, template_folder='./templates', static_folder='./static')

excluded = ['bare', 'base']


@pages.route('/', defaults={'page': 'index'})
@pages.route('/<page>')
def show(page):
    if page in excluded:
        return render_template('404.html')

    logged_in_as = request.cookies.get('logged_in_as')

    if page in ['signin']:
        if logged_in_as and logged_in_as > '0':
            return redirect('/queue')

    if page in ['queue', 'manage']:
        if logged_in_as and logged_in_as > '0':
            pass
        else:
            return redirect('/signin')

    if page in ['manage']:
        if logged_in_as and logged_in_as > '1':
            pass
        else:
            return redirect('/queue')

    try:
        return render_template('{}.html'.format(page))
    except TemplateNotFound:
        return render_template('404.html')


@pages.route('/signout')
def logout():
    @after_this_request
    def set_cookie(response):
        response.set_cookie('logged_in_as', '0', max_age=64800)
        return response

    return redirect('/signin')


def init_page(app):
    app.register_blueprint(pages)


__all__ = [init_page]
