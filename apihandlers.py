import functions
import entities
import handlers

# Handler for the page displaying posts
###############################
class BlogAPI(handlers.Handler):
	def get(self):
		currentPosts = entities.db.GqlQuery("SELECT * "
			"FROM BlogPost "
			"ORDER BY created DESC "
			"LIMIT 10"
			)

		currentPosts = list(currentPosts)

		points = []
		for p in currentPosts:
			if p.coords:
				points.append(p.coords)

		img_url = None
		if points:
			img_url = functions.gmaps_img(points)

		self.render("blog.html", currentPosts=currentPosts, img_url=img_url)

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

		point = None
		if this_post.coords:
			point = this_post.coords

		img_url = None
		if point:
			img_url = functions.gmaps_img([point])

		self.render("permalink.html", currentPosts = [this_post], img_url=img_url)