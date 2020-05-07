from flask import Flask
from registree_auth import check_user_id, requires_auth, requires_scope

app = Flask(__name__)

@app.route('/<id>')
@requires_auth
@requires_scope('registree')
@check_user_id
def display(id):
  return "This is protected information for user " + id

if __name__=='__main__':
  app.run()
