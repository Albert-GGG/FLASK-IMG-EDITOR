import os
from flask import Flask, flash, redirect, render_template, request, Response, url_for, send_file
from flask_uploads import UploadSet, IMAGES, configure_uploads
import cv2
from funcs import *
import numpy
from werkzeug.utils import secure_filename
import io
import zipfile
import time

# Initialize empty variables for uploaded image and modified image
up_image = None
mod_image = None
is_inverted = False

url_image = None
url_mod = None

# Initialize flask application and folder for temporary saved image
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecKey9402#'

# Add folder to save image in disk:
app.config['UPLOADED_PHOTOS_DEST'] = 'uploaded_imgs'

# Initialize parameters for allowed uploads (images only)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


# Only allow image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Send to index page when app s run or by clicking the logo in the navbar
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    initialize()    
    return render_template('welcome.html')


# Verify the uploaded file (flask documentation)
def up_form():

    # Intialize global images and urls to None
    initialize()
    global up_image, url_image
   
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

        # After verifying upload, convert the image directly to cv2 image (numpy array) and store it in memory instead of disk
        up_image = cv2.imdecode(numpy.fromstring(request.files['file'].read(), numpy.uint8), cv2.IMREAD_UNCHANGED) 
        # Obtain url for the uploaded or original image to pass it to the templates
        url_image = url_for('upload_img')
        

# Route that is accessed when an image is uploaded from any html page
@app.route('/send_form', methods=['GET', 'POST'])
def send_form():
    if request.method == 'POST':
        # Verify upload and store image in memory as np array
        up_form()
        for name in request.form:
            template = name

    # Redirect to the same page by refreshing the template with the new image url variable
    return redirect(url_for('load_page', page=template))
    

# Obtain url of the original uploaded image
@app.route("/upload_img", methods=['GET', 'POST'])
def upload_img():
    return Response(convert(up_image), mimetype="multipart/x-mixed-replace; boundary=frame")

# Obtain the url of the modified image in memory without cache data
@app.route('/get_url_mod', methods=['GET', 'POST'])
def get_url_mod():
    resp = Response(convert(mod_image), mimetype="multipart/x-mixed-replace; boundary=frame")
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp

# Function that converts cv2 image to a readable format to be shown in the "layout.html" template
def convert(img):
    flag, encoded = cv2.imencode('.jpg', img)
    if flag:
         return(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded) + b'\r\n')


# Load specified page template with current variables in memory
@app.route("/load_page/<page>", methods=['GET', 'POST'])
def load_page(page):
    return render_template(f'{page}', file_url=url_image, file_url_ad=url_mod)


# Delete current original image and modified image in memory and their url's
def initialize():
    global up_image, mod_image, is_inverted, url_image, url_mod
    up_image = None
    mod_image = None
    is_inverted = False
    url_image = None
    url_mod = None


# Load specified page with images already loaded into memory or without them (Welcome page links | navbar links)
@app.route("/go_to/<page>/<with_photo>", methods=['GET', 'POST'])
def go_to(page, with_photo):
    global mod_image, url_mod, is_inverted
    if with_photo == 'no':
        print('no photo')
        initialize()

    mod_image, url_mod, is_inverted = None, None, False
    return redirect(url_for('load_page', page=page))


# Convert original image in memory to gray scale and save it in the modified image global variable and its url
@app.route("/to_gray", methods=['GET', 'POST'])
def to_gray():
    global mod_image, url_mod
    if up_image is not None:
        mod_image = Grays(up_image)
        url_mod = url_for('get_url_mod')
    
    return redirect(url_for('load_page', page='gray_scale.html'))


# Convert original image in memory to the contours version and save it in the modified image global variable and its url
@app.route("/to_contours", methods=['GET', 'POST'])
def to_contours():
    global mod_image, url_mod
    if up_image is not None:
        mod_image = Contours(up_image, is_inverted)
        url_mod = url_for('get_url_mod')
    
    return redirect(url_for('load_page', page='contours.html'))


# Change the invert variable of Contours to the opposite boolean and refresh the contours page
@app.route("/invert", methods=['GET', 'POST'])
def invert():
    global is_inverted
    if mod_image is not None:
        is_inverted = not is_inverted
    return redirect(url_for('to_contours'))


# Obtain new modified image with the brigtness or blurring filters with values from the sliders
# and return the url of the new modified image
@app.route('/slider_filter', methods=['POST', 'GET'])
def update_slider():
    global mod_image, url_mod
    if up_image is not None:
        data = request.json
        current_slider = str(data.get('slider'))
        current_val = int(data.get('value'))
        print(current_slider)
        print(current_val)

        if current_slider == 'mod_bright':
            mod_image = Brightness(up_image, current_val)
        else:
            mod_image = Blurring(up_image, current_val)
        
        url_mod = url_for('get_url_mod')

        return url_mod

    return 


# Get blocks of image, convert them to binary data, add them to a zipfile and download it
@app.route('/get_split', methods=['GET', 'POST'])
def get_split():
    buf = io.BytesIO()
    if up_image is not None:
        rows = int(request.form.get('rows'))
        columns = int(request.form.get('columns'))
        regions = Split(up_image, rows, columns)

        with zipfile.ZipFile(buf, 'a', zipfile.ZIP_DEFLATED, False) as z:
            for i, reg in enumerate(regions):
                flag, encoded = cv2.imencode('.jpg', reg)
                if flag:
                    print(rows, columns)
                    z.writestr(f'Region {i}.jpg', io.BytesIO(encoded).getvalue())
            
        return Response(buf.getvalue(), mimetype='application/zip', headers={'Content-Disposition': 'attachment; filename=SPLIT_IMAGE.zip'})
        
    return redirect(request.referrer)


@app.route('/get_stripes', methods=['GET', 'POST'])
def get_stripes():
    global mod_image, url_mod
   
    if up_image is not None:
        data = request.json
        rows = int(data.get('rows'))
        columns = int(data.get('columns'))
        regions = SplitStripes(up_image, rows, columns)
        
        mod_image = mergeImg(regions)
        url_mod = url_for('get_url_mod')

        return url_mod
    
    return


# Download modified image using flask's send_file only if there is a modified in memory
@app.route('/download', methods=['GET', 'POST'])
def download():
    if mod_image is not None:
        flag, encoded = cv2.imencode('.jpg', mod_image)
        if flag:
            # Since image is not stored in a disk path, encode it as .jpg image and then to a bytes stream to send it to the user
            io_buf = io.BytesIO(encoded)

            return send_file(path_or_file=io_buf, as_attachment=True, download_name='EDITED_IMG.jpg')
        
    return redirect(request.referrer)

# Return url with no cache data
def no_cache_url(route):
    resp = app.make_response(url_for(route))
    resp.headers.add('Last-Modified', time.time())
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    resp.headers.add('Pragma', 'no-cache')

    return resp


# Run app
if __name__ == "__main__":
    app.run(debug=True)






               