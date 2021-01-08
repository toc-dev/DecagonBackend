"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, render_template
app = Flask(__name__)
import requests
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def dashboard():
    """Renders a sample page."""
    res = requests.get("https://randomuser.me/api/")
    if res.status_code == 200:
        data = res.json()
        print(data.keys())
        #name, adress, phone number, date joined
        for k in data['results']:
            name = k['name']#['title'] + ' ' + k['name']['first'] + ' ' + k['name']['last']
            email = k['email']
            phone = k['phone']
            cell = k['cell']
            registered = k['registered']['date']

    return render_template("dashboard.html", name=name, email=email, phone=phone, cell=cell, registered=registered)


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
