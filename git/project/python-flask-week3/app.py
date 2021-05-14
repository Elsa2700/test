from flask import *

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("week3.html")

app.run(host="0.0.0.0", port=3000, debug=True)