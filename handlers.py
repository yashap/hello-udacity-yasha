# !/usr/bin/env python

import webapp2

import functions
import entities

# General Handler class
###############################
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		# literally just makes it easier to type

	def render_str(self, template, **params):
		t = functions.jinja_env.get_template(template)
		params["user"] = self.user
		return t.render(params)
		# pass it the template, then the paramaters you want to pass in
		# gives you a template object, then you can call the render method to render it with the params
		# we're also making sure that the user object (from the initialize method) is always passed as one of the params
		# 	Honestly, not sure why yet

	def render(self, template, **params):
		self.write(self.render_str(template, **params))
		# writes the rendered template

	def set_secure_cookie(self, name, val):
		cookie_val = functions.make_secure_val(val)
		self.response.headers.add_header(
			"Set-Cookie",
			"%s=%s; Path=/" % (name, cookie_val)
		)
		# sets a secure cookie in the http response
		# 	name is the name of the cookie
		# 	val is the value to make secure, i.e. the user id
		# so after we verify a login attempt, we can pass the user id to this

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and functions.check_secure_val(cookie_val)
		# This is Python shorthand for "if cookie_val and check_secure_val: return check_secure_val(cookie_val)"
		# so if the cookie is legit (properly hashed):
		# 	this will return the user id since check_secure_val() takes in userid|hash

	def login(self, user):
		self.set_secure_cookie("user", str(user.key().id()))
		# set_secure_cookie takes two arguments, the cookie name and the user id
		# we already know the cookie name -> "user"
		# to get the user id, we pass in the user object, then grab it with user.key().id()

	def logout(self):
		self.response.headers.add_header(
			"Set-Cookie",
			"user=; Path=/"
		)
		# simply set an empty cookie

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie("user")
		self.user = uid and entities.User.by_id(int(uid))
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
		currentPosts = entities.db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
		self.render("blog.html", currentPosts=currentPosts)

# Handler for the page to submit posts
###############################
class NewPostHandler(Handler):
	def get(self):
		if self.user:
			self.render("newpost.html")
		else:
			self.redirect("/blog/signup")

	def post(self):
		if self.user:
			subject = self.request.get("subject")
			content = self.request.get("content")

			if subject and content:
				# if they entered a subject and content
				e = entities.BlogPost(parent = functions.blog_key(), subject=subject, content=content)
				e.put()
				this_id = str(e.key().id())

				self.redirect("/blog/%s" % this_id)

			else:
				error = "We need both a subject and a blog post!"
				self.render("newpost.html", subject=subject, content=content, error=error)

		else:
			self.redirect("/blog/signup")

# Handler for permalinks to individual posts
###############################
class PermalinkHandler(Handler):
	def get(self, post_id):
		# look at how we set up the mapping
		# 	post_id is automatically passed to the handler
		this_post = entities.BlogPost.get_by_id(int(post_id), parent=functions.blog_key())

		if not this_post:
			self.error(404)
			return

		self.render("permalink.html", currentPosts = [this_post])

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

		if not functions.valid_username(self.username):
			params["error"] = "That's not a valid username."
			have_error = True
		elif not functions.valid_password(self.password):
			params["error"] = "That's not a valid password."
			have_error = True
		elif self.password != self.verify:
			params["error"] = "Your passwords don't match."
			have_error = True
		elif not functions.valid_email(self.email):
			params["error"] = "That's not a email."
			have_error = True
		elif entities.User.by_name(self.username):
			params["error"] = "That username has already been taken."
			have_error = True

		if have_error:
			self.render("signup.html", **params)
		else:
			u = entities.User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)
			self.redirect("/blog/welcome")


# Handler for the welcome page
###############################
class WelcomeHandler(Handler):
	def get(self):
		if self.user:
			self.render("welcome.html", username = self.user.name)
		else:
			self.redirect("/blog/signup")
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

		u = entities.User.login(username, password)
		# remember that User.login just checks the db to see if the username and pw are valid
		# 	if so, it returns the user object from the db
		# it doesn't actually set the user cookie

		if u:
			self.login(u)
			# that sets the cookie!
			self.redirect("/blog/welcome")
		else:
			self.render("login.html", error = "Invalid login.")

# Handler for the logout page
###############################
class LogoutHandler(Handler):
	def get(self):
			self.logout()
			self.redirect("/blog/signup")
