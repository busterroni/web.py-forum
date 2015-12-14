import web, bcrypt, random, model
from web import form

urls=(
    '/', 'Index',
    '/login', 'Login',
    '/register', 'Register',
    '/logout', 'Logout',
    '/newpost', 'NewPost',
    '/post/(\d+)', 'ViewPost'
)
web.config.debug=False
app=web.application(urls, globals())
render=web.template.render('templates/')
if web.config.get('_session') is None:
    session=web.session.Session(app, web.session.DiskStore('sessions'), initializer={'username': '', 'loggedIn': False})
    web.config._session=session
else:
    session=web.config._session

db=web.database(dbn='mysql', db='forum', user='root', pw='a')

class Index:
    def GET(self):
        return render.index(model.recent_topics())

class Login:
    loginForm=form.Form(
        form.Textbox('username', description="", class_="form-control center", id="username", placeholder="Username"),
        form.Password('password', description="", class_="form-control center", id="password", placeholder="Password"),
        form.Button('Submit')
    )
    blankForm=form.Form()
    def GET(self):
        if session.loggedIn:
            return web.seeother('/')
        return render.login(self.loginForm, "")
    def POST(self):
        form=self.loginForm
        if not form.validates():
            return render.login(self.loginForm, "The form did not validate.")
        else:
            username=form.d.username
            password=form.d.password
            pwCorrect=checkAccount(username, password)
            if pwCorrect:
                return web.seeother('/')
            else:
                return render.login(self.loginForm, "incorrect username or password")

class Logout:
    def GET(self):
        session.kill()
        return web.seeother('/')

class Register:
    registerForm=form.Form(
        form.Textbox('username', form.regexp('^[a-zA-Z0-9]{1,20}$', 'Only letters or numbers, <20 characters'), description="", class_="form-control center", id="username", placeholder="Username"),
        form.Password('password', form.regexp('.{6,100}', 'Your password must be at least 6 characters'), description="", class_="form-control center", id="password", placeholder="Password"),
        form.Password('password2', description="", class_="form-control center", placeholder="Confirm password"),
        form.Textbox('email', form.regexp('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', 'Invalid email'), description="", class_="form-control center", id="email", placeholder="Email"),
        form.Button('Submit'),
        validators=[form.Validator("Passwords didn't match", lambda i: i.password == i.password2)]
    )
    blankForm=form.Form()
    def GET(self):
        if session.loggedIn:
            return web.seeother('/')
        return render.register(self.registerForm, "")
    def POST(self):
        form=self.registerForm
        if not form.validates():
            return render.register(self.registerForm, "The form did not validate.")
        else:
            username=form.d.username
            password=form.d.password
            email=form.d.email
            users=db.select('users')
            for user in users:
                if username==user.username:
                    return render.register(self.registerForm, "Username already taken")

            hashedPassword=bcrypt.hashpw(password, bcrypt.gensalt())
            model.add_user(username, hashedPassword, email)
            return render.register(self.blankForm, "Success!")

class NewPost():
    newPostForm=form.Form(
        form.Textbox('title', placeholder="Title"),
        form.Textbox('body', placeholder="Body..."),
        form.Button('Submit')
    )
    def GET(self):
        if not session.loggedIn:
            raise web.seeother('/register')
        return render.newpost(self.newPostForm)
    def POST(self):
        form=self.newPostForm
        if not form.validates():
            return "Form didn't validate, please try again"
        model.add_topic(form.d.title, form.d.body, session.get('id'))
        return "<html>Successfully added new topic \"%s\"! <a href=\"/\">Return home</a>.</html" % form.d.title

class ViewPost():
    newReplyForm=form.Form(
        form.Textbox('body', placeholder="Body..."),
        form.Button('Submit')
    )
    def GET(self, id):
        return render.viewpost(id, model.get_post(id), self.newReplyForm, db)
    def POST(self, id):
        form=self.newReplyForm
        if not form.validates():
            return ":("
        model.add_reply(int(id), form.d.body, session.get('id'))
        return "<html>Successfully added new reply \"%s\"! <a href=\"/post/%s\">Go back to topic</a>.</html" % (form.d.body, id)


def checkAccount(username, password):
    try:
        user=db.query('SELECT * FROM users WHERE username=$username', vars={'username': username})[0]
    except IndexError:
        return False
    userPass=user['password']
    if bcrypt.hashpw(password, userPass) == userPass:
        session.loggedIn=True
        session.username=user['username']
        session.id=user['id']

        return True
    return False

if __name__=="__main__":
    app.run()