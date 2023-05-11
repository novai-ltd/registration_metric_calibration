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
import tifffile
from skimage.color import gray2rgb
from utils import calculate_metrics
import json
# import scipy.interpolate as interpolate
# import matplotlib.pyplot as plt
# from scipy.signal import savgol_filter
# from scipy.interpolate import CubicSpline
#import numpy
#from scipy.signal import medfilt
#from numpy.random import randint
#import pandas as pd
import math

from datetime import datetime
#from GenRPEMesh import createRPEMesh
#from skimage import exposure
#import pyqtgraph as pg
from PyQt5.QtCore import QSettings
import time


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # set data directory and get list of eyes
        self.data_dir =  "C:\\Users\\Johnathan Young\\Box\\AIDEV\\03. Internal AI Projects\\4. Improved registration\\data\\hi_res\\NIR\\TV_registered_to_first_visit_sitk_corr\\"
        self.image_size = (450, 450)

        # initialise image display to grey
        # fix height so resizing window doesn't mess up pixel coordinates
        # initialise image display to grey
        # fix height so resizing window doesn't mess up pixel coordinates
        self.toggle_image = QLabel(self)
        self.grey = QPixmap(self.image_size[0], self.image_size[1])
        self.grey.fill(QColor('darkGray'))
        self.toggle_image.setFixedHeight(self.image_size[0])
        self.toggle_image.setPixmap(self.grey)
        self.difference_image = QLabel(self)
        self.difference_image.setPixmap(self.grey)
        self.difference_image.setFixedHeight(self.image_size[0])
        self.target_image = QLabel(self)
        self.target_image.setPixmap(self.grey)
        self.target_image.setFixedHeight(self.image_size[0])
        self.registered_image = QLabel(self)
        self.registered_image.setPixmap(self.grey)
        self.registered_image.setFixedHeight(self.image_size[0])

        self.target_image.setMouseTracking(True)

        # Set up crosshair
        self.crosshair_size = 10
        self.crosshair_color = Qt.red
        self.crosshair_position = None

        # make radio button for toggling between target and registered images
        self.toggle_image_layout = QGridLayout()
        self.target_radiobutton = QRadioButton("target image")
        self.target_radiobutton.setChecked(True)
        self.target_radiobutton.image = "target"
        self.target_radiobutton.toggled.connect(self.imageOnClicked)
        self.toggle_image_layout.addWidget(self.target_radiobutton, 0, 0)
        self.registered_radiobutton = QRadioButton("registered image")
        self.registered_radiobutton.image = "registered"
        self.registered_radiobutton.toggled.connect(self.imageOnClicked)
        self.toggle_image_layout.addWidget(self.registered_radiobutton, 0, 1)

        # set up metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setRowCount(2)
        self.metrics_table.setColumnCount(3)
        self.metrics_table.setVerticalHeaderLabels(["metric", "value"])
        self.metrics_table.horizontalHeader().setVisible(False)

        # set up image selection labels
        self.toggle_image_label = QLabel(self)
        self.difference_image_label = QLabel(self)
        self.metrics_table_label = QLabel(self)
        self.target_image_label = QLabel(self)
        self.registered_image_label = QLabel(self)
        self.set_grading_label = QLabel(self)
        self.registration_selection_label =QLabel(self)
        self.toggle_image_label.setText('Toggle between target and registered image')
        self.difference_image_label.setText('Difference between target and registered image')
        self.metrics_table_label.setText('Image registration metrics')
        self.target_image_label.setText('Target image')
        self.registered_image_label.setText('Registered image')
        self.set_grading_label.setText('Set registration grading')
        self.registration_selection_label.setText('Select registered image pair')
        self.toggle_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.difference_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.metrics_table_label.setAlignment(QtCore.Qt.AlignCenter)
        self.target_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.registered_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.set_grading_label.setAlignment(QtCore.Qt.AlignCenter)
        self.registration_selection_label.setAlignment(QtCore.Qt.AlignCenter)

        # set up layout for grading registrations on a scale of 1 to 5
        # radion buttons arranged horizontally
        self.select_grading_buttons_layout = QHBoxLayout()
        radiobutton = QRadioButton("1")
        radiobutton.setChecked(True)
        radiobutton.grading = 1
#        radiobutton.toggled.connect(self.onClicked)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("2")
        radiobutton.grading = 2
#       radiobutton.toggled.connect(self.onClicked)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("3")
        radiobutton.grading = 3
#        radiobutton.toggled.connect(self.onClicked)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("4")
        radiobutton.grading = 4
#        radiobutton.toggled.connect(self.onClicked)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("5")
        radiobutton.grading = 5
#        radiobutton.toggled.connect(self.onClicked)
        self.select_grading_buttons_layout.addWidget(radiobutton)

        # button to save grading
        self.save_grading_button = QPushButton(self)
        self.save_grading_button.setText('save grading')
        #self.save_grading_button.clicked.connect(self.save_grading)

        # overall grading layout
        # label, then radio buttons, then save button
        self.grading_layout = QVBoxLayout()
        self.grading_layout.addWidget(self.set_grading_label)
        self.grading_layout.addLayout(self.select_grading_buttons_layout)
        self.grading_layout.addWidget(self.save_grading_button)

        # overall registration selection layout
        # label then dropdown
        self.registration_selection_layout = QVBoxLayout()
        self.registration_selection_menu = QComboBox(self)
        self.registration_selection_layout.addWidget(self.registration_selection_label)
        self.registration_selection_layout.addWidget(self.registration_selection_menu)

        # set up widgets for displaying metrics
        self.metrics_layout = QVBoxLayout()
        self.metrics_layout.addWidget(self.metrics_table_label)
        self.metrics_layout.addWidget(self.metrics_table)

        # set up overall layout with qgrid
        self.layout = QGridLayout()
        self.layout.addWidget(self.toggle_image_label, 0, 0)
        self.layout.addWidget(self.difference_image_label, 0, 1)
        self.layout.addWidget(self.target_image_label, 0, 2)
        self.layout.addWidget(self.registered_image_label, 0, 3)
        self.layout.addWidget(self.toggle_image, 1, 0)
        self.layout.addWidget(self.difference_image, 1, 1)
        self.layout.addWidget(self.target_image, 1, 2)
        self.layout.addWidget(self.registered_image, 1, 3)
        self.layout.addLayout(self.toggle_image_layout, 2, 0)
        self.layout.addLayout(self.registration_selection_layout, 3, 0, 1, 2)
        self.layout.addLayout(self.metrics_layout, 3, 2)
        self.layout.addLayout(self.grading_layout, 3, 3)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Set up event handlers
        self.target_image.mouseMoveEvent = self.mouse_move_event
 #       self.target_image.leaveEvent()



        # get list of registrations
        image_files = glob.glob(os.path.join(self.data_dir, "*.tif"))
        image_files = pd.DataFrame({'image file': image_files})
        image_files['file name'] = image_files['image file'].apply(lambda x: os.path.basename(x))
        image_files['eyedentifier'] = image_files['file name'].apply(lambda x: '_'.join(x.split('_')[:4]))
        grouped = image_files.groupby('eyedentifier')
        target_filenames = []
        registered_filenames = []

        for group, data in grouped:

            data = data.sort_values('file name')
            filenames = data['file name'].tolist()
            for registered_filename in filenames[1:]:
                target_filenames.append(filenames[0])
                registered_filenames.append(registered_filename)

        self.registrations = pd.DataFrame({'target filename': target_filenames, 'registered filename': registered_filenames})

        # populate registration selection dropdown
        # connect to select_registration function
        i = 1
        for row in self.registrations.iterrows():
            alignment_txt = str(i) + ': ' + row[1][1] + ' to ' + row[1][0]

            self.registration_selection_menu.addItem(alignment_txt)
            i = i + 1
        self.registration_selection_menu.activated[str].connect(self.select_registration)
        radiobutton.toggled.connect(self.imageOnClicked)


    def select_registration(self, registration_str):

        # set current registration files
        registration_ind = int(registration_str.split(':')[0]) - 1
        self.target_file_name = self.registrations['target filename'].iloc[registration_ind]
        self.registered_file_name = self.registrations['registered filename'].iloc[registration_ind]
        self.target_file_path = os.path.join(self.data_dir, self.target_file_name)
        self.registered_file_path = os.path.join(self.data_dir, self.registered_file_name)

        # set images
        target_image = tifffile.imread(self.target_file_path)
        registered_image = tifffile.imread(self.registered_file_path)
        target_image_RGB = gray2rgb(target_image)
        registered_image_RGB = gray2rgb(registered_image)
        self.target_image_array = (target_image_RGB * 255).astype(np.uint8)
        self.registered_image_array = (registered_image_RGB * 255).astype(np.uint8)
        self.difference_image_array = self.target_image_array - self.registered_image_array
        self.target_image.setPixmap(self.convert_ndarray_to_QPixmap(self.target_image_array))
        self.registered_image.setPixmap(self.convert_ndarray_to_QPixmap(self.registered_image_array))
        self.difference_image.setPixmap(self.convert_ndarray_to_QPixmap(self.difference_image_array))
        self.toggle_image.setPixmap(self.grey)

        # by default have target/registration image toggling as target
        self.target_radiobutton.setChecked(True)
        self.toggle_image.setPixmap(self.convert_ndarray_to_QPixmap(self.target_image_array))

        # calculate similarity metrics
        NMI, NCC, MSE = calculate_metrics(target_image, registered_image)
        print(NMI, NCC, MSE)

    # define behaviour for toggling between registered and target images
    def imageOnClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            selected_image = radioButton.image
            if selected_image == 'target' :
                self.toggle_image.setPixmap(self.convert_ndarray_to_QPixmap(self.target_image_array))
            else :
                self.toggle_image.setPixmap(self.convert_ndarray_to_QPixmap(self.registered_image_array))

    def draw_crosshair_on_registered_image(self, position):

        # reload image
        self.registered_image.setPixmap(self.convert_ndarray_to_QPixmap(self.registered_image_array))

        # Create a QPainter object and set the pen color and width
        painter = QPainter(self.registered_image.pixmap())
        painter.setPen(QPen(QColor(255, 0, 0), 1))


        # Draw two lines to form a crosshair at the given position
        painter.drawLine(QPoint(position.x() - 5, position.y()), QPoint(position.x() + 5, position.y()))
        painter.drawLine(QPoint(position.x(), position.y() - 5), QPoint(position.x(), position.y() + 5))

        self.registered_image.repaint()

        # End painting
        painter.end()







    def mouse_move_event(self, event):
        # Update the crosshair position when the mouse is moved over the left-hand image
       # self.crosshair_position = None
        #if event.pos().x() < self.target_image.width():
       #     self.crosshair_position = QPoint(event.pos().x() * self.registered_image.width() / self.target_image.width(),
       #                                      event.pos().y() * self.registered_image.height() / self.target_image.height())
        #self.repaint()
        print(event.pos())
        if not self.target_image.underMouse():
            print('off!')
        self.draw_crosshair_on_registered_image(event.pos())

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