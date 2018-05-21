#!/usr/bin/env python

from flask import Flask, render_template, request
from genealogy_lib import graphviz

# This is a tinkertoy web app. Please enjoy.

# Here we make our application; we'll use this to set routes, among other
# things.
app = Flask(__name__)
# For now we're manually turning on `debug`; we like this for a few
# reasons. Chief among them: much better logging; "hot reloading," in which
# changes to our code will show up without having to stop and restart the
# server.
app.debug = True


# This is a "route" -- it tells the http server what URLs it can respond to
# (technically, we're defining "resources"). This route responds to "/", which
# is the "root" of our website. "/" is what you get implicitly if you go to,
# say "www.google.com" -- google.com is the "host", and with nothing else
# specified you get "/".
@app.route('/')
@app.route('/index.html')
def index():
    return app.send_static_file('html/graph.html')

@app.route('/get_plot', methods=['POST'])
def plot_thingy():
    #print(form.args.get('fname'))
    print(request.form)
    print(request.form.get('lname'))
    return app.send_static_file('svg/example_graph.svg')

def run_server_publicly():
    app.run(host='0.0.0.0')