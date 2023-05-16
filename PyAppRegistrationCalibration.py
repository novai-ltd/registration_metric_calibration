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
from skimage import exposure
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

class QLabelWithLeaveEvent(QLabel):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

    def leaveEvent(self, event):
        # This method is called whenever the mouse pointer leaves the label
        # call method of main window which refreshes registered image
        self.main_window.mouse_left_target_image()


class MainWindow(QtWidgets.QMainWindow):


    def __init__(self):
        super().__init__()

        # set data directory and get list of eyes
        self.data_dir =  "C:\\Users\\Johnathan Young\\Box\\AIDEV\\03. Internal AI Projects\\4. Improved registration\\data\\lo_res\\NIRAF\\TV_registered_to_first_visit_sitk_corr"
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
        self.target_image = QLabelWithLeaveEvent(self, self)
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
        self.target_radiobutton.toggled.connect(self.toggle_images)
        self.toggle_image_layout.addWidget(self.target_radiobutton, 0, 0)
        self.registered_radiobutton = QRadioButton("registered image")
        self.registered_radiobutton.image = "registered"
        self.registered_radiobutton.toggled.connect(self.toggle_images)
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
        # include -1 reject button
        self.select_grading_buttons_layout = QHBoxLayout()
        radiobutton = QRadioButton("1")
        radiobutton.grading = 1
        radiobutton.toggled.connect(self.select_grading)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("2")
        radiobutton.grading = 2
        radiobutton.toggled.connect(self.select_grading)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("3")
        radiobutton.grading = 3
        radiobutton.toggled.connect(self.select_grading)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("4")
        radiobutton.grading = 4
        radiobutton.toggled.connect(self.select_grading)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("5")
        radiobutton.grading = 5
        radiobutton.toggled.connect(self.select_grading)
        self.select_grading_buttons_layout.addWidget(radiobutton)
        radiobutton = QRadioButton("-1")
        radiobutton.grading = -1
        radiobutton.toggled.connect(self.select_grading)
        self.select_grading_buttons_layout.addWidget(radiobutton)

        # button to store current grading
        self.store_grading_button = QPushButton(self)
        self.store_grading_button.setText('store grading')
        self.store_grading_button.clicked.connect(self.store_grading)

        # button to save all metrics and gradings to file
        # initialise as disabled
        self.save_gradings_to_file_button = QPushButton(self)
        self.save_gradings_to_file_button.setText('save gradings and metrics to file')
        self.save_gradings_to_file_button.clicked.connect(self.save_gradings_to_file)
        self.save_gradings_to_file_button.setDisabled(True)

        # button to show ungraded registrations
        self.show_ungraded_button = QPushButton(self)
        self.show_ungraded_button.setText('show ungraded registrations')
        self.show_ungraded_button.clicked.connect(self.show_ungraded)

        # overall grading layout
        # label, then radio buttons, then store, save and show ungraded buttons
        self.grading_layout = QVBoxLayout()
        self.grading_layout.addWidget(self.set_grading_label)
        self.grading_layout.addLayout(self.select_grading_buttons_layout)
        self.grading_layout.addWidget(self.store_grading_button)
        self.grading_layout.addWidget(self.save_gradings_to_file_button)
        self.grading_layout.addWidget(self.show_ungraded_button)

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

        # switch on mouse tracking for target image
        self.target_image.mouseMoveEvent = self.mouse_move_event

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
        # also initialize dicts to hold metrics and gradings
        # connect to select_registration function
        self.metrics_target_filenames_dict = {}
        self.metrics_registered_filenames_dict = {}
        self.NMI_dict = {}
        self.NCC_dict = {}
        self.MSE_dict = {}
        self.grading_dict = {}
        i = 1
        for row in self.registrations.iterrows():
            alignment_txt = str(i) + ': ' + row[1][1] + ' to ' + row[1][0]

            # add entry to metrics and gradings dicts
            # also store target and registered filenames
            self.metrics_target_filenames_dict.update({i - 1:None})
            self.metrics_registered_filenames_dict.update({i - 1: None})
            self.NMI_dict.update({i - 1: None})
            self.NCC_dict.update({i - 1: None})
            self.MSE_dict.update({i - 1: None})
            self.grading_dict.update({i - 1: None})

            # automatically load first image pair on startup
            if i == 1 :

                self.first_registration_txt = alignment_txt

            self.registration_selection_menu.addItem(alignment_txt)



            i = i + 1

        # load the first image pair
        self.select_registration(self.first_registration_txt)

        # connect the registration selection menu to functiion loading image pairs
        self.registration_selection_menu.activated[str].connect(self.select_registration)

        # put headings in metrics table
        self.metrics_table.setItem(0, 0, QTableWidgetItem("NMI"))
        self.metrics_table.setItem(0, 1, QTableWidgetItem("NCC"))
        self.metrics_table.setItem(0, 2, QTableWidgetItem("MSE"))

        self.current_grading = None

    def select_registration(self, registration_str):

        # set current registration files
        registration_ind = int(registration_str.split(':')[0]) - 1
        self.registration_ind = registration_ind
        self.target_file_name = self.registrations['target filename'].iloc[registration_ind]
        self.registered_file_name = self.registrations['registered filename'].iloc[registration_ind]
        self.target_file_path = os.path.join(self.data_dir, self.target_file_name)
        self.registered_file_path = os.path.join(self.data_dir, self.registered_file_name)

        # set images
        target_image = tifffile.imread(self.target_file_path)
        registered_image = tifffile.imread(self.registered_file_path)

        # do contrast stretching to enable visualization of image features
        p2, p98 = np.percentile(target_image[100:-100, 100:-100], (2, 98))
        target_image = exposure.rescale_intensity(target_image, in_range=(p2, p98))
        p2, p98 = np.percentile(registered_image[100:-100, 100:-100], (2, 98))
        registered_image = exposure.rescale_intensity(registered_image, in_range=(p2, p98))

        # pad images
        #padded_target_image = np.zeros((2000, 2000))
        #padded_registered_image = np.zeros((2000, 2000))
        #border_width = int((2000 - 1536) / 2)
        #padded_target_image[border_width:border_width + 1536, border_width:border_width + 1536] = target_image
        #padded_registered_image[border_width:border_width + 1536, border_width:border_width + 1536] = registered_image
        #target_image = padded_target_image
        #registered_image = padded_registered_image



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
        #(re)-invert NCC
        NMI, NCC, MSE = calculate_metrics(target_image, registered_image)
        NCC = -1 * NCC
        self.NMI = NMI
        self.NCC = NCC
        self.MSE = MSE

        # update dicts
        self.metrics_target_filenames_dict.update({registration_ind:self.target_file_name})
        self.metrics_registered_filenames_dict.update({registration_ind:self.registered_file_name})
        self.NMI_dict.update({registration_ind:NMI})
        self.NCC_dict.update({registration_ind:NCC})
        self.MSE_dict.update({registration_ind:MSE})

        #  update values in metrics table
        self.metrics_table.setItem(1, 0, QTableWidgetItem(f'{NMI:4.3f}'))
        self.metrics_table.setItem(1, 1, QTableWidgetItem(f'{-1*NCC:4.3f}'))
        self.metrics_table.setItem(1, 2, QTableWidgetItem(f'{MSE:4.3f}'))

        # reset current grading
        # has to be done here as select_grading is somehow called earlier in this function - how??
        self.current_grading = None

    # when mouse leaves target image, repaint registered image to remove crosshair
    def mouse_left_target_image(self):

        # reload image
        self.registered_image.setPixmap(self.convert_ndarray_to_QPixmap(self.registered_image_array))
        self.registered_image.repaint()

    # define behaviour for toggling between registered and target images
    def toggle_images(self):
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

    # when a grading radio button is selected, store the grading
    def select_grading(self):

        # save the grading associated with the radio button for the current image pair
        grading_radio_button = self.sender()
        self.current_grading = grading_radio_button.grading


    # store the current grading for the current
    def store_grading(self) :

        self.grading_dict.update({self.registration_ind: self.current_grading})

        # when a grading is set for all image pairs, enable saving
        grading_vals = self.grading_dict.values()
        if None in grading_vals :

            self.save_gradings_to_file_button.setDisabled(True)

        else :

            self.save_gradings_to_file_button.setDisabled(False)

    def mouse_move_event(self, event):
        # Update the crosshair position when the mouse is moved over the left-hand image
       # self.crosshair_position = None
        #if event.pos().x() < self.target_image.width():
       #     self.crosshair_position = QPoint(event.pos().x() * self.registered_image.width() / self.target_image.width(),
       #                                      event.pos().y() * self.registered_image.height() / self.target_image.height())
        #self.repaint()
        #print(event.pos())
        #if not self.target_image.underMouse():
        #    print('off!')
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
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def show_ungraded(self):

        # find ungraded registrations
        ungraded_registrations = [key + 1 for key, value in self.grading_dict.items() if value is None]

        # list them in popup
        msg = QMessageBox()
        msg.setWindowTitle("Ungraded registrations")
        msg.setText("Ungraded registrations are as follows:" + str(ungraded_registrations))
        msg.exec_()

    def save_gradings_to_file(self):

        # convert gradings and metrics to dataframe
        # save dataframe to csv
        metrics_gradings_DF = pd.DataFrame([self.metrics_target_filenames_dict, self.metrics_registered_filenames_dict, self.NMI_dict, self.NCC_dict, self.MSE_dict, self.grading_dict])
        metrics_gradings_DF = metrics_gradings_DF.transpose()
        metrics_gradings_DF.columns=['target image file', 'registered image file', 'NMI', 'NCC', 'MSE', 'grading']
        metrics_gradings_DF.to_csv(os.path.join(self.data_dir, 'metrics_gradings.csv'))

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