from flask import Flask

from registree_auth import requires_auth, requires_scope
app = Flask(__name__)

@app.route('/')
@requires_auth
@requires_scope('admin')
def display():
  return "This is protected information!"

if __name__=='__main__':
  app.run()
