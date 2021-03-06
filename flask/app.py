import os
import cv2
import time
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory, Response
from werkzeug.utils import secure_filename
from Camera import VideoCamera


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['mov', 'mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def detect_cars(filename):
    face_cascade = cv2.CascadeClassifier('./haar-cascades/cars.xml')
    video_path = os.path.join("./uploads", filename)
    target_video_path = os.path.join("./static", filename)
    time.sleep(30)
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    out = cv2.VideoWriter('output.mp4',fourcc, 15.0, (1280,360))
    vc = cv2.VideoCapture(video_path)
    if vc.isOpened():
        rval , frame = vc.read()
    else:
        rval = False
    
    frameIndex = 0
    while True:
        frameIndex += 1
        rval, frame = vc.read()
        if not rval: break
        
        frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
        cars = face_cascade.detectMultiScale(frame, 1.1, 2)
    
        ncars = 0
        for (x,y,w,h) in cars:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            ncars = ncars + 1
 

        out.write(frame)
    
    vc.release()
    out.release()
    cv2.destroyAllWindows()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                os.makedev(app.config['UPLOAD_FOLDER'])
            except:
                pass
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('watch_file',
                                    filename=filename))
    return render_template('index.html')

                    
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)



@app.route('/watch')
@app.route('/watch/<filename>')
def watch_file(filename=None):
    return render_template('watch.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/camera')
def traffic():
    return render_template('camera.html')


@app.route('/slides')
def presentation():
    return render_template('slides.html')