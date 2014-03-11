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

import webapp2

import handlers

app = webapp2.WSGIApplication([
		("/blog", handlers.BlogHandler),
		("/blog/newpost", handlers.NewPostHandler),
		("/blog/([0-9]+)", handlers.PermalinkHandler),
		# The () mean this part should be passed as a parameter to our handler
		# The [0-9]+ part is a regular expression.  [0-9] means any digit, + means 1 or more
		("/blog/signup", handlers.SignupHandler),
		("/blog/login", handlers.LoginHandler),
		("/blog/logout", handlers.LogoutHandler),
		("/blog/welcome", handlers.WelcomeHandler)
	],
	debug=True)
