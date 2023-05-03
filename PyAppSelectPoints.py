import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import pickle
import cv2
import os
import glob
import pandas as pd
import json
# import scipy.interpolate as interpolate
# import matplotlib.pyplot as plt
# from scipy.signal import savgol_filter
# from scipy.interpolate import CubicSpline
#import numpy
#from scipy.signal import medfilt
from numpy.random import randint
#import pandas as pd
import math

from datetime import datetime
#from GenRPEMesh import createRPEMesh
#from skimage import exposure
#import pyqtgraph as pg
from PyQt5.QtCore import QSettings
import time

#p = '195'
#side = 'os'

split = 497
targetsz=400# 500
OCTRectHeight = 330

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # set data directory and get list of eyes
        self.data_dir =  "c:\\Users\\Johnathan Young\\Documents\\GitHub\\AMD_data_flow\\data"
        self.set_eyes(self.data_dir)
        self.image_size = (495, 497)

        # initialise dictionary of saved coordinates
        self.points_dict = {}

        # populate eye selection dropdown
        self.widgetEyeSelection = QComboBox(self)
        for eye in self.eyes :

            self.widgetEyeSelection.addItem(eye)

        self.widgetEyeSelection.activated[str].connect(self.select_eye)

        # initialise AMD image selection
        self.widgetAMDSelection = QComboBox(self)
        self.widgetAMDSelection.activated[str].connect(self.select_AMD)

        # initialise image display to grey
        # fix height so resizing window doesn't mess up pixel coordinates
        self.DARC_image = QLabel(self)
        grey = QPixmap(self.image_size[0], self.image_size[1])
        grey.fill(QColor('darkGray'))
        self.DARC_image.setFixedHeight(self.image_size[0])
        self.DARC_image.setPixmap(grey)
        self.DARC_image.mousePressEvent = self.set_point_on_DARC
        self.AMD_image = QLabel(self)
        self.AMD_image.setPixmap(grey)
        self.AMD_image.setFixedHeight(self.image_size[0])
        self.AMD_image.mousePressEvent = self.set_point_on_AMD

        # set labels
        self.DARC_image_label = QLabel(self)
        self.AMD_image_label = QLabel(self)
        self.point_table_label = QLabel(self)
        self.DARC_image_label.setText('DARC image')
        self.AMD_image_label.setText('AMD image')
        self.point_table_label.setText('added points')
        self.DARC_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.AMD_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.point_table_label.setAlignment(QtCore.Qt.AlignCenter)

        # set up added points table
        self.point_table = QTableWidget()
        self.point_table.setRowCount(3)
        self.point_table.setColumnCount(2)
        self.point_table.setHorizontalHeaderLabels(["DARC image point", "AMD image point"])

        # set up image selection labels
        self.DARC_image_selection_label = QLabel(self)
        self.AMD_image_selection_label = QLabel(self)
        self.DARC_image_selection_label.setText('eye selection')
        self.AMD_image_selection_label.setText('AMD image selection')
        self.DARC_image_selection_label.setAlignment(QtCore.Qt.AlignCenter)
        self.AMD_image_selection_label.setAlignment(QtCore.Qt.AlignCenter)

        # set up point saving buttons
        self.layoutPointControl = QVBoxLayout()
        self.add_points_button = QPushButton(self)
        self.add_points_button.setText('add current point pair')
        self.add_points_button.clicked.connect(self.add_points)
        self.save_points_button = QPushButton(self)
        self.save_points_button.setText('save current points')
        self.save_points_button.clicked.connect(self.save_points)
        self.remove_points_button = QPushButton(self)
        self.remove_points_button.setText('remove all points')
        self.remove_points_button.clicked.connect(self.remove_points)
        self.write_points_button = QPushButton(self)
        self.write_points_button.setText('write saved points to file')
        self.write_points_button.clicked.connect(self.write_points_to_file)
        self.layoutPointControl.addWidget(self.point_table)
        self.layoutPointControl.addWidget(self.add_points_button)
        self.layoutPointControl.addWidget(self.save_points_button)
        self.layoutPointControl.addWidget(self.remove_points_button)
        self.layoutPointControl.addWidget(self.write_points_button)

        # initially cannot add, save, write or remove points
        self.add_points_button.setDisabled(True)
        self.save_points_button.setDisabled(True)
        self.remove_points_button.setDisabled(True)
        self.write_points_button.setDisabled(True)

        # set up overall layout with qgrid
        self.layout = QGridLayout()
        self.layout.addWidget(self.DARC_image_label, 0, 0)
        self.layout.addWidget(self.AMD_image_label, 0, 1)
        self.layout.addWidget(self.point_table_label, 0, 2)
        self.layout.addWidget(self.DARC_image, 1, 0)
        self.layout.addWidget(self.AMD_image, 1, 1)
        self.layout.addLayout(self.layoutPointControl, 1, 2)
        self.layout.addWidget(self.DARC_image_selection_label, 2, 0)
        self.layout.addWidget(self.AMD_image_selection_label, 2, 1)
        self.layout.addWidget(self.widgetEyeSelection, 3, 0)
        self.layout.addWidget(self.widgetAMDSelection, 3, 1)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.AMD_selected = False
        # set number of current points to 0
        self.current_n_points = 0

    # list unique eyes to be processed
    def set_eyes(self, data_dir) :

        im_dirs = os.listdir(self.data_dir)
        eyes = map(lambda x: '_'.join(x.split('_')[:2]), im_dirs)
        self.eyes = list(set(eyes))

    # display DARC eye for selected eye
    def select_eye(self, eye_str) :

        # DARC & AMD directory
        self.current_eye = eye_str
        DARC_dir = os.path.join(self.data_dir, eye_str + '_DARC')
        self.AMD_dir = os.path.join(self.data_dir, eye_str + '_AMD')
        DARC_baseline_img = glob.glob(os.path.join(DARC_dir, '*_0.png'))[0]
        self.current_DARC_file = os.path.join(DARC_dir, DARC_baseline_img)

        # set DARC image
        self.set_original_DARC_image()

        # set AMD image to blank as none is selected
        grey = QPixmap(self.image_size[0], self.image_size[1])
        grey.fill(QColor('darkGray'))
        self.AMD_image.setPixmap(grey)

        # populate AMD selection
        AMD_imgs = glob.glob(os.path.join(self.AMD_dir, '*.jpg'))
        AMD_imgs = list(map(lambda x: os.path.basename(x), AMD_imgs))
        self.widgetAMDSelection.clear()
        for AMD_img in AMD_imgs :

            self.widgetAMDSelection.addItem(AMD_img)

        # set AMD_selected to false
        self.AMD_selected = False

        # set number of current points to 0
        self.current_n_points = 0

    def select_AMD(self, AMD_str) :

        # set AMD image
        self.current_AMD = AMD_str
        self.set_original_AMD_image()
        self.current_DARC_AMD_combo = self.current_eye + '_' + AMD_str

        # set number of current points to 0
        self.current_n_points = 0

        # initialise point storage
        self.current_points = []
        self.current_DARC_point = None
        self.current_AMD_point = None

        # reset DARC image
        self.set_original_DARC_image()

        # empty table
        self.point_table.clear()
        self.point_table.setHorizontalHeaderLabels(["DARC image point", "AMD image point"])

        self.AMD_selected = True

        # draw points if necessary
        # and repopulate table
        if self.current_DARC_AMD_combo in self.points_dict.keys() :

            points = self.points_dict[self.current_DARC_AMD_combo]
            self.current_points = points
            new_AMD_img = cv2.imread(self.current_AMD_file)
            new_DARC_img = cv2.imread(self.current_DARC_file)
            for i, point_pair in enumerate(points) :

                colour = self.get_colour(i)
                new_DARC_img = cv2.resize(new_DARC_img, (self.image_size[0], self.image_size[1]))
                new_DARC_img = cv2.circle(new_DARC_img, (point_pair[0][0], point_pair[0][1]), 3, colour, -1)
                new_AMD_img = cv2.resize(new_AMD_img, (self.image_size[0], self.image_size[1]))
                new_AMD_img = cv2.circle(new_AMD_img, (point_pair[1][0], point_pair[1][1]), 3, colour, -1)

                self.point_table.setItem(i, 0, QTableWidgetItem(str(point_pair[0])))
                self.point_table.setItem(i, 1, QTableWidgetItem(str(point_pair[1])))



            self.DARC_image.setPixmap(self.convert_ndarray_to_QPixmap(new_DARC_img))
            self.AMD_image.setPixmap(self.convert_ndarray_to_QPixmap(new_AMD_img))
            self.current_n_points = 3
            # turn off save button
            self.save_points_button.setDisabled(True)
            self.remove_points_button.setDisabled(False)

        else :

            self.remove_points_button.setDisabled(True)

    def write_points_to_file(self) :

        # loop through eye combos
        for DARC_AMD_combo, points_list in self.points_dict.items() :

            # get directory to write to
            eye = '_'.join(DARC_AMD_combo.split('_')[:2])
            AMD_image_filename = '_'.join(DARC_AMD_combo.split('_')[2:])
            AMD_image_basename = os.path.splitext(AMD_image_filename)[0]
            AMD_dir = os.path.join(self.data_dir, eye +'_AMD')
            fixed_image_basename = os.path.basename(self.current_DARC_file).split('.')[0]
            out_filename = os.path.join(AMD_dir, AMD_image_basename + '_to_' + fixed_image_basename + '.json')
            DARC_points = []
            AMD_points = []
            for pair in points_list :

                DARC_points.append([pair[0][0], pair[0][1]])
                AMD_points.append([pair[1][0], pair[1][1]])

            fixed_data = {'points':DARC_points, 'filename':self.current_DARC_file, 'size':self.current_AMD_img.shape}
            moving_data = {'points':AMD_points, 'filename':self.current_AMD_file, 'size':self.current_DARC_img.shape}
            data = {'fixed img':fixed_data, 'moving img':moving_data}

            #PD_out = pd.DataFrame({'DARC x':DARC_x, 'DARC y':DARC_y, 'AMD x':AMD_x, 'AMD y':AMD_y})
            #PD_out.to_csv(out_filename, index=False)
            with open(out_filename, 'w') as outfile:
                json.dump(data, outfile)


    def set_original_AMD_image(self) :

        self.current_AMD_file = os.path.join(self.AMD_dir, self.current_AMD)
        self.current_AMD_img = cv2.imread(self.current_AMD_file)
        self.AMD_image.setPixmap(self.convert_ndarray_to_QPixmap(self.current_AMD_img))

    def set_original_DARC_image(self) :

        self.current_DARC_img = cv2.imread(self.current_DARC_file)
        self.DARC_image.setPixmap(self.convert_ndarray_to_QPixmap(self.current_DARC_img))

    def set_point_on_AMD(self, event):

        if not self.AMD_selected :

            QMessageBox.about(self, "points warning", "Cannot add points when DARC and AMD images are not both selected")

        elif self.current_n_points == 3 :

            QMessageBox.about(self, "points warning", "Cannot have more than 3 points in an image. Remove all points or select another image")

        else :

            # extract coordinate
            x = event.pos().x()
            y = event.pos().y()
            self.current_AMD_point = (x, y)

            # draw point on image
            # set colour based on whether this is first, second or third point
            colour = self.get_colour(self.current_n_points)
            new_AMD_img = self.current_AMD_img
            new_AMD_img = cv2.resize(new_AMD_img, (self.image_size[0], self.image_size[1]))
            new_AMD_img = cv2.circle(new_AMD_img, (x, y), 3, colour, -1)
            self.new_AMD_img = new_AMD_img
            self.AMD_image.setPixmap(self.convert_ndarray_to_QPixmap(new_AMD_img))

            # enable adding the points if both points are set
            if (self.current_AMD_point is not None) and (self.current_DARC_point is not None):
                self.add_points_button.setDisabled(False)

    def set_point_on_DARC(self, event):

        if not self.AMD_selected :

            QMessageBox.about(self, "points warning", "Cannot add points when DARC and AMD images are not both selected")

        elif self.current_n_points == 3 :

            QMessageBox.about(self, "points warning", "Cannot have more than 3 points in an image. Remove all points or select another image")

        else :

            # extract coordinate
            x = event.pos().x()
            y = event.pos().y()
            self.current_DARC_point = (x, y)

            # draw point on image
            # set colour based on whether this is first, second or third point
            colour = self.get_colour(self.current_n_points)
            new_DARC_img = self.current_DARC_img
            new_DARC_img = cv2.resize(new_DARC_img, (self.image_size[0], self.image_size[1]))
            new_DARC_img = cv2.circle(new_DARC_img, (x, y), 3, colour, -1)
            self.new_DARC_img = new_DARC_img
            self.DARC_image.setPixmap(self.convert_ndarray_to_QPixmap(new_DARC_img))

            # enable adding the points if both points are set
            if (self.current_AMD_point is not None) and (self.current_DARC_point is not None) :

                self.add_points_button.setDisabled(False)



    def get_colour(self, ind) :

        colour = np.zeros(3, )
        colour[ind] = 255
        return tuple(colour)

    # see https://stackoverflow.com/questions/34232632/convert-python-opencv-image-numpy-array-to-pyqt-qpixmap-image
    def convert_ndarray_to_QPixmap(self, img):
        w, h, ch = img.shape
        # Convert resulting image to pixmap
        if img.ndim == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        qimg = QImage(img.data, h, w, 3 * h, QImage.Format_RGB888)
        qpixmap = QPixmap(qimg)
        qpixmap = qpixmap.scaled(self.image_size[0], self.image_size[1])
        return qpixmap

    def add_points(self) :

        # add to points table
        self.point_table.setItem(self.current_n_points, 0, QTableWidgetItem(str(self.current_DARC_point)))
        self.point_table.setItem(self.current_n_points, 1, QTableWidgetItem(str(self.current_AMD_point)))

        # add to points list
        self.current_points.append((self.current_DARC_point, self.current_AMD_point))
        self.current_DARC_point = None
        self.current_AMD_point = None

        # increment number of added points
        self.current_n_points = self.current_n_points + 1

        # store images with added points
        self.current_DARC_img = self.new_DARC_img
        self.current_AMD_img = self.new_AMD_img

        # update buttons
        self.add_points_button.setDisabled(True)

        if self.current_n_points < 3 :

            self.remove_points_button.setDisabled(False)

        if self.current_n_points == 3 :

            self.save_points_button.setDisabled(False)

        # don't let user change AMD or eye with unsaved points added
        self.widgetAMDSelection.setDisabled(True)
        self.widgetEyeSelection.setDisabled(True)

    def save_points(self) :

        # update entry for points_dict
        self.points_dict[self.current_DARC_AMD_combo] = self.current_points

        # turn off save button
        self.save_points_button.setDisabled(True)

        # points are saved, allow change of eye/AMD
        self.widgetAMDSelection.setDisabled(False)
        self.widgetEyeSelection.setDisabled(False)

        # enable writing of saved points
        self.write_points_button.setDisabled(False)
        print(self.points_dict)

        # disable saving as points are already saved
        self.save_points_button.setDisabled(True)

    def remove_points(self) :

        #empty table
        self.point_table.clear()
        self.point_table.setHorizontalHeaderLabels(["DARC image point", "AMD image point"])

        # remove points from images
        self.set_original_DARC_image()
        self.set_original_AMD_image()

        # remove points from dictionary
        if self.current_DARC_AMD_combo in self.points_dict.keys() :

            self.points_dict.pop(self.current_DARC_AMD_combo)

        # reset points and counter
        self.current_n_points = 0
        self.current_points = []
        self.current_DARC_point = None
        self.current_AMD_point = None

        # can't remove or save points if we don't have any
        self.remove_points_button.setDisabled(True)
        self.save_points_button.setDisabled(True)

        # points are removed, allow change of eye/AMD
        self.widgetAMDSelection.setDisabled(False)
        self.widgetEyeSelection.setDisabled(False)

        # if we have removed the last saved points, disable writing
        if len(self.points_dict) == 0:

            self.write_points_button.setDisabled(True)

    def closeEvent(self, event):
        buttonReply = QMessageBox.question(self, 'Save points', "Save points",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
           self.savePoints()
        else:
            print('No clicked.')

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook


app = QtWidgets.QApplication(sys.argv)


window = MainWindow()

window.show()
app.exec_()