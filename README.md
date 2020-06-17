# Server instructions (to be used with front-end react application)

#### run 'export FLASK_APP=app.py' in console where the app.py file is
#### run 'flask run' in the same console to start the server
#### if you recieve an error and can not start the server use the command 'lsof -i :5000'
#### to see what is already running on port 5000 and kill it using 'kill -9 pid' command and use 'flask run' again

### Several dependencies are not installed using 'pip3 install' requirements.txt file you have to install them manually and remove them from requirement.txt file after their manual installation becuase the automatic file installation using 'pip3 install' makes several systems crash

### xlxswriter and editdistance also need to be installed using 'pip3 install' because for some reason they were not captured in requirements file using the freeze package to capture the requirements.

# Demo

### In the demo file I have set up a basic structure where you can use the TR function for your own mappings you should store your own test.jpg image in the TRM-backend directory before running the TR function with the mappings for that test.jpg image. This work was never finalized due to lack of access to a strong enough a GPU server to connect the table structure extraction pipeline to TRM-backend. If you ever get to carry this project forward try to map the main_copy.py, piping_copy.py, demo.py onto main.py, piping.py, app.py(TR function) respectively this would make the sever run even for new images. Right now the sever runs on main.py, piping.py and app.py files.
#### For now we only tested the mappings of a single image which we got the maps of from running Table extractor on google colab.
#### you are also going to need to set up the Google-text-recognition api for printed texts you can follow the instructions for setting it up following their own instruction at : https://cloud.google.com/vision/docs/ocr#vision_text_detection_gcs-python