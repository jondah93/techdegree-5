import datetime

from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


DATABASE = SqliteDatabase('journal_entries.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=25)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    @classmethod
    def create_user(cls, username, password, is_admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password),
                    is_admin=is_admin,
                )
        except IntegrityError:
            raise ValueError('User already exists')


class JournalEntry(Model):
    title = TextField(unique=True)
    created_at = DateField(default=datetime.date.today)
    time = TextField(verbose_name='time_spent')
    entry = TextField()
    resources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-created_at',)

    @classmethod
    def create_journal_entry(cls, title, created_at, time, entry, resources):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    created_at=created_at,
                    time=time,
                    entry=entry,
                    resources=resources,
                )
        except IntegrityError:
            raise ValueError('A journal entry with that title already exists')


class EntryTag(Model):
    # TODO: make this a many-to-many so that one tag can relate to multiple posts and make tag-field unique.
    tag = CharField()
    entry = ForeignKeyField(JournalEntry, backref='tags')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([JournalEntry, EntryTag, User], safe=True)
    DATABASE.close()
