"""Flask app module."""
import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from page_analyzer.db import UrlCheckDatabase, UrlDatabase
from page_analyzer.page_parser import get_page_data
from page_analyzer.url_utilities import normalize, validate

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

PAGE_NOT_FOUND = 404


@app.route('/')
def index():
    """Home page.

    GET: Landing initial page.

    Returns:
        Render index.html template
    """
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def show_urls():
    """Show all urls already added.

    GET: Landing urls page.

    Returns:
        Render urls.html template with url records.
    """
    url_records = UrlDatabase().find_all()
    return render_template(
        'urls.html',
        records=url_records,
    )


@app.route('/urls', methods=['POST'])
def post_url():
    """Receive, check and add new url from filled form.

    POST: add new url from filled form.

    Returns:
        If url validation failed: redirect to render index.html template.
        If url valid: data stored in db, redirect to render url_detail.html.
    """
    url_address = request.form.get('url')
    errors = validate(url_address)
    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template(
            'index.html',
        ), 422

    normalized_url = normalize(url_address)
    try:
        repo = UrlDatabase()
        existing_record = repo.find_url_name(normalized_url)
        if existing_record:
            flash(
                'Страница уже существует',
                'info',
            )
            return redirect(
                url_for(
                    'show_url',
                    record_id=existing_record.get('id'),
                ),
            )

        flash('Страница успешно добавлена', 'success')
        return redirect(
            url_for(
                'show_url',
                record_id=repo.save({'name': normalized_url}),
            ),
        )
    except Exception as ex:
        flash(
            'Error {raised_ex} while save url'.format(raised_ex=ex),
            'danger',
        )
        return redirect(url_for('index'))


@app.route('/urls/<int:record_id>', methods=['GET'])
def show_url(record_id):
    """Page with stored url and already done SEO checks.

    GET: landing url detailed page.

    Parameters:
        record_id: id of url address.

    Returns:
        If url: render url_detail.html template.
        If url not exist: abort with 404 error
    """
    repo = UrlDatabase()
    url_record = repo.find_url_id(record_id)
    if not url_record:
        return abort(PAGE_NOT_FOUND)

    url_checks = UrlCheckDatabase().find_all_checks(record_id)
    return render_template(
        'url_detail.html',
        record=url_record,
        url_checks=url_checks,
    )


@app.route('/urls/<int:record_id>/checks', methods=['POST'])
def check_url(record_id):
    """Initiate a new check for existing url.

    POST: landing url detailed page.

    Parameters:
        record_id: id of url address.

    Returns:
        If url record exist: add check in db,
        redirect to render url_detail.html template.

        If url not exist: abort with 404 error.
    """
    url_record = UrlDatabase().find_url_id(record_id)

    if not url_record:
        return abort(PAGE_NOT_FOUND)

    try:
        response = requests.get(url_record.get('name'))
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')

    else:
        checks = UrlCheckDatabase()
        new_check = {'status_code': response.status_code}
        new_check.update(get_page_data(response.content.decode()))
        checks.save_check(record_id, new_check)
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', record_id=record_id))


@app.errorhandler(PAGE_NOT_FOUND)
def show_error_page(error):
    """Handle error 404.

    Parameters:
        error: caught 404 error.

    Returns:
         page for 404 error
    """
    return render_template(
        'page404.html',
        title='Страница не найдена',
    ), 404


if __name__ == '__main__':
    app.run(debug=True)
