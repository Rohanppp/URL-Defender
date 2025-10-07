#importing required libraries

from flask import Flask, request, render_template, make_response, session, redirect, url_for
import os
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
import pickle
warnings.filterwarnings('ignore')
from feature import FeatureExtraction

file = open("pickle/model.pkl","rb")
gbc = pickle.load(file)
file.close()


app = Flask(__name__)
# Secret key required for session. Use env var in production.
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key_change_me")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        obj = FeatureExtraction(url)
        x = np.array(obj.getFeaturesList()).reshape(1,30)

        y_pred = gbc.predict(x)[0]
        # 1 is safe, -1 is unsafe
        y_pro_phishing = gbc.predict_proba(x)[0,0]
        y_pro_non_phishing = gbc.predict_proba(x)[0,1]

        # Store result once in session, then redirect (PRG pattern)
        session['result'] = {
            'xx': round(y_pro_non_phishing, 2),
            'url': url
        }
        return redirect(url_for('index'))

    # GET: read-once result from session; disappear on refresh
    data = session.pop('result', None)
    if data is None:
        # Provide empty xx (string) to keep JS in a clean state
        html = render_template("index.html", xx="", url="")
    else:
        html = render_template('index.html', xx=data.get('xx', -1), url=data.get('url', ''))

    resp = make_response(html)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    return resp


if __name__ == "__main__":
    app.run(debug=True)