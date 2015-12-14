import web, datetime

db=web.database(dbn='mysql', db='forum', user='root', pw='a')

def add_user(username, password, email):
	db.insert('users', username=username, password=password, email=email)

def add_topic(name, content, poster):
	db.insert('topics', poster=poster, name=name, content=content)

def add_reply(post_id, reply, poster):
	db.insert('replies', post_id=post_id, reply=reply, poster=poster)

def recent_topics():
	return db.query('SELECT * FROM topics ORDER BY last_updated')

def get_post(id):
	return db.query('SELECT * FROM replies WHERE post_id=' + id)