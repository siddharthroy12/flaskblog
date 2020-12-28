import os
from flaskblog import app

if __name__ == "__main__":
    if os.environ['ENV'] == "production":
        app.run()
    else:
        app.run(debug=True)