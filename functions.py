# !/usr/bin/env python

import os
import jinja2
import hmac
import random
import string
import hashlib
import re

from google.appengine.ext import db

# Template boilerplate
###############################
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

# Hashing functions for cookies
###############################
SECRET = "imsosecret"

def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()
	# used for secure cookies, in make_secure_val

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))
	# used for secure cookies
	# 	i.e. pass the userid, get the secure cookie
	# make_secure_val("12356")
	# 	"12356|8d8e8018be02969246ef4ac04bf2a151"

def check_secure_val(h):
	val = h.split("|")[0]
	if h == make_secure_val(val):
		return val
	# checks cookies
	# check_secure_val("12356|8d8e8018be02969246ef4ac04bf2a151") --> "12356"
	# check_secure_val("NOT12356|8d8e8018be02969246ef4ac04bf2a151") --> None

# Hashing functions for database
###############################
def make_salt():
	return "".join(random.choice(string.ascii_letters) for x in range(5))
	# just returns a string of 5 random ascii letters

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s,%s" % (salt, h)
	# if you don"t give a salt, it will return different every time
	# 	make_pw_hash("ypodeswa","testPass")
	# 		"tDtdD,26addd6404e3a8fd561496d6661c3308641c99edf719cd07676060a59e1b03c7"
	# 		"gyDWP,e0f90bf5799dba3f87da323ed9164937c2f59411f4c4cc3159ddfbbe924d56b3"
	# but if you give it a salt
	# 	make_pw_hash("ypodeswa","testPass","Salty")
	# 		"Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d"
	# 		"Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d"
	# the idea is that this can be used to create the original pw hash, with a random salt, to store in the db
	# BUT it can also be used in valid_pw, to validate a user/pw combo, as we can grab the salt from the hash

def valid_pw(name, pw, h):
	salt = h.split(",")[0]
	return h == make_pw_hash(name, pw, salt)
	# Given the username, pw and hash, tells you if it"s the valid pw for the username
	# 	Note that you"d have to be able to pull h out of a db?
	# valid_pw("ypodeswa","testPass","Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d")
	# 	True
	# valid_pw("ypodeswa","wrongPass","Salty,6afd21bb3b0c725c5f1ebc1c318da527da090c74d01a2f21b09d0cbba8f5fe0d")
	# 	False

def users_key(group = "default"):
	return db.Key.from_path("users", group)
	# An instance of the Key class represents a unique key for a Datastore entity
	# 	Key is provided by the google.appengine.ext.db module
	# Key.from_path() builds a new Key object from an ancestor path of one or more entity keys
	# Creates an ancestor element, in the db, to store all our users
	# 	I don't really get what this does, honestly
	# 	Just gonna roll with it

def blog_key(name = "default"):
	return db.Key.from_path("blogs", name)
	# As above, but it's an ancestor element, in the db, to store all our blog posts

# Form validation
###############################
user_regex = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and user_regex.match(username)

pass_regex = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and pass_regex.match(password)

email_regex = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
	return not email or email_regex.match(email)