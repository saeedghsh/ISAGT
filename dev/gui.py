import sys, os, platform
import time
import thread
import numpy as np
import cv2

import PySide
from PySide import QtCore, QtGui  # QtGui.QMainWindow, QtGui.QPushButton, QtGui.QApplication

import isagt # isagt.Ui_MainWindow
__version__ = '0.1'



##############################################################
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
import pylab

# from matplotlib.backends import qt4_compat
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure()#figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)


        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.draw()

    def plotImage(self,image=None):

        # t = np.arange(0.0, 3.0, 0.01)
        # s = np.sin(2*np.pi*t)
        # self.axes.plot(t, s)
        self.axes.imshow(image)
        self.draw()



##############################################################

# https://gist.github.com/andrewgiessel/3493579

##############################################################

class MainWindow(QtGui.QMainWindow, isagt.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = isagt.Ui_MainWindow()
        self.ui.setupUi(self)


        ######### Matplotlib Setting
        self.main_widget = self.ui.graphicsView #QtGui.QWidget(self)
        self.layout = QtGui.QVBoxLayout(self.main_widget)
        # sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        # dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        # l.addWidget(sc)
        # l.addWidget(dc)
        self.myCanvas = MyMplCanvas(self.main_widget)
        self.layout.addWidget(self.myCanvas)
        # self.main_widget.setFocus()
        #self.setCentralWidget(self.main_widget)

        ######### Push buttons
        self.ui.loadButton.clicked.connect(self.loadFiles)
        self.ui.aboutButton.clicked.connect(self.about)
        self.ui.navGoto.clicked.connect(self.navGoTo)
        self.ui.navNext.clicked.connect(self.navNext)
        self.ui.navPrev.clicked.connect(self.navPrev)
        ######### Radio buttons
        self.ui.loadYaml.toggled.connect(self.draw)
        self.ui.unwrapFlag.toggled.connect(self.draw)
        self.ui.displayAnnotation.toggled.connect(self.draw)
        
    def loadFiles(self):

        # laodOption = 'folder' if  self.ui.loadOption.currentIndex()==0 else 'file'

        if self.ui.loadOption.currentText() == 'Folder':
            path = QtGui.QFileDialog.getExistingDirectory()
            content = [ f for f in os.listdir(path)
                        if os.path.isfile(os.path.join(path,f)) ]
            filesNames = [os.path.join(path,f) for f in content]

        elif self.ui.loadOption.currentText() == 'Single File':
            filesNames = QtGui.QFileDialog.getOpenFileName()

        # remove empty strings and none image files
        yamlList, imagList = [], []
        for i in range(len(filesNames)-1,-1,-1):
            if len(filesNames[i]) == 0:
                pass #filesNames.pop(i)
            elif filesNames[i][-4:] == ('yaml' or 'YAML'):
                yamlList.append(filesNames[i])
            elif filesNames[i][-4:] == ('.png' or '.PNG' or '.jpg' or '.JPG' or 'JPEG' or 'jpeg'):
                imagList.append(filesNames[i])

        if len(imagList) > 0:
            imagList.sort(), yamlList.sort()
            self.yamlList, self.imagList = yamlList, imagList
            print "ready to go"
            self.ui.groupCategory.setEnabled(True)
            self.ui.groupNavigation.setEnabled(True)
            self.ui.groupAnnotation.setEnabled(True)
            self.ui.groupAnnotationList.setEnabled(True)
            self.ui.groupAnnotationID.setEnabled(True)

            self.imagIndx = 0

            # http://softwareramblings.com/2008/06/running-functions-as-threads-in-python.html
            # thread.start_new_thread(self.draw, ())
            self.draw()
            
        else:
            pass

    def draw(self):


        # this function is [always?] hosted by other functins
        # such as "loadFiles", "navGoTo",...
        # be careful not to lock it!

        # TODO: First check if imagList is loaded, then go through!
        # because some radioButtons are connected to this function and they
        # they might be toggled before loading!
        
        self.ui.textAddress.setText(self.imagList[self.imagIndx])
        self.ui.navigationCounter.setText(str(self.imagIndx+1)+'/'+str(len(self.imagList)))
        
        # http://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html
        self.image = cv2.imread(self.imagList[self.imagIndx])
        self.myCanvas.plotImage(self.image)        
        if self.ui.unwrapFlag.isChecked():
            if self.ui.unwrapOption.currentText() == 'Fisheye - Downward':
                pass # unrwape image
            elif self.ui.unwrapOption.currentText() == 'Fisheye - Forward':
                pass # unrwape image
            elif self.ui.unwrapOption.currentText() == 'OminCam':
                pass # unrwape image
        # plot self.image

        # self.annotations = []
        # if self.ui.loadYaml.isChecked():
        #     # TODO:
        #     self.yamlIndx = corresponding (self.imagList[self.imageCounter])
        #     if yaml exists:
        #         #TODO:
        #         self.annotations = load self.yamlList[self.yamlIndx]
        # if self.ui.displayAnnotation.isChecked():
        #     #TODO:
        #     plot self.annotations

    def navNext(self):
        idx = self.imagIndx + 1# python value increase by button
        idx = idx%len(self.imagList) # handling overflow
        idx += 1 # UI value 
        self.ui.navigationCounter.setText(str(idx)+'/'+str(len(self.imagList)))
        self.navGoTo()

    def navPrev(self):
        idx = self.imagIndx - 1 # python value decrease by button
        idx = idx%len(self.imagList) # handling overflow
        idx += 1 # UI value 
        self.ui.navigationCounter.setText(str(idx)+'/'+str(len(self.imagList)))
        self.navGoTo()

    def navGoTo(self):
        navCount = self.ui.navigationCounter.toPlainText().split('/')[0]
        if navCount.isdigit():
            if -1 < int(navCount)-1 < len(self.imagList):
                self.save2yaml()
                self.imagIndx = int(navCount)-1 # compensating for python starting at 0
                self.draw()
            else:
                QtGui.QMessageBox.about(self, "error",
                                        """navGoTo function says: image index is out of range""")
        else:
            QtGui.QMessageBox.about(self, "error",
                                    """navGoTo function says: please enter an integer number""")

    def captureAnnotation(self):
        pass
        # self.annotateTemp.append()
        # TODO: by every click on image add point to self.annotateTemp[[p1x,p1y] , [] ,...]
        
    def save2yaml(self):
        pass

    def readCategory(self):
        if self.ui.catPoly.isChecked():
            return 'polygone'
        elif self.ui.catConstellation.isChecked():
            return 'constellation'
        elif self.ui.catLine.isChecked():
            return 'line'
        elif self.ui.catCircle.isChecked():
            return 'circle'
        else:
            QtGui.QMessageBox.about(self, "error",
                                    """readCategory function says: no category?!!""")


    def about(self):
        QtGui.QMessageBox.about(self, "About Image Semantic Annotation for Ground Truth",
                                """<b>Version</b> %s
                                <p>Copyright &copy; 2015 Saeed Gholami Shahbandi.
                                All rights reserved in accordance with
                                BSD 3-clause - NO WARRANTIES!
                                <p>This GUI facilitates the process of 
                                manually generating ground truth for semantic annotation of images.
                                The results are stored in YAML format.
                                <p>Python %s - PySide version %s - Qt version %s on %s""" % (__version__,
                                                                                             platform.python_version(), PySide.__version__, QtCore.__version__,
                                                                                             platform.system()))

##############################################################

# if ''name'' == "''main''":
app = QtGui.QApplication(sys.argv)
mySW = MainWindow()
mySW.show()
app.exec_()
# sys.exit(app.exec_())




