from flask import (Flask, render_template, url_for, abort,
                   redirect, g, flash, request)

from flask_login import (LoginManager, login_user, logout_user,
                         login_required)

from flask_bcrypt import check_password_hash
from flask_wtf.csrf import CSRFProtect

import models, forms


DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)
app.secret_key = 'ultrasecretz'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash('Your email or password does not match', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password does not match', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out!', 'success')
    return redirect(url_for('index'))


@app.route('/')
@app.route('/entries')
@app.route('/entries/<tag>')
def index(tag=None):
    if tag:
        entries = models.JournalEntry.select().join(models.EntryTag).where(
            models.EntryTag.tag == tag
        ).order_by(models.JournalEntry.id.desc())
    else:
        entries = models.JournalEntry.select().order_by(models.JournalEntry.id.desc())
    return render_template('index.html', entries=entries)


@app.route('/entries/<int:id>')
def entry_detail(id):
    entry = models.JournalEntry.select().where(
        models.JournalEntry.id == id
    ).order_by(models.JournalEntry.id).get()
    if not entry:
        abort(404)
    return render_template('detail.html', entry=entry)


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.JournalEntry.create_journal_entry(
            title=form.title.data.strip(),
            created_at=form.created_at.data,
            time=form.time.data,
            entry=form.entry.data,
            resources=form.resources.data,
        )
        for tag in form.tags.data.split(','):
            models.EntryTag.create(
                tag=tag,
                entry=models.JournalEntry.get(
                    models.JournalEntry.title == form.title.data.strip(),
                )
            )
        flash('Journal entry created!', 'success')
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_entry(id):
    entry = models.JournalEntry.get(models.JournalEntry.id == id)
    form = forms.EditEntryForm()
    form.process(formdata=request.form, obj=entry)
    # TODO: find a better solution to the row below (78) for pre-populating the tags-field
    form.tags.process(formdata=request.form, data=(','.join([tag.tag for tag in entry.tags])))
    if form.validate_on_submit():
        models.JournalEntry.update({
            models.JournalEntry.title: form.title.data,
            models.JournalEntry.created_at: form.created_at.data,
            models.JournalEntry.time: form.time.data,
            models.JournalEntry.entry: form.entry.data,
            models.JournalEntry.resources: form.resources.data,
        }).where(
            models.JournalEntry.id == id
        ).execute()

        for tag in entry.tags:
            if tag.tag not in form.tags.data.split(','):
                tag.delete_instance()
        for tag in form.tags.data.split(','):
            if tag not in [tag.tag for tag in entry.tags] and tag != '':
                models.EntryTag.create(
                    tag=tag,
                    entry=entry,
                )

        flash('Journal entry edited!', 'success')
        return redirect(url_for('entry_detail', id=id))
    return render_template('edit.html', entry=entry, form=form)


@app.route('/entries/<int:id>/delete')
@login_required
def delete_entry(id):
    entry = models.JournalEntry.select().where(
        models.JournalEntry.id == id
    ).get()
    entry.delete_instance()
    flash('Entry deleted!', 'success')
    return redirect((url_for('index')))


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='admin',
            password='admin',
        )
        models.JournalEntry.create_journal_entry(
            title='Initial Journal Entry',
            created_at=models.JournalEntry.created_at.default(),
            time='1 hour',
            entry='My first journal entry!',
            resources='teamtreehouse.com',
        )
        models.EntryTag.create(
            tag='tag',
            entry=models.JournalEntry.get(models.JournalEntry.id == 1),
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
