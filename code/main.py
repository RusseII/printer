import os
from db import db #import my database connection class
import subprocess
from flask import Flask,flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
            Namespace

UPLOAD_FOLDER = 'upload_folder/'
ALLOWED_EXTENSIONS = set(['md','doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

async_mode = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'] )

def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db().query("UPDATE stats SET print_jobs = print_jobs + 1")
            newprint()
            subprocess.call('/home/pi/git/printer/code/scripts/print.sh upload_folder/'+ filename, shell=True)
            return "Your document has printed!"
        
        elif (allowed_file(file.filename)==False):
            return "INVALID FILETYPE NOTHING WAS PRINTED \n allowed types: 'md','doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'"

            #PRINT THE FILE!
            #printing code here!
    db().query("UPDATE stats SET visits = visits + 1")
    newvisitor()
    return render_template("index.html",async_mode=socketio.async_mode)

@socketio.on('loaded')
def page_load():
    newvisitor()
    newprint()

def newvisitor():
    visitors = db().query("SELECT visits FROM stats")[0][0]
    socketio.emit('visitor_update',
            {'data': visitors})
    print visitors
    return

def newprint():
    prints = db().query("SELECT print_jobs FROM stats")[0][0]
    socketio.emit('print_job_update',
            {'data': prints})
    return

if __name__ == "__main__":
    socketio.run(app, debug=True) 
