from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Drowsiness Detection App Running Successfully!"

if __name__ == "__main__":
    app.run()