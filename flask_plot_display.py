from flask import Flask, render_template
import os
import time

working_dir = os.getcwd()


from flask import Flask, render_template, send_file
import os

app = Flask(__name__, template_folder=os.path.join(working_dir,'templates'))
@app.route('/')
def index():
    return render_template('plot.html', current_time=time.time())

@app.route('/plots/<filename>')
def plots(filename):
    response = send_file(os.path.join(os.getcwd(), 'plots', filename))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
