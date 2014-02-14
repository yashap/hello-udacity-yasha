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

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

# Create my entity
class BlogPosts(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

# Handler for the page displaying posts
class BlogHandler(Handler):
	def render_blog(self, subject="", content="", created="", error=""):
		currentPosts = db.GqlQuery("SELECT * FROM BlogPosts ORDER BY created DESC LIMIT 10")
		self.render("blog.html", subject=subject, content=content, error=error, currentPosts=currentPosts)

	def get(self):
		self.render_blog()

# Handler for the page to submit posts
class AdminHandler(Handler):
	def render_blog(self, subject="", content="", error=""):
		self.render("post.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_blog()

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
			self.render_blog(subject, content, error)

# Handler for permalinks to individual posts
class Permalink(BlogHandler):
	def get(self, post_id):
		this_post = BlogPosts.get_by_id(int(post_id))

		if not this_post:
			self.error(404)
			return

		self.render("blog.html", currentPosts = [this_post])

# Defines what class to handle requests related to each url
app = webapp2.WSGIApplication([
		('/', BlogHandler),
		('/newpost', AdminHandler),
		('/([0-9]+)', Permalink)
		# The () mean this part should be passed as a parameter to our handler
		# The [0-9]+ part is a regular expression.  [0-9] means any digit, + means 1 or more
	],
	debug=True)
