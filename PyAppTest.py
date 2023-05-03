#from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#from PyAppSelectPoints_pyside import MainWindow
#from PyAppImgPainter_OCT_ANNO_SS_CNN_Test_use import MainWindow
# Only needed for access to command line arguments
import sys
import pickle
from PyAppSelectPoints_pyside import call_app

# class Color(QWidget):
#
#     def __init__(self, color, *args, **kwargs):
#         super(Color, self).__init__(*args, **kwargs)
#         self.setAutoFillBackground(True)
#
#         palette = self.palette()
#         palette.setColor(QPalette.Window, QColor(color))
#         self.setPalette(palette)
#
#
# # Subclass QMainWindow to customise your application's main window
# class CustomDialog(QDialog):
#
#     def __init__(self, *args, **kwargs):
#         super(CustomDialog, self).__init__(*args, **kwargs)
#
#         self.setWindowTitle("HELLO!")
#
#         QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
#
#         self.buttonBox = QDialogButtonBox(QBtn)
#         self.buttonBox.accepted.connect(self.accept)
#         self.buttonBox.rejected.connect(self.reject)
#
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.buttonBox)
#         self.setLayout(self.layout)
#
#
# class MainWindow(QMainWindow):
#
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#
#         self.setWindowTitle("My Awesome App")
#
#         widget = Color('red')#QPushButton()
#        # widget.setMaxLength(10)
#         #widget.setPlaceholderText("Enter your text")
#
#         # widget.setReadOnly(True) # uncomment this to make readonly
#
#         #widget.pressed.connect(self.return_pressed)
#         # widget.selectionChanged.connect(self.selection_changed)
#         # widget.textChanged.connect(self.onMyToolBarButtonClick)
#         # widget.textEdited.connect(self.text_edited)
#
#         self.setCentralWidget(widget)
#
#     def return_pressed(self):
#         print("Return pressed!")
#         self.centralWidget().setText("BOOM!")
#
#     def selection_changed(self):
#         print("Selection changed")
#         print(self.centralWidget().selectedText())
#
#     def text_changed(self, s):
#         print("Text changed...")
#         print(s)
#
#     def text_edited(self, s):
#         print("Text edited...")
#         print(s)
#
#     def onMyToolBarButtonClick(self, s):
#         print("click", s)
#
#         dlg = CustomDialog(self)
#         if dlg.exec_():
#             print("Success!")
#         else:
#             print("Cancel!")

# for now read in list of alignments from file
#with open('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\manual_alignment_list', 'rb') as f:
#    manual_alignments_list = pickle.load(f)

manual_alignments_list = [('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.1_0.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.1_1.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.1_2.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.1_3.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.2_0.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.2_1.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.2_2.tif'), ('c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test\\Original\\ONL1204-GA-001\\AUS_02\\002\\OS\\V1\\NIRAF', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.0_0.tif', 'ONL1204-GA_AUS_02_002_OS_V1_01092021_1.2_3.tif')]


# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
base_dir = 'c:\\Users\\Johnathan Young\\Novai Dropbox\\Jonathan Young\\development_data\\workflow_test'
upload_name = 'ONL1204-GA-001_AUS_02_002_V1_31122021_000'
#app = QApplication(sys.argv)
#window = MainWindow(base_dir, upload_name, manual_alignments_list)
#window.set_alignments('foo')
#window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
#app.exec_()

# Your application won't reach here until you exit and the event
# loop has stopped
call_app(base_dir, upload_name, manual_alignments_list)
print('done!')

