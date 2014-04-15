# !/usr/bin/env python

from google.appengine.ext import db

import functions

class BlogPost(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	coords = db.GeoPtProperty()

	def as_dict(self):
		time_fmt = "%c"
		d = {"subject": self.subject if self.subject else None,
			"content": self.content if self.content else None,
			"created": self.created.strftime(time_fmt) if self.created else None,
			"last_modified": self.last_modified.strftime(time_fmt) if self.last_modified else None,
			"coords": "%s,%s" % (self.coords.lat, self.coords.lon) if self.coords else None}
		return d

class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	@classmethod
	def by_id(cls, uid):
		return cls.get_by_id(uid, parent = functions.users_key())

	@classmethod
	def by_name(cls, name):
		u = db.GqlQuery("SELECT * FROM User WHERE name = :1", name).get()
		return u

	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = functions.make_pw_hash(name, pw)
		return User(
			parent = functions.users_key(),
			name = name,
			pw_hash = pw_hash,
			email = email
		)

	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and functions.valid_pw(name, pw, u.pw_hash):
			return u