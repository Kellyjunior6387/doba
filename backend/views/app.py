import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask
from groq_llm import groq
from auth import auth
from views.Spotify import spotify


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Register blueprints with the app
#app.register_blueprint(auth)
app.register_blueprint(groq)
app.register_blueprint(auth)
app.register_blueprint(spotify)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000",debug=True, )
