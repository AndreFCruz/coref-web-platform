"""
Backend server for demo of online coreference resolution.
"""

import os
os.environ['DATA_PATH'] = os.getenv('DATA_PATH', './data')

import coref.api
import json
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/api/clusters', methods=['POST'])
def clusters():
    text = request.form['document']
    model = int(request.form['model'])
    automatic = request.form['automaticMentionDetection']

    # Parse document
    if automatic == 'true':
        doc = coref.api.automatic_mention_detection(text, 'es' if model == 1 else 'pt')
    else:
        doc = coref.api.parse_manual_mentions(text)

    # Perform coreference resolution
    clusters = coref.api.cluster_mentions(doc, ['pt', 'es', 'pt-transferred'][model])
    
    # Convert sets to lists, and numpy.int to native integers, in order to be JSON serializable
    clusters = [[int(i) for i in c] for c in clusters]

    # Clusters' order is from last to first
    clusters.reverse()

    return json.dumps({
        'mentions': [m.full_mention for m in doc.mentions],
        'clusters': clusters
    })


if __name__ == '__main__':
    coref.api.set_up()

    # Start server
    app.run()