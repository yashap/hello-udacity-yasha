hello-udacity-yasha
===================

A web app I'm building for Steve Huffman's "Web Development" course on Udacity:

https://www.udacity.com/course/cs253

This code is deployed at:

http://hello-udacity-yasha.appspot.com

I'm building this app purely for learning purposes, following along with the lessons in the course, but at the moment:
- The app is a blog
- Anyone can register for an account, and post to the blog
- When you post, the app tries to map the location you posted from, though it doesn't do it particularly well
- The app is built on Google App Engine, using their webapp2 framework
- I'm using memcache to reduce DB queries
- The app has a simple JSON api.  Add ".json" to the url when you're on
  either the main blog page (i.e.
http://hello-udacity-yasha.appspot.com/blog.json) or on a link to
specific post (i.e.
http://hello-udacity-yasha.appspot.com/blog/5684049913839616.json) and
it'll return JSON instead of HTML
