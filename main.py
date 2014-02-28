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

from google.appengine.ext import db


###############################
# Boilerplate and general purpose functions
###############################

# Template boilerplate
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

# Hashing functions
SECRET = 'imsosecret'

def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val


###############################
# Entities
###############################
class BlogPosts(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Members(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty(required = False)
	created = db.DateTimeProperty(auto_now_add = True)


###############################
# Handlers
###############################

# General Handler class, that specific handlers will inherit from
###############################
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

# Handler for the page displaying posts
###############################
class BlogHandler(Handler):
	def render_blog(self, subject="", content="", created="", error=""):
		currentPosts = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT 10")
		self.render("blog.html", subject=subject, content=content, error=error, currentPosts=currentPosts)

	def get(self):
		self.render_blog()

# Handler for the page to submit posts
###############################
class AdminHandler(Handler):
	def render_page(self, subject="", content="", error=""):
		self.render("post.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_page()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			# if they post good imput, then create a new db record (note that created doesn't have to be entered)
			e = BlogPosts(subject=subject, content=content)
			e.put()
			this_id = str(e.key().id())

			self.redirect("/%s" % this_id)

		else:
			error = "We need both a subject and a blog post!"
			self.render_page(subject, content, error)

# Handler for permalinks to individual posts
###############################
class Permalink(BlogHandler):
	def get(self, post_id):
		this_post = BlogPosts.get_by_id(int(post_id))

		if not this_post:
			self.error(404)
			return

		self.render("blog.html", currentPosts = [this_post])

# Handler for the signup page
###############################
class SignupHandler(Handler):
	def render_page(self, username="", password="", verify="", email="", error=""):
		self.render("signup.html", username=username, password=password, verify=verify, email=email, error=error)

	def get(self):
		self.render_page()

	def checkUser(self, user):
		# Read up on Google data store:
		# https://developers.google.com/appengine/docs/python/ndb/
		q = db.GqlQuery("SELECT * FROM Members WHERE username = :1", user)
		this_user = q.get()
		if this_user:
			return this_user
		else:
			return None

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		user_in_db = self.checkUser(username)

		if not username or not password or not verify:
			error = "Please enter a user name and password."
			self.render_page(username, password, verify, email, error)

		elif password != verify:
			error = "Your password and verification password were not the same."
			self.render_page(username, password, verify, email, error)

		elif user_in_db:
			error = "This user name has already regisitered for an account."
			self.render_page(username, password, verify, email, error)

		else:
			e = Members(username=username, password=password, email=email)
			e.put()

			user_id = str(e.key().id())
			user_cookie = make_secure_val(str(user_id))
			self.response.headers.add_header('Set-Cookie', 'user=%s; Path=/' % user_cookie)

			self.redirect("/welcome")


# Handler for the welcome page
###############################
class WelcomeHandler(Handler):
	def get_user(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id = check_secure_val(user_cookie)
			if user_id:
				user = Members.get_by_id(int(user_id))
				return user.username
			else:
				self.redirect("/signup")
		else:
			self.redirect("/signup")

	def get(self):
		username = self.get_user()
		self.render("welcome.html", username=username)


###############################
# Mapping
###############################

app = webapp2.WSGIApplication([
		('/', BlogHandler),
		('/newpost', AdminHandler),
		('/([0-9]+)', Permalink),
		('/signup', SignupHandler),
		('/welcome', WelcomeHandler)
		# The () mean this part should be passed as a parameter to our handler
		# The [0-9]+ part is a regular expression.  [0-9] means any digit, + means 1 or more
	],
	debug=True)
