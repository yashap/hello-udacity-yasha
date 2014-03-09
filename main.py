# !/usr/bin/env python

# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import webapp2
import jinja2
import hmac
import random
import string
import hashlib
import re

from google.appengine.ext import db


###############################
# Boilerplate and general purpose functions
###############################

# Template boilerplate
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

# Hashing functions for cookies
###############################
SECRET = 'imsosecret'

def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()
	# used for secure cookies, in make_secure_val

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))
	# used for secure cookies
	# 	i.e. pass the userid, get the secure cookie
	# make_secure_val('12356')
	# 	'12356|8d8e8018be02969246ef4ac04bf2a151'

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val
	# checks cookies
	# check_secure_val('12356|8d8e8018be02969246ef4ac04bf2a151') --> '12356'
	# check_secure_val('NOT12356|8d8e8018be02969246ef4ac04bf2a151') --> None

# Hashing functions for database
###############################
def make_salt():
	return ''.join(random.choice(string.ascii_letters) for x in range(5))
	# just returns a string of 5 random ascii letters

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)
	# if you don't give a salt, it will return different every time
	# 	make_pw_hash('ypodeswa','testPass')
	# 		'tDtdD,26addd6404e3a8fd561496d6661c3308641c99edf719cd07676060a59e1b03c7'
	# 		'gyDWP,e0f90bf5799dba3f87da323ed9164937c2f59411f4c4cc3159ddfbbe924d56b3'
	# but if you give it a salt
	# 	make_pw_hash('ypodeswa','testPass','Salty')
	# 		'Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d'
	# 		'Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d'
	# the idea is that this can be used to create the original pw hash, with a random salt, to store in the db
	# BUT it can also be used in valid_pw, to validate a user/pw combo, as we can grab the salt from the hash

def valid_pw(name, pw, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, pw, salt)
	# Given the username, pw and hash, tells you if it's the valid pw for the username
	# 	Note that you'd have to be able to pull h out of a db?
	# valid_pw('ypodeswa','testPass','Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d')
	# 	True
	# valid_pw('ypodeswa','wrongPass','Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d')
	# 	False

def users_key(group = 'default'):
	return db.Key.from_path('users', group)
	# An instance of the Key class represents a unique key for a Datastore entity
	# 	Key is provided by the google.appengine.ext.db module
	# Key.from_path() builds a new Key object from an ancestor path of one or more entity keys
	# Creates an ancestor element, in the db, to store all our users
	# 	I don't really get what this does, honestly
	# 	Just gonna roll with it

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)
	# As above, but it's an ancestor element, in the db, to store all our blog posts

# Form validation
###############################
user_regex = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and user_regex.match(username)

pass_regex = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and pass_regex.match(password)

email_regex = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	return not email or email_regex.match(email)


###############################
# Entities
###############################
class BlogPosts(db.Model):
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
		return User.get_by_id(uid, parent = users_key())
		# this is a convenience function to quickly get the user out of the db
		# 	cls is very similar to self
		# 	self refers to the instance of the class (the object)
		# 	cls refers to the class itself
		# pass the id, get the user object

	@classmethod
	def by_name(clas, name):
		u = db.GqlQuery("SELECT * FROM User WHERE name = :1", name).get()
		return u
		# pass the username, get the user object

	@classmethod
	def register(cls, name, pw, email=None):
		pw_hash = make_pw_hash(name, pw)
		return User(
			parent = users_key(),
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
		if u and valid_pw(name, pw, u.pw_hash):
			return u
		# note the use of the by_name() method, which will return a user object from the db
		# 	Doesn't verify anything, just grabs the user object
		# then it takes the name and pw it's passed, and verifies against the pw has from the db
		# 	if valid, returns the user object
		# so this will be used to log people in, as we can use this user object to generate the secure cookie


###############################
# Handlers
###############################

# General Handler class, that specific handlers will inherit from
###############################
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		# literally just makes it easier to type

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		params['user'] = self.user
		return t.render(params)
		# pass it the template, then the paramaters you want to pass in
		# gives you a template object, then you can call the render method to render it with the params
		# we're also making sure that the user object (from the initialize method) is always passed as one of the params
		# 	Honestly, not sure why yet

	def render(self, template, **params):
		self.write(self.render_str(template, **params))
		# writes the rendered template

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val)
		)
		# sets a secure cookie in the http response
		# 	name is the name of the cookie
		# 	val is the value to make secure, i.e. the user id
		# so after we verify a login attempt, we can pass the user id to this

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)
		# This is Python shorthand for "if cookie_val and check_secure_val: return check_secure_val(cookie_val)"
		# so if the cookie is legit (properly hashed):
		# 	this will return the user id since check_secure_val() takes in userid|hash

	def login(self, user):
		self.set_secure_cookie('user', str(user.key().id()))
		# set_secure_cookie takes two arguments, the cookie name and the user id
		# we already know the cookie name -> 'user'
		# to get the user id, we pass in the user object, then grab it with user.key().id()

	def logout(self):
		self.response.headers.add_header(
			'Set-Cookie',
			'user=; Path=/'
		)
		# simply set an empty cookie

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user')
		self.user = uid and User.by_id(int(uid))
		# This function is automatically called by the app enginge framework
		# 	any handlers we have that inherit from this Handler class (i.e. all of them) will automatically be storing this user object in self.user if the user is legitimately logged in
		# 	so it's just easy access to the user object, if the user is logged in
		# Basically, IF the cookie is properly hashed, uid = the user id
		# User.by_id(int(uid)) checks the db to see if this user id is in there, and if so it returns the user object
		# 	we store this user object in self.user


# Handler for the page displaying posts
###############################
class BlogHandler(Handler):
	def get(self):
		currentPosts = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT 10")
		self.render("blog.html", currentPosts=currentPosts)

# Handler for the page to submit posts
###############################
class AdminHandler(Handler):
	def get(self):
		if self.user:
			self.render("post.html")
		else:
			self.redirect("/login")

	def post(self):
		if self.user:
			subject = self.request.get("subject")
			content = self.request.get("content")

			if subject and content:
				# if they entered a subject and content
				e = BlogPosts(parent = blog_key(), subject=subject, content=content)
				e.put()
				this_id = str(e.key().id())

				self.redirect("/%s" % this_id)

			else:
				error = "We need both a subject and a blog post!"
				self.render("post.html", subject=subject, content=content, error=error)

		else:
			self.redirect('/login')

# Handler for permalinks to individual posts
###############################
class Permalink(Handler):
	def get(self, post_id):
		# look at how we set up the mapping
		# 	post_id is automatically passed to the handler
		this_post = BlogPosts.get_by_id(int(post_id), parent=blog_key())

		if not this_post:
			self.error(404)
			return

		self.render("blog.html", currentPosts = [this_post])

# Handler for the signup page
###############################
class SignupHandler(Handler):
	def get(self):
		self.render("signup.html")

	def post(self):
		self.username = self.request.get("username")
		self.password = self.request.get("password")
		self.verify = self.request.get("verify")
		self.email = self.request.get("email")

		have_error = False
		params = {"username": self.username,
			"password": self.password,
			"verify": self.verify,
			"email": self.email
		}

		if not valid_username(self.username):
			params["error"] = "That's not a valid username."
			have_error = True
		elif not valid_password(self.password):
			params["error"] = "That's not a valid password."
			have_error = True
		elif self.password != self.verify:
			params["error"] = "Your passwords don't match."
			have_error = True
		elif not valid_email(self.email):
			params["error"] = "That's not a email."
			have_error = True
		elif User.by_name(self.username):
			params["error"] = "That username has already been taken."
			have_error = True

		if have_error:
			self.render('signup.html', **params)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)
			self.redirect("/welcome")


# Handler for the welcome page
###############################
class WelcomeHandler(Handler):
	def get(self):
		if self.user:
			self.render("welcome.html", username=self.user.name)
		else:
			self.redirect("/")
		# remember that the initialize function automatically checks the cookie
		# 	if legit, stores the user object in self.user


# Handler for the login page
###############################
class LoginHandler(Handler):
	def get(self):
		self.render("login.html")

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")

		u = User.login(username, password)
		# remember that User.login just checks the db to see if the username and pw are valid
		# 	if so, it returns the user object from the db
		# it doesn't actually set the user cookie

		if u:
			self.login(u)
			# that sets the cookie!
			self.redirect('/')
		else:
			self.render('login.html', error = "Invalid login.")

# Handler for the logout page
###############################
class LogoutHandler(Handler):
	def get(self):
			self.logout()
			self.redirect("/")


###############################
# Mapping
###############################

app = webapp2.WSGIApplication([
		('/', BlogHandler),
		('/newpost', AdminHandler),
		('/([0-9]+)', Permalink),
		# The () mean this part should be passed as a parameter to our handler
		# The [0-9]+ part is a regular expression.  [0-9] means any digit, + means 1 or more
		('/signup', SignupHandler),
		('/login', LoginHandler),
		('/logout', LogoutHandler),
		('/welcome', WelcomeHandler)
	],
	debug=True)
