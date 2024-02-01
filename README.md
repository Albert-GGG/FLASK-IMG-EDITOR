# SMPL Image Editor

# Video demo: <https://www.youtube.com/watch?v=z6l47ms0PMw>

#### Description:

SMPL image editor (pronounced "simple") is a  web application that allows users to apply simple filters to images: Gray scale,
contours in black and white, brightness and blurring. Additionally, users can split the images in any quantity of blocks or regions
and download all the changes made to the original images.

## Libraries used

The application's backend was written in Python using the flask library, the image processing was implemented using
the OpenCv modules, the file manipulation was done with the io.BytesIO and the zipfile modules.

## Files and directories

### The project is structured by the directories "static" and "templates", the "app.py" and "funcs.py" files

### Static directory: It has the icons used in the application and the style sheets

- icon_img: Icon made in inkscape for the "SMPL Image Editor" "brand"
- "bright_sun.svg" and "bright.svg" icons obtained from: <https://icon-icons.com/es/icono/preferencias-del-sistema--brillo-bloqueo/94470>
and <https://icon-icons.com/es/icono/brillo-ida-y-vuelta-bot%C3%B3n/122314>.
- "styles.css" contains most of the styles of all the html templates (Other styles are applied directly from within the templates).

### Templates directory: Contains all the html templates that are displayed on the user's browser

- "blurring.html": The page in which the user can adjust the blurriness of an image. It shows the original image, and the modified version
on the right with the slider that modifies the image.
- "brightness.html": The page that shows the original image and the modified one with the slider in the bottom right to increase or
decrease the brightness of the image.
- "contours.html": Shows the original image and the contours version.
- "gray_scale.html": Shows the original image and the gray_scale image.
- "layout.html": The layout from which all the templates inherit. It contains the navbar with a link to each filter, the logo and the
title. It also contains the java script code.
- "split.html": The html that displays the original image with the form that contains the rows and columns inputs in which the image is
split.
- "welcome.html": The index html that shows the user the uploaded image and one button for each of the filters that load the specified
template with the image already loaded. NOTE: The navbar links load the templates with no image loaded into the memory, whereas the
links of the index html open the templates with the image already loaded.

### Python files

- "app.py": Contains all the functionality of the backend using flask routes and functions.

- "funcs.py": Contains all the opencv functions used to apply the filters to the images.
  - Gray scale
  - Contours (canny filter)
  - Brightness (adds or subtracts 0-100 values from pixels)
  - Blurriness (gets the blurred image with kernel of size k)
  - Split (divides the image in blocks with the specified number of rows and columns)

## Overall functionality

The users can upload an image through a file form that is present in all the html pages. This image is converted directly into a numpy
array to be manipulated with the opencv modules and is stored in memory as a global variable. No disk space is ever used since the images
and their modified versions are only manipulated and downloaded by the user himself. An url for the uploaded image is generated and stored
in memory to be used when loading the html templates (encoded in .jpg and used as a byte array). Once the image is loaded into memory, the
user can a apply any filter to it by clicking the "convert" buttons or by dragging the sliders depending on the html they are in. This sends
'GET' or 'POSTS' requests to the backend routes that update a global variable with the modified version of the opencv image as well as the
url for it to be shown in the templates. When the user clicks the "download" buttons, the modified opencv version of the image loaded in the
global variable is encoded as a .jpg image, converted to binary data with the io.BytesIO module and sent to the user to be downloaded using
the send_file function from flask.

### Data refresh

To reload the pages with data sent from the user, there is a complete refresh when using the welcome, gray scale, contours and split templates.
The templates where reloaded with the global url variables found in memory by using the jinja syntax.
In the case of the brightness and blurriness templates, AJAX was used to fetch the new modified version of the image whenever the user dragged
the sliders. This way, only the modified image was refreshed in real time.

### Download the split image

To download the split image, a zip file is created in memory using the io.BytesIO module and all the regions or blocks of the image are encoded,
converted to bytes and added to the zip file that is then downloaded by the user.

## Visual design and structure

The main goal of the design in the visual aspect, was to create templates with only the necessary elements, colors and words that would make the
use of the app an easy task. The bootstrap library was used for the buttons and the navbar, whereas for the rest of the elements, plain HTML and CSS were used. All the templates basically consist of a space to show the original uploaded image and a space to show the modified version with
the chosen filter, the convert buttons, the sliders and the download buttons. Finally, the pages were designed to responsive with all screen sizes
through the use of flexbox and media queries in CSS.

## Help and resources

- Range slider usage and customization: <https://blog.hubspot.com/website/html-slider>
- AJAX: <https://programacionymas.com/blog/ajax-fetch-api-ejemplo>
- Eliminate cache from responses: <https://stackoverflow.com/questions/11997051/flask-url-for-no-cache?rq=3>
- In-memory zip file: <https://stackoverflow.com/questions/2463770/python-in-memory-zip-library>
- zipfile docs: <https://docs.python.org/3/library/zipfile.html>
- Download zip file from memory: <https://stackoverflow.com/questions/67785867/how-to-send-zip-file-with-send-file-flask-framework>
- Bootstrap docs: <https://getbootstrap.com>
- Create urls with url_for: <https://stackoverflow.com/questions/7478366/create-dynamic-urls-in-flask-with-url-for>
- Uploading files with flask: <https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/>
- Site inspiration: <https://pinetools.com/c-images/>
- CSS flexbox: <https://www.youtube.com/watch?v=3YW65K6LcIA&t=1274s>
- Display openCv images on the browser: <https://www.youtube.com/watch?v=ywaSiIf1C2w&t=722s>
- Convert openCv image to bytes: <https://jdhao.github.io/2019/07/06/python_opencv_pil_image_to_bytes/>
