from flask import Flask, render_template, send_from_directory, request, send_file
from werkzeug import secure_filename
import os
import util
import multiprocessing
from multiprocessing import Pool
import pandas as pd
from classes import CSVChunkInformation
import shutil

app = Flask(__name__)

# this part is used to find file path based on their url path
@app.route('/<path:path>')
def relation(path):
	# get the current app location
	app_root = os.path.dirname(os.path.abspath(__file__))
	# redirect path for html files
	if path.endswith('.html'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/templates/'+ filename)
	elif path.endswith('.css'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/templates/css/', filename)
	elif path.endswith('.js'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/templates/js/', filename)
	elif path.endswith('.gif'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/templates/images/', filename)
	elif path.endswith('.jpg'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/templates/images/', filename)
	elif path.endswith('.png'):
		filename = path.rsplit('/',1)[1]
		return send_from_directory(app_root + '/data/', filename)



# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
# only csv files are allowed
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index_page():
	return render_template("index.html")

@app.route('/contact')
def contact_page():
    return render_template("contact.html")


# Route that will process the file upload
@app.route('/upload/', methods=['POST', "GET"])
def upload():
	if request.method == "POST":
	    # Get the name of the uploaded file
	    file = request.files['file']
	    # Check if the file is one of the allowed types/extensions
	    if file and allowed_file(file.filename):
	        # Make the filename safe, remove unsupported chars
	        filename = secure_filename(file.filename)
	        # Move the file form the temporal folder to
	        # the upload folder we setup
	        app_root = os.path.dirname(os.path.abspath(__file__))
	        download_dir = app_root + '/templates/UPLOAD_FOLDER/'
	        file.save(os.path.join(download_dir, filename))
            # need to save a backup for zoom_in
            # srcfile = download_dir + filename
            # dstdir = download_dir + 'temp_zoom_in_' + filename
            # shutil.copy(srcfile, dstdir)
	        # Redirect the user to the uploaded_file route, which
	        # will basicaly show on the browser the uploaded file
            return render_template("csv_new_metadata_confirm.html", \
	        	                   filename = filename)
	elif request.method == "GET":
		return render_template("upload.html")

@app.route('/visualization_results/upload/<filename>/', methods=['POST'])
def csv_new_upload_visualization(filename=''):
    """
    This function is designed for users to upload
    a file to visualize
    """

    # TODO
    # choose a file stored in the server 
    # grab the url of the csv file
    
    # obtain row_offset and column_offset
    csv_row_offset = request.form['row_offset']
    csv_column_offset = request.form['column_offset']

    item_name_list = []
    # get the current app location
    # app/visualization
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'
    # getItemName five variables: folder, file name, item in the csv,
    # first row offset, second row offset,  coloumn offset
    util.getItemName(download_dir, filename, item_name_list, \
                     csv_row_offset, 0, csv_column_offset)
    # remove .csv from the end of file name
    file_origin_name = filename[:-4]
    input_filename = 'temp' + filename
    file_name = filename
    
    file_path = download_dir + input_filename
    #print file_path

    cpu_num = multiprocessing.cpu_count()
    # I don't know why funcion separate_csv does not work here, I used code directly
    # and it works
    #chunk = util.separate_csv(file_path, cpu_num)
    filename = file_path
    csv_handle = pd.read_csv(filename)
    csv_len = len(csv_handle)
    if csv_len%cpu_num == 0:
        chunk_size = csv_len/cpu_num
    elif csv_len%(cpu_num-1) == 0:
        chunk_size = (csv_len/(cpu_num-1))-1
    else:
        chunk_size = csv_len/(cpu_num-1)
    chunk=[None]*cpu_num
    count=0
    for chunk_piece in pd.read_csv(filename, chunksize=chunk_size):
        chunk[count] = chunk_piece
        count = count+1
    # print chunk[0]
    #
    column_bool = [1]*len(csv_handle.columns)

    x_scale = util.x_date_max_min_of_csv(filename)
    y_scale = util.y_max_min_of_csv(filename,column_bool)



    # create a list of input class objects for the pool
    input_objects = [None]*cpu_num
    for i in range(cpu_num):
        input_objects[i] = CSVChunkInformation(file_origin_name,i,chunk[i],x_scale,y_scale,column_bool)

    # test
    # cpu_num = 
    # separate work into cpu_number pieces
    pool = Pool(cpu_num)
    pool.map(util.plot, input_objects)
    #close pool
    pool.close()
    pool.join()
    # combine temp imgs and delete temp imgs
    temp_img_dir = app_root + '/data/img/'
    #temp_img_name = 'temp_fig_'+file_origin_name+'_0.png'
    result_img_name = file_origin_name+'_result.png'
    result_img_path = temp_img_dir+'../'+result_img_name
    util.combine_delete_image(temp_img_dir, result_img_path)
    return render_template('csv_new_visualization_results.html', \
                           item_name_list=item_name_list, \
                           input_filename=result_img_name, \
                           filename = file_name)


@app.route("/CSV_New/<update_info>/<filename>/CSVNewUpdate/", methods=['GET'])
def csv_new_image_update(update_info='',filename=''):
    # turn update_info into array
    # the initial 1 is for the first column, date
    column_bool = [1]
    for i in range(len(update_info)):
        column_bool.append(int(update_info[i]))
    #get csv file name
    file_csv_name = filename.split('_result')[0] + '.csv'
    img_name = filename
    #print img_name
    # kind of repeat need to create a function
    # remove .csv from the end of file name
    file_origin_name = filename.split('_result')[0]
    input_filename = 'temp_zoom_in_' + file_origin_name + '.csv'
    #print 'aaaaaaaaaaaaaaaaaaaaaaa'
    #print file_origin_name
    #print input_filename
    
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'
    file_path = download_dir + input_filename
    #print file_path

    cpu_num = multiprocessing.cpu_count()
    # I don't know why funcion separate_csv does not work here, I used code directly
    # and it works
    #chunk = util.separate_csv(file_path, cpu_num)
    filename = file_path
    csv_handle = pd.read_csv(filename)
    csv_len = len(csv_handle)
    if csv_len%cpu_num == 0:
        chunk_size = csv_len/cpu_num
    elif csv_len%(cpu_num-1) == 0:
        chunk_size = (csv_len/(cpu_num-1))-1
    else:
        chunk_size = csv_len/(cpu_num-1)
    chunk=[None]*cpu_num
    count=0
    for chunk_piece in pd.read_csv(filename, chunksize=chunk_size):
        chunk[count] = chunk_piece
        count = count+1
    # print chunk[0]

    x_scale = util.x_date_max_min_of_csv(filename)
    y_scale = util.y_max_min_of_csv(filename,column_bool)

    # create a list of input class objects for the pool
    input_objects = [None]*cpu_num
    for i in range(cpu_num):
        input_objects[i] = CSVChunkInformation(file_origin_name,i,chunk[i],x_scale,y_scale,column_bool)

    # separate work into cpu_number pieces
    pool = Pool(cpu_num)
    pool.map(util.plot, input_objects)
    #close pool
    pool.close()
    pool.join()
    temp_img_dir = app_root + '/data/img/'
    temp_img_name = 'temp_fig_'+file_origin_name+'_0.png'
    result_img_name = file_origin_name+'_result.png'
    result_img_path = temp_img_dir+'../'+result_img_name
    util.combine_delete_image(temp_img_dir, result_img_path)
    #
    #print "aaaaaaaaaaaaaa  "+img_name
    return send_file('data/'+img_name,mimetype='image/png')

@app.route("/CSV_New/<update_info>/<filename>/<imgname>/zoomOut/", methods=['GET'])
def csv_new_image_zoomOut(update_info='',imgname='',filename=''):
    # recover temp_zoom_in file from temp file
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'
    srcfile = download_dir + filename
    dstdir = download_dir + 'temp_zoom_in_' + filename
    shutil.copy(srcfile, dstdir)

    # turn update_info into array
    # the initial 1 is for the first column, date
    column_bool = [1]
    for i in range(len(update_info)):
        column_bool.append(int(update_info[i]))
    #get csv file name
    file_csv_name = filename
    #print 'aaaaaaaaaaaaaaaaaaaaa'
    #print filename
    img_name = imgname
    #print img_name
    # kind of repeat need to create a function
    # remove .csv from the end of file name
    file_origin_name = filename.split('.')[0]
    input_filename = 'temp_zoom_in_' + file_origin_name + '.csv'
    #print 'aaaaaaaaaaaaaaaaaaaaaaa'
    #print file_origin_name
    #print input_filename
    

    file_path = download_dir + input_filename
    #print file_path

    cpu_num = multiprocessing.cpu_count()
    # I don't know why funcion separate_csv does not work here, I used code directly
    # and it works
    #chunk = util.separate_csv(file_path, cpu_num)
    filename = file_path
    csv_handle = pd.read_csv(filename)
    csv_len = len(csv_handle)
    if csv_len%cpu_num == 0:
        chunk_size = csv_len/cpu_num
    elif csv_len%(cpu_num-1) == 0:
        chunk_size = (csv_len/(cpu_num-1))-1
    else:
        chunk_size = csv_len/(cpu_num-1)
    chunk=[None]*cpu_num
    count=0
    for chunk_piece in pd.read_csv(filename, chunksize=chunk_size):
        chunk[count] = chunk_piece
        count = count+1
    # print chunk[0]

    x_scale = util.x_date_max_min_of_csv(filename)
    y_scale = util.y_max_min_of_csv(filename,column_bool)

    # create a list of input class objects for the pool
    input_objects = [None]*cpu_num
    for i in range(cpu_num):
        input_objects[i] = CSVChunkInformation(file_origin_name,i,chunk[i],x_scale,y_scale,column_bool)

    # separate work into cpu_number pieces
    pool = Pool(cpu_num)
    pool.map(util.plot, input_objects)
    #close pool
    pool.close()
    pool.join()
    temp_img_dir = app_root + '/data/img/'
    temp_img_name = 'temp_fig_'+file_origin_name+'_0.png'
    result_img_name = file_origin_name+'_result.png'
    result_img_path = temp_img_dir+'../'+result_img_name
    util.combine_delete_image(temp_img_dir, result_img_path)
    #
    #print "aaaaaaaaaaaaaa  "+img_name
    return send_file('data/'+img_name,mimetype='image/png')


# this part is for zoom in function
@app.route('/visualization_results/zoom_in/<update_info>/<start_per>/<end_per>/<filename>/', methods=['GET'])
def csv_new_zoom_in_visualization(filename='',update_info='',start_per=0,end_per=0):
    # turn update_info into array
    # the initial 1 is for the first column, date
    column_bool = [1]
    for i in range(len(update_info)):
        column_bool.append(int(update_info[i]))

    # get the current app location
    # app/visualization
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'

    #temp_file = download_dir + 'temp'+filename
    #file_handle = open(temp_file)
    #item_name_list = file_handle.readline().split(',')
    #print item_name_list
    #file_handle.close()

    # remove .csv from the end of file name
    file_origin_name = filename[:-4]
    input_filename = "temp_zoom_in_" + filename

    # this is the zoomed in file name
    file_path = download_dir + 'temp_zoom_in_'+filename
    original_filename = filename
    filename = file_path
    x_scale = util.x_date_max_min_of_csv(filename)


    # TODO x_axis_min and max
    # get the value of start and end
    imgpath = app_root + '/data/' + file_origin_name +'_result.png'
    start_per = float(start_per)
    end_per = float(end_per)
    date_min_str = util.convert_date_format(x_scale[1].strftime("%m/%d/%Y %H:%M"))
    date_max_str = util.convert_date_format(x_scale[0].strftime("%m/%d/%Y %H:%M"))
    start, end = util.getX_RealValues(imgpath,\
                                      date_min_str, \
                                      date_max_str, \
                                      start_per, \
                                      end_per)
    #print 'aaaaaaaaaaaabbbbbbbbbbbbbbbbbbbb'
    #print start
    #print end
    #print date_min_str
    #print date_max_str
    # this function will create a temp file named "temp_zoom_in_"+filename
    util.extract_csv(original_filename,start,end)
    # do this again, coz need to find the date min and max for the extracted data
    x_scale = util.x_date_max_min_of_csv(filename)
    #print date_min_str
    #print date_max_str

    cpu_num = multiprocessing.cpu_count()
    # I don't know why funcion separate_csv does not work here, I used code directly
    # and it works
    #chunk = util.separate_csv(file_path, cpu_num)
    csv_handle = pd.read_csv(filename)
    csv_len = len(csv_handle)
    # decide chunk_size
    if csv_len%cpu_num == 0:
        chunk_size = csv_len/cpu_num
    elif csv_len%(cpu_num-1) == 0:
        chunk_size = (csv_len/(cpu_num-1))-1
    else:
        chunk_size = csv_len/(cpu_num-1)
    chunk=[None]*cpu_num
    count=0
    for chunk_piece in pd.read_csv(filename, chunksize=chunk_size):
        chunk[count] = chunk_piece
        count = count+1
    # print chunk[0]
    # 
    #column_bool = [1]*len(csv_handle.columns)

    y_scale = util.y_max_min_of_csv(filename,column_bool)

    # create a list of input class objects for the pool
    input_objects = [None]*cpu_num
    for i in range(cpu_num):
        input_objects[i] = CSVChunkInformation(file_origin_name,i,chunk[i],x_scale,y_scale,column_bool)

    #if input_objects[cpu_num].chunk_piece

    # test
    #print input_objects[1].chunk_piece.columns
    # cpu_num = 
    # separate work into cpu_number pieces
    pool = Pool(cpu_num)
    pool.map(util.plot, input_objects)
    #close pool
    pool.close()
    pool.join()
    # combine temp imgs and delete temp imgs
    temp_img_dir = app_root + '/data/img/'
    #temp_img_name = 'temp_fig_'+file_origin_name+'_0.png'
    img_name = filename
    result_img_name = file_origin_name+'_result.png'
    result_img_path = temp_img_dir+'../'+result_img_name
    util.combine_delete_image(temp_img_dir, result_img_path)
    return send_file('data/'+result_img_name,mimetype='image/png')

@app.route('/downloadChosenFile/<filename>')
def download_zoom_in_part(filename):
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'
    aim_file = download_dir + "temp_zoom_in_" + filename
    #print 'aaaaaaaaaaaaaaaaaaa'
    #print aim_file
    return send_file(aim_file)


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)



#url /line chart
@app.route('/linechart')
def linechart_page():
	return render_template("linechart.html")

if __name__ == '__main__':
	app.debug = True
	app.run(host='134.197.42.136')
