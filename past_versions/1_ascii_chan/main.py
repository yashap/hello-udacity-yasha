#!/usr/bin/env python
#
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
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)
# autoescape = True is really convenient
# it means any html we insert into the template as a variable will be escaped automatically!
# there is a way to avoid this if you want, but this way the default is "safe"

class Handler(webapp2.RequestHandler):
# inherits from the webapp2 request handler class
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		# this just makes it so we don't have to write self.response.out.write all the time

	def render_str(self, template, **params):
		# this function takes a template as input, and returns a string of that template
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		# writes the string we've rendered
		self.write(self.render_str(template, **kw))

# In this framework you can simply create db tables like this
# This is us creating the 'Art' table
# ----> this entire class is just us creating a db "entity" (~table)!
class Art(db.Model):
	# db.Model is included from Google App Engine
	# it let's us work with entities
	title = db.StringProperty(required = True)
	art = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	# so in the entity we'll store the title, art and created date for every entry
	# title and art are String, created is a DateTime

class MainPage(Handler):
	# we'll be rendering the front page from both the get and post methods
	# give it its own method to prevent duplication!
	def render_front(self, title="", art="", error=""):
	# didn't put the template as an input, since we'll always use this method for a specific template
	# basically it will put the proper title/art/error (if applicable) into the template, then render the template into a string
		arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
		self.render("front.html", title=title, art=art, error=error, arts=arts)
		# so this is just taking the title/art/error values that we're passing into the method, and letting us use them in the template
		# for example, to use the title variable in the template, we just put {{title}} in the template where we want it substituted

	def get(self):
	# so when we receive a get request, we'll call the render_front method (defined above)
	# this means 
		self.render_front()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		# basic error handling
		if title and art:
			a = Art(title = title, art = art)
			a.put()

			self.redirect("/")
			# This is just to ignore those annoying "resubmit form" errors
		else:
			error = "we need both a title and some artwork!"
			self.render_front(title, art, error)
			# note that we had to pass title, art, error
			# this makes it so we don't "lose" the input when there's an error

app = webapp2.WSGIApplication([('/', MainPage)],
	debug=True)
