import functions
import entities
import handlers
import json

# Handler for the page displaying posts
###############################
class BlogAPI(handlers.Handler):
	def get(self):
		currentPosts = entities.db.GqlQuery("SELECT * "
			"FROM BlogPost "
			"ORDER BY created DESC "
			"LIMIT 10"
			)

		data = []
		for p in currentPosts:
			print p.last_modified
			data.append({
				"subject": p.subject, 
				"content": p.content,
				"created": p.created.strftime("%b %d %Y %H:%M:%S"),
				"last_modified": p.last_modified.strftime("%b %d %Y %H:%M:%S"),
				"coords": p.coords
			})

		self.response.headers["Content-Type"] = "application/json; charset=UTF-8"
		self.write(json.dumps(data))


# Handler for permalinks to individual posts
###############################
class PermalinkAPI(handlers.Handler):
	def get(self, post_id):
		# look at how we set up the mapping
		# 	post_id is automatically passed to the handler
		this_post = entities.BlogPost.get_by_id(int(post_id), parent=functions.blog_key())

		if not this_post:
			self.error(404)
			return

		data = {
			"subject": this_post.subject, 
			"content": this_post.content,
			"created": this_post.created.strftime("%b %d %Y %H:%M:%S"),
			"last_modified": this_post.last_modified.strftime("%b %d %Y %H:%M:%S"),
			"coords": this_post.coords
		}

		self.response.headers["Content-Type"] = "application/json; charset=UTF-8"
		self.write(json.dumps(data))
