from flaskblog import app
from dotenv import load_dotenv

# Run app on debug mode. This is only used for development
if __name__ == "__main__":
    app.run(debug=True)