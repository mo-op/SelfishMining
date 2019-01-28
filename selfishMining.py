from forms import simulationForm
from flask import Flask, render_template, redirect, url_for, request

import sys
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app._static_folder = "static"
app.config.update(dict(SECRET_KEY="powerful secretkey", WTF_CSRF_SECRET_KEY="a csrf secret key"))

@app.route('/',methods=['GET','POST'])
def index():
  '''
  Gets the input from the form values
  '''
  form = simulationForm()
  if request.method == 'POST':
    results = 1.5
    return render_template('index.html',form=form,results=results)
  return render_template('index.html',form=form)

if __name__ == '__main__':
   app.run(debug = True)