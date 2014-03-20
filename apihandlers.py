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
				"subject": p.subject if p.subject else None,
				"content": p.content if p.content else None,
				"created": p.created.strftime("%Y-%m-%d %H:%M:%S") if p.created else None,
				"last_modified": p.last_modified.strftime("%Y-%m-%d %H:%M:%S") if p.last_modified else None,
				"coords": "%s,%s" % (p.coords.lat, p.coords.lon) if p.coords else None
			})

		self.response.headers["Content-Type"] = "application/json; charset=UTF-8"
		self.write(json.dumps(data))


# Handler for permalinks to individual posts
###############################
class PermalinkAPI(handlers.Handler):
	def get(self, post_id):
		# look at how we set up the mapping
		# 	post_id is automatically passed to the handler
		p = entities.BlogPost.get_by_id(int(post_id), parent=functions.blog_key())

		if not p:
			self.error(404)
			return

		data = {
			"subject": p.subject if p.subject else None,
			"content": p.content if p.content else None,
			"created": p.created.strftime("%Y-%m-%d %H:%M:%S") if p.created else None,
			"last_modified": p.last_modified.strftime("%Y-%m-%d %H:%M:%S") if p.last_modified else None,
			"coords": "%s,%s" % (p.coords.lat, p.coords.lon) if p.coords else None
		}

		self.response.headers["Content-Type"] = "application/json; charset=UTF-8"
		self.write(json.dumps(data))
