from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from PIL import Image
import ImageEnhance
import datetime
import time
import shutil

#This function is used to get the name of each item
#and remove the offset and write the results into temp file
#The users need to remove the temp file by themselves
def getItemName(downloadDir='', filename='', itemNameList=[], rowOffset=0, rowOffset2=0, columnOffset=0):
    inputFile = open(downloadDir + filename,'r')
    itemList = []
    outputFile = open(downloadDir + 'temp' + filename, 'w+')
    # outputFile = open(downloadDir + 'input.csv', 'w+')

    #skip first rowOffset rows
    for i in range(0, int(rowOffset)):
        itemList = inputFile.readline()

    #obtain item name from the list
    #go back to the start of the file
    itemNameLine = inputFile.readline()
    itemList = itemNameLine.rstrip().split(',')

    #remove the first columnOffset elements
    for i in range(0, int(columnOffset)):
        itemList.pop(0)

    #does not work to do this: itemNameList = itemList
    #should use the following method
    for item in itemList:
        itemNameList.append(str(item))

    #skip second rowOffset rows
    for i in range(0, int(rowOffset2)):
        itemList = inputFile.readline()

    #add the item name list into csv file
    tempList = []
    tempList = itemNameLine.split(',')
    outputFile.write(','.join(tempList))

    #skip first columnOffset columns
    #this is used to get every line of this file
    for line in inputFile:
        tempList = line.split(',')
        for i in range(0, int(columnOffset)):
            tempList.pop(0)        
        outputFile.write(','.join(tempList))
        tempList = []

    #close file
    inputFile.close()
    outputFile.close()
    # back up temp file with the name temp_zoom_in_XX
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'
    srcfile = download_dir + filename
    dstdir = download_dir + 'temp_zoom_in_' + filename
    shutil.copy(srcfile, dstdir)


# this function will return a list of max and min of a csv file
# return result [max,min]
def y_max_min_of_csv(filename='', column_bool=[]):
    csv_handle = pd.read_csv(filename)
    temp_min = []
    temp_max = []
    # range from 1 not 0, because I want to skip first column "date"
    for count in range(1, len(csv_handle.columns)):
        if column_bool[count] == 1:
            temp_min.append(min(csv_handle[csv_handle.columns[count]]))
            temp_max.append(max(csv_handle[csv_handle.columns[count]]))
    result = []
    result.append(max(temp_max))
    result.append(min(temp_min))
    return result

# return results [max,min]
# for this version, I treat the first column is date
def x_date_max_min_of_csv(filename=''):
    csv_handle = pd.read_csv(filename)
    len_date = len(csv_handle)
    datemin = csv_handle[csv_handle.columns[0]][0]
    datemax = csv_handle[csv_handle.columns[0]][len_date-1]
    # numpy datetime64 does not work for set_xlim, should change it into datetime
    datemin = pd.to_datetime(datemin).to_pydatetime()
    datemax = pd.to_datetime(datemax).to_pydatetime()
    date_result = []
    date_result.append(datemax)
    date_result.append(datemin)
    return date_result


# app_root='/home/scidb/Desktop/vw_project/vwplatform/app/templates/visualization/img/temp_img/'
# this function is used to combine images and delete the 
# temp_img_name is one of the temp image name
# result_img_name is the result img name, this should be a png file
def combine_delete_image(path='', result_img_name=''):
    listing = os.listdir(path)
    # print path
    #new_img = Image.open(path + temp_img_name) 
    new_img = Image.new("RGBA", (800, 600), "white") 
    for file in listing:
        im = Image.open(path + file)  
        #print file + os.linesep 
        new_img = Image.blend(im, new_img, 2.0)
        new_img = Image.blend(im, new_img, 0.5)

    enhancer = ImageEnhance.Color(new_img)
    new_img = enhancer.enhance(3)
    enhancer = ImageEnhance.Contrast(new_img)
    new_img = enhancer.enhance(2)
    new_img.save(result_img_name,"PNG")
    # delete the temp images
    
    # for file in listing:
    #     # set delete information here
    #     if file.endswith('.png'):
    #         os.remove(path+file)
    
    return

def plot(args):
    i = args
    x_scale = i.x_max_min
    y_scale = i.y_max_min
    filename = i.filename
    chunk_count = i.chunk_count
    chunk_piece = i.chunk_piece

    fig, ax = plt.subplots()

    column_bool = i.column_bool
    # x axis, for this version, x should be time
    x_axis_name = chunk_piece.columns[0]
    x_axis = pd.to_datetime(chunk_piece[x_axis_name])
    x_axis = np.array(x_axis)


    column_num = len(chunk_piece.columns)
    # column_num -1 because need to remove x-axis
    y_axises = [None] * (column_num-1)
    for y_count in range(1,column_num):
        y_axises[y_count-1] = np.array(chunk_piece[chunk_piece.columns[y_count]])

    # auto fix x_axis label's angle
    fig.autofmt_xdate()
    # valid column num
    valid_column_num = 0
    for m in column_bool:
        if m == 1:
            valid_column_num = valid_column_num + 1
    cmap = plt.get_cmap('gnuplot')
    colors = [cmap(m) for m in np.linspace(0, 1, valid_column_num)]
    # There are only four types of line chart
    line_style = ['-', '--', '-.', ':']
    #print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    # plot figure
    for y_count in range(1,column_num):
        if column_bool[y_count] == 1:
            line_style_count = (y_count-1)%len(line_style)
            column_name = chunk_piece.columns[y_count]
            #ax.plot_date(x_axis,y_axises[y_count-1],ls=line_style[line_style_count],fmt='',label='column_name',color=colors[y_count-1])
            ax.plot(x_axis,y_axises[y_count-1],ls=line_style[line_style_count],label=column_name,color=colors[(y_count-1)%valid_column_num])
            
    # set x axis scale
    ax.set_xlim([x_scale[1], x_scale[0]])
    # set y axis scale
    ax.set_ylim([y_scale[1], y_scale[0]])

    # this is for legends
    # http://stackoverflow.com/questions/10824156/matplotlib-legend-location-numbers
    legend = ax.legend(loc='upper right', shadow=True)
    #print 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    #plt.legend()
    plt.xlabel("Day")
    plt.ylabel("Count")

    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('small')

    for label in legend.get_lines():
        label.set_linewidth(1.5)  # the legend line width

    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/data/img/'

    plt.title(filename)
    fig.savefig(download_dir+'temp_fig_'+filename+'_{}.png' .format(chunk_count))

def extract_csv(filename,start,end):
    # this is for the csv file location
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/templates/UPLOAD_FOLDER/'
    file_handle =  open(download_dir+'temp'+filename,'r')
    temp_file_handle = open(download_dir+'temp_zoom_in_'+filename,'w')
    # add title line into temp file
    title_line = file_handle.readline()
    temp_file_handle.write(title_line)
    start_writing = False
    for temp_line in file_handle:
        if start_writing==False and temp_line.split(',')[0]==start:
            start_writing = True
        if start_writing == True:
            temp_file_handle.write(temp_line)
        if temp_line.split(',')[0]==end:
            break
    file_handle.close()
    temp_file_handle.close()

# Jose part starts here
def most_common(lst):
    return max(set(lst), key=lst.count)

def getGraphStartEndPixels(imgpath=''):
   im = Image.open(imgpath) 
   width, height = im.size
   pix=im.load()

   x,y = width-1,(height-1)/2
   y_min, y_max = y-50, y+50
   xValueList = []
   # make sure y_min and y_max are int
   y_min = int(y_min)
   y_max = int(y_max)
   for y in range(y_min, y_max):
     x = width-1
     while x>=0:
        red, blue, green, alpha = pix[x,y]
        # this part may have a problem because in the enhanced image, black is not (0,0,0)
        if (red <= 20) and (blue <= 20) and (green <= 20) :  
           #print x
           xValueList.append(x)
           break
        x=x-1
   
   rValue = most_common(xValueList)
   print "Right side: %s" %most_common(xValueList)
   del xValueList[:]

   for y in range(y_min, y_max):
      x=0
      while x<width:
         red, blue, green, alpha = pix[x,y] 
         # this part may have a problem because in the enhanced image, black is not (0,0,0)
         if (red <= 20) and (blue <= 20) and (green <= 20) :  
            #print x
            xValueList.append(x)
            break
         x=x+1

   lValue = most_common(xValueList)
   #print "Left side: %s" %most_common(xValueList)
   return (lValue, rValue)


def diff_dates(date1, date2):
    return abs(date2-date1).days

# function to get real x axis values for dates
def getX_RealValues(imgpath,x_axis_min,x_axis_max,user_x1_percent,user_x2_percent):

  #checking for errors 
   if(isinstance(x_axis_min, basestring)):
      if(not isinstance(x_axis_max, basestring)):
         return ('ERROR','ERROR')
   elif(isinstance(x_axis_max, basestring)):
      if(not isinstance(x_axis_min, basestring)):
         return ('ERROR','ERROR')
   elif(type(x_axis_min) == float):
      if(not type(x_axis_max) == float):
        return ('ERROR','ERROR')
   elif(type(x_axis_max) == float):
      if(not type(x_axis_min) == float):
         return ('ERROR','ERROR')
   else:
      return ('ERROR','ERROR')

   # assign bigger %tage to user_x2_percent
   if (user_x1_percent > user_x2_percent):
     user_x1_percent, user_x2_percent = user_x2_percent, user_x1_percent
   
  
   if(isinstance(x_axis_min, basestring) and isinstance(x_axis_max, basestring)):
      # convert string to date
      x_axis_min = datetime.datetime.strptime(x_axis_min, '%m/%d/%Y %H:%M')
      x_axis_max = datetime.datetime.strptime(x_axis_max, '%m/%d/%Y %H:%M')
      
      #Get the difference between dates in minutes. So convert the dates to unix timestamps 
      d1_ts = time.mktime(x_axis_min.timetuple()) 
      d2_ts = time.mktime(x_axis_max.timetuple())

   
   #Find the graph's starting and ending pixel values.
   graph_start_pixel, graph_end_pixel = getGraphStartEndPixels(imgpath)
   graph_xValues= graph_end_pixel - graph_start_pixel

   #user input %tage real pixel values.
   x1_pixel = (user_x1_percent * 800)/100
   x2_pixel = (user_x2_percent * 800)/100

   if (((x1_pixel < graph_start_pixel)and(x2_pixel < graph_start_pixel)) or ((x1_pixel > graph_end_pixel)and (x2_pixel > graph_end_pixel))):
      return ('MARGIN', 'MARGIN')
   else:
      if(x1_pixel < graph_start_pixel): 
         x1_pixel = graph_start_pixel
      if(x2_pixel > graph_end_pixel): 
         x2_pixel = graph_end_pixel
       
      #subtract the right margin pixels from user input pixel values
      x1_pixel =  x1_pixel - graph_start_pixel
      x2_pixel =  x2_pixel - graph_start_pixel


   if(type(x_axis_min) == float) and (type(x_axis_max) == float):
      totalXValues = float(x_axis_max) - x_axis_min
   else:
      totalXValues = int(d2_ts - d1_ts) / 60
      #totalXValues = diff_dates(x_axis_max, x_axis_min)
   
   #print totalXValues   

   if totalXValues > 0:
      onePixelValue = float(totalXValues)/graph_xValues
     
      x1_num = (x1_pixel * onePixelValue)
      x2_num = (x2_pixel * onePixelValue)

      if(type(x_axis_min) == float)or(type(x_axis_max) == float):
         x1_value = x_axis_min + x1_num
         x2_value = x_axis_min + x2_num
      else:
         x1_value = x_axis_min + datetime.timedelta(minutes = x1_num)
         x2_value = x_axis_min + datetime.timedelta(minutes = x2_num)
         #Convert the datetime object into %m/%d/%Y %H:%M format
         x1_value= x1_value.strftime("%m/%d/%Y %H:%M")
         x2_value= x2_value.strftime("%m/%d/%Y %H:%M")
         #modifying the minutes value to 00 
         x1_value = str(x1_value).split(':')[0] + ':00' 
         x2_value = str(x2_value).split(':')[0] + ':00'
         x1_value = convert_date_format(x1_value)
         x2_value = convert_date_format(x2_value)
      return (x1_value, x2_value)
# Jose part ends here

# need to convert 07/03/2015 00:00 these types of time into
# 7/3/2015 00:00
def convert_date_format(date_string):
    # process 0X/0X/XXXX XX:XX
    temp_list = date_string.split('/')
    temp_list[0] = str(int(temp_list[0]))
    temp_list[1] = str(int(temp_list[1]))
    temp_str = '/'.join(temp_list)
    # process X/X/XXXX 0X:XX
    temp_list = temp_str.split(' ')
    temp = temp_list[1].split(':')
    temp[0] = ':'.join([str(int(temp[0])),temp[1]])
    temp_str = ' '.join([temp_list[0],temp[0]])
    return temp_str
