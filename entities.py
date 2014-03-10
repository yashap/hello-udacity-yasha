# !/usr/bin/env python

from google.appengine.ext import db

import functions

class BlogPost(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

class User(db.Model):
	name = db.StringProperty(required = True)
	pw_hash = db.StringProperty(required = True)
	email = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	@classmethod
	# this is a "decorator"
	# means you can call this method on a User object
	def by_id(cls, uid):
		return cls.get_by_id(uid, parent = functions.users_key())
		# this is a convenience function to quickly get the user out of the db
		# 	cls is very similar to self
		# 	self refers to the instance of the class (the object)
		# 	cls refers to the class itself
		# pass the id, get the user object

	@classmethod
	def by_name(cls, name):
		u = db.GqlQuery("SELECT * FROM User WHERE name = :1", name).get()
		return u
		# pass the username, get the user object

	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = functions.make_pw_hash(name, pw)
		return User(
			parent = functions.users_key(),
			name = name,
			pw_hash = pw_hash,
			email = email
		)
		# Note that this creates the object, but doesn't store it in the db yet
		# We are mostly going to use this for entering user objects into the db, though
		# 	i.e. a user enters their details into the login page
		# 	then if they're valid we use this create the user that we can then enter into the db
		# 	also note that 

	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and functions.valid_pw(name, pw, u.pw_hash):
			return u
		# note the use of the by_name() method, which will return a user object from the db
		# 	Doesn't verify anything, just grabs the user object
		# then it takes the name and pw it's passed, and verifies against the pw has from the db
		# 	if valid, returns the user object
		# so this will be used to log people in, as we can use this user object to generate the secure cookie
