"""
Copyright © 2023 Howard Hughes Medical Institute, Authored by Carsen Stringer and Marius Pachitariu.
"""

from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtGui import QPainter, QPixmap, QImage, QFont
from qtpy.QtWidgets import QApplication, QRadioButton, QWidget, QDialog, QButtonGroup, QSlider, QStyle, QStyleOptionSlider, QGridLayout, QPushButton, QLabel, QLineEdit, QDialogButtonBox, QComboBox, QCheckBox, QDockWidget, QMenu, QWidgetAction
from qtpy.QtCore import QEvent
import pyqtgraph as pg
from pyqtgraph import functions as fn
from pyqtgraph import Point
import numpy as np
import pathlib, os


def stylesheet():
    return """
        QToolTip { 
                            background-color: black; 
                            color: white; 
                            border: black solid 1px
                            }
        QComboBox {color: white;
                    background-color: rgb(40,40,40);}
                    QComboBox::item:enabled { color: white;
                    background-color: rgb(40,40,40);
                    selection-color: white;
                    selection-background-color: rgb(50,100,50);}
                    QComboBox::item:!enabled {
                            background-color: rgb(40,40,40);
                            color: rgb(100,100,100);
                        }
        QScrollArea > QWidget > QWidget
                {
                    background: transparent;
                    border: none;
                    margin: 0px 0px 0px 0px;
                } 

        QGroupBox 
            { border: 1px solid white; color: rgb(255,255,255);
                           border-radius: 6px;
                            margin-top: 8px;
                            padding: 0px 0px;}            

        QPushButton:pressed {Text-align: center; 
                             background-color: rgb(150,50,150); 
                             border-color: white;
                             color:white;}
                            QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }
        QPushButton:!pressed {Text-align: center; 
                               background-color: rgb(50,50,50);
                                border-color: white;
                               color:white;}
                                QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }
        QPushButton:disabled {Text-align: center; 
                             background-color: rgb(30,30,30);
                             border-color: white;
                              color:rgb(80,80,80);}
                               QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }

        """


class DarkPalette(QtGui.QPalette):
    """Class that inherits from pyqtgraph.QtGui.QPalette and renders dark colours for the application.
    (from pykilosort/kilosort4)
    """

    def __init__(self):
        QtGui.QPalette.__init__(self)
        self.setup()

    def setup(self):
        self.setColor(QtGui.QPalette.Window, QtGui.QColor(40, 40, 40))
        self.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.Base, QtGui.QColor(34, 27, 24))
        self.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 50, 47))
        self.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 50, 47))
        self.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
        self.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
        self.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,
                      QtGui.QColor(128, 128, 128))
        self.setColor(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.ButtonText,
            QtGui.QColor(128, 128, 128),
        )
        self.setColor(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.WindowText,
            QtGui.QColor(128, 128, 128),
        )


def create_channel_choose():
    # choose channel
    ChannelChoose = [QComboBox(), QComboBox()]
    ChannelLabels = []
    ChannelChoose[0].addItems(["gray", "red", "green", "blue"])
    ChannelChoose[1].addItems(["none", "red", "green", "blue"])
    cstr = ["chan to segment:", "chan2 (optional): "]
    for i in range(2):
        ChannelLabels.append(QLabel(cstr[i]))
        if i == 0:
            ChannelLabels[i].setToolTip(
                "this is the channel in which the cytoplasm or nuclei exist \
            that you want to segment")
            ChannelChoose[i].setToolTip(
                "this is the channel in which the cytoplasm or nuclei exist \
            that you want to segment")
        else:
            ChannelLabels[i].setToolTip(
                "if <em>cytoplasm</em> model is chosen, and you also have a \
            nuclear channel, then choose the nuclear channel for this option")
            ChannelChoose[i].setToolTip(
                "if <em>cytoplasm</em> model is chosen, and you also have a \
            nuclear channel, then choose the nuclear channel for this option")

    return ChannelChoose, ChannelLabels


class ModelButton(QPushButton):

    def __init__(self, parent, model_name, text):
        super().__init__()
        self.setEnabled(False)
        self.setText(text)
        self.setFont(parent.boldfont)
        self.clicked.connect(lambda: self.press(parent))
        self.model_name = model_name if "cyto3" not in model_name else "cyto3"

    def press(self, parent):
        parent.compute_segmentation(model_name=self.model_name)


class DenoiseButton(QPushButton):

    def __init__(self, parent, text):
        super().__init__()
        self.setEnabled(False)
        self.model_type = text
        self.setText(text)
        self.setFont(parent.medfont)
        self.clicked.connect(lambda: self.press(parent))

    def press(self, parent):
        if self.model_type == "filter":
            parent.restore = "filter"
            normalize_params = parent.get_normalize_params()
            if (normalize_params["sharpen_radius"] == 0 and
                    normalize_params["smooth_radius"] == 0 and
                    normalize_params["tile_norm_blocksize"] == 0):
                print(
                    "GUI_ERROR: no filtering settings on (use custom filter settings)")
                parent.restore = None
                return
            parent.restore = self.model_type
            parent.compute_saturation()
        elif self.model_type != "none":
            parent.compute_denoise_model(model_type=self.model_type)
        else:
            parent.clear_restore()
        parent.set_restore_button()


class TrainWindow(QDialog):

    def __init__(self, parent, model_strings):
        super().__init__(parent)
        self.setGeometry(100, 100, 900, 350)
        self.setWindowTitle("train settings")
        self.win = QWidget(self)
        self.l0 = QGridLayout()
        self.win.setLayout(self.l0)

        yoff = 0
        qlabel = QLabel("train model w/ images + _seg.npy in current folder >>")
        qlabel.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

        qlabel.setAlignment(QtCore.Qt.AlignVCenter)
        self.l0.addWidget(qlabel, yoff, 0, 1, 2)

        # choose initial model
        yoff += 1
        self.ModelChoose = QComboBox()
        self.ModelChoose.addItems(model_strings)
        self.ModelChoose.addItems(["scratch"])
        self.ModelChoose.setFixedWidth(150)
        self.ModelChoose.setCurrentIndex(parent.training_params["model_index"])
        self.l0.addWidget(self.ModelChoose, yoff, 1, 1, 1)
        qlabel = QLabel("initial model: ")
        qlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.l0.addWidget(qlabel, yoff, 0, 1, 1)

        # choose channels
        self.ChannelChoose, self.ChannelLabels = create_channel_choose()
        for i in range(2):
            yoff += 1
            self.ChannelChoose[i].setFixedWidth(150)
            self.ChannelChoose[i].setCurrentIndex(
                parent.ChannelChoose[i].currentIndex())
            self.l0.addWidget(self.ChannelLabels[i], yoff, 0, 1, 1)
            self.l0.addWidget(self.ChannelChoose[i], yoff, 1, 1, 1)

        # choose parameters
        labels = ["learning_rate", "weight_decay", "n_epochs", "model_name"]
        self.edits = []
        self.parameter_explanations = ["The learning rate determines how quickly or slowly the model learns from data. A higher learning rate may lead to faster learning but could cause the model to overshoot the optimal solution. Conversely, a lower learning rate may result in slower learning but is safer and more likely to find the best solution.",
                                       "Weight decay helps prevent overfitting by penalizing large parameter values in the model. \n Increasing weight decay encourages the model to learn simpler patterns from the data,\n improving its ability to generalize to new, unseen examples.",
                                       "The number of times the entire dataset is passed forward and backward through the machine learning model during training. Increasing the number of epochs allows the model to see the data more times, potentially improving its accuracy. However, too many epochs can lead to overfitting, where the model memorizes the training data instead of learning generalizable patterns.",
                     ""]
        yoff += 1
        for i, label in enumerate(labels):
            qlabel = QLabel(label)
            qlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            qlabel.setToolTip(self.parameter_explanations[i])
            self.l0.addWidget(qlabel, i + yoff, 0, 1, 1)
            self.edits.append(QLineEdit())
            self.edits[-1].setText(str(parent.training_params[label]))
            self.edits[-1].setFixedWidth(200)
            self.l0.addWidget(self.edits[-1], i + yoff, 1, 1, 1)

        yoff += len(labels)

        yoff += 1
        self.use_norm = QCheckBox(f"use restored/filtered image")
        self.use_norm.setChecked(True)
        #self.l0.addWidget(self.use_norm, yoff, 0, 2, 4)

        yoff += 2
        qlabel = QLabel(
            "(to remove files, click cancel then remove \nfrom folder and reopen train window)"
        )
        self.l0.addWidget(qlabel, yoff, 0, 2, 4)

        # click button
        yoff += 3
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(lambda: self.accept(parent))
        self.buttonBox.rejected.connect(self.reject)
        self.l0.addWidget(self.buttonBox, yoff, 0, 1, 4)

        # list files in folder
        qlabel = QLabel("filenames")
        qlabel.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
        self.l0.addWidget(qlabel, 0, 4, 1, 1)
        qlabel = QLabel("# of masks")
        qlabel.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
        self.l0.addWidget(qlabel, 0, 5, 1, 1)

        for i in range(10):
            if i > len(parent.train_files) - 1:
                break
            elif i == 9 and len(parent.train_files) > 10:
                label = "..."
                nmasks = "..."
            else:
                label = os.path.split(parent.train_files[i])[-1]
                nmasks = str(parent.train_labels[i].max())
            qlabel = QLabel(label)
            self.l0.addWidget(qlabel, i + 1, 4, 1, 1)
            qlabel = QLabel(nmasks)
            qlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.l0.addWidget(qlabel, i + 1, 5, 1, 1)

    def accept(self, parent):
        # set channels
        for i in range(2):
            parent.ChannelChoose[i].setCurrentIndex(
                self.ChannelChoose[i].currentIndex())
        # set training params
        parent.training_params = {
            "model_index": self.ModelChoose.currentIndex(),
            "learning_rate": float(self.edits[0].text()),
            "weight_decay": float(self.edits[1].text()),
            "n_epochs": int(self.edits[2].text()),
            "model_name": self.edits[3].text(),
            #"use_norm": True if self.use_norm.isChecked() else False,
        }
        self.done(1)


class ExampleGUI(QDialog):

    def __init__(self, parent=None):
        super(ExampleGUI, self).__init__(parent)
        self.setGeometry(100, 100, 1300, 900)
        self.setWindowTitle("GUI layout")
        self.win = QWidget(self)
        layout = QGridLayout()
        self.win.setLayout(layout)
        guip_path = pathlib.Path.home().joinpath(".cellpose", "cellpose_gui.png")
        guip_path = str(guip_path.resolve())
        pixmap = QPixmap(guip_path)
        label = QLabel(self)
        label.setPixmap(pixmap)
        pixmap.scaled
        layout.addWidget(label, 0, 0, 1, 1)


class HelpWindow(QDialog):

    def __init__(self, parent=None):
        super(HelpWindow, self).__init__(parent)
        self.setGeometry(100, 50, 700, 1000)
        self.setWindowTitle("cellpose help")
        self.win = QWidget(self)
        layout = QGridLayout()
        self.win.setLayout(layout)

        text_file = pathlib.Path(__file__).parent.joinpath("guihelpwindowtext.html")
        with open(str(text_file.resolve()), "r") as f:
            text = f.read()

        label = QLabel(text)
        label.setFont(QtGui.QFont("Arial", 8))
        label.setWordWrap(True)
        layout.addWidget(label, 0, 0, 1, 1)
        self.show()

class TrainHelpWindow(QDialog):
    def __init__(self, parent=None):
        super(TrainHelpWindow, self).__init__(parent)
        self.setGeometry(200, 200, 1000, 700)
        self.setMinimumSize(300, 200)
        self.setWindowTitle("Training Instructions")

        layout = QGridLayout()
        self.setLayout(layout)

        text_file = pathlib.Path(__file__).parent.joinpath("guitrainhelpwindowtext.html")
        with open(str(text_file.resolve()), "r") as f:
            text = f.read()

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        layout.addWidget(self.label, 0, 0, 1, 1)

        # Dropdown menu for font size
        self.font_size_combo = QComboBox(self)
        self.font_size_combo.addItems([str(size) for size in range(8, 45, 3)])
        # Set fixed size (width, height)
        self.font_size_combo.setFixedSize(55, 25)
        # Set default index to 17
        self.font_size_combo.setCurrentText("17")

        # The line "self.font_size_combo.currentIndexChanged.connect(self.adjust_font_size)"
        # directly connects the currentIndexChanged signal of the "self.font_size_combo" object
        # to the "self.adjust_font_size" method.
        # The "self.adjust_font_size" method is automatically called whenever the index changes
        # in ("self.font_size_combo") the dropdown menu.
        self.font_size_combo.currentIndexChanged.connect(self.adjust_font_size)
        layout.addWidget(self.font_size_combo, 1, 0, 1, 1)

        self.adjust_font_size()  # Initial font size adjustment

        self.show()

    def adjust_font_size(self):
        # Get the current font size from the combo box
        font_size = int(self.font_size_combo.currentText())
        # Calculate the new font size based on window height and width
        new_font_size = max(5, int((self.height() * self.width())**0.5 / 45))
        # Set the font size for the label
        # The if statement prevents the font from being too big to fit the screen/window
        if new_font_size < font_size:
            font = QFont("Arial", new_font_size)
        else:
            font = QFont("Arial", font_size)
        self.label.setFont(font)

    def resizeEvent(self, event):
        # Call adjust_font_size when the window is resized
        self.adjust_font_size()
        super().resizeEvent(event)


# window displaying a minimap of the current image
class MinimapWindow(QDialog):
    """
    Method to initialize the Minimap Window.
    It creates a title for the window and a QDialog with a basic layout.
    It also takes the current picture stored in the stack and loads it in a Viewbox.
    The proportions of this image stay constant.
    The minimap updates with the image in the main window.
    """

    def __init__(self, parent=None):
        super(MinimapWindow, self).__init__(parent)
        # Set the title of the window
        self.title = "Minimap (click right mouse button to resize)"
        self.setWindowTitle(self.title)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Set min, max and default size of the minimap
        self.defaultSize = 400
        self.minimumSize = 100
        self.maximumSize = 800
        self.minimapSize = self.defaultSize
        self.rightClickInteraction = True


        # Create a QGridLayout for the window
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Set margins (left, top, right, bottom) to zero
        self.setLayout(layout)

        # Create a widget and add the layout to it
        self.image_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.image_widget, 0, 0, 1, 1)

        # Create custom context menu
        self.createSlider()

        # Create a viexbox for the minimap
        self.viewbox = pg.ViewBox()
        self.viewbox.setMouseEnabled(x=False, y=False)
        # Invert and fix the aspect ratio of the viewbox to look like the original image
        self.viewbox.invertY(True)
        self.viewbox.setAspectLocked(True)

        # Update the minimap so that it responds to changes in the main window
        self.update_minimap(parent)
        # Set the value of the slider according to the default size
        self.slider.setValue(int((self.defaultSize - self.minimumSize) / self.maximumSize * 100))

        # Add the viewbox to the image widget
        self.image_widget.addItem(self.viewbox)

        # This marks the menu button as checked
        parent.minimapWindow.setChecked(True)

        # Create and add a highlight rectangle to the minimap with initial position [0, 0] and size [100, 100], outlined
        # in white with a 3-pixel width.
        self.highlight_area = pg.RectROI([0, 0], [100, 100], pen=pg.mkPen('w', width=3), resizable=False, movable=False)
        self.highlight_area.hoverEvent = lambda event: None
        # Remove all resize handles after initialization
        QtCore.QTimer.singleShot(0, lambda: [self.highlight_area.removeHandle(handle) for handle in
                                             self.highlight_area.getHandles()])
        # Add the highlight area to the viewbox
        self.viewbox.addItem(self.highlight_area)

    def closeEvent(self, event: QEvent):
        """
        Method to uncheck the button in the menu if the window is closed.
        It overrides closeEvent and is automatically called when the window is closed.
        It calls minimap_closed from gui.py.
        """
        # Notify the parent that the window is closing
        self.parent().minimap_closed()
        event.accept()  # Accept the event and close the window

    def update_minimap(self, parent):
        """
        Method to update the minimap.
        It takes the current image from the parent and updates the image in the minimap.
        """
        if parent.img.image is not None:
            # Obtain image data from the parent
            image = parent.img.image
            # Obtain saturation levels
            levels = parent.img.levels
            # Obtain current channel
            current_channel = parent.color

            # Set image
            self.mini_image = pg.ImageItem(image)
            # Display of RGB or greyscale image
            if current_channel == 0 or current_channel == 4:
                self.mini_image.setLookupTable(None)
            # Display of image using a pre-defined colormap corresponding to a specific color channel
            # (red, green, blue)
            elif current_channel < 4:
                self.mini_image.setLookupTable(parent.cmap[current_channel])
            # Display of spectral mage
            elif current_channel == 5:
                self.mini_image.setLookupTable(parent.cmap[0])

            self.mini_image.setLevels(levels)
            self.viewbox.addItem(self.mini_image)

            # Set the size of the minimap based on the aspect ratio of the image
            # this ensures that the aspect ratio is always correct
            aspect_ratio = self.mini_image.width() / self.mini_image.height()
            self.setFixedSize(int(self.minimapSize * aspect_ratio), self.minimapSize)
            # Ensure image fits viewbox
            self.viewbox.setLimits(xMin=0, xMax=parent.Lx, yMin=0, yMax=parent.Ly)

        # If there is no image and the minimap is checked, an empty window is opened
        else:
            self.setFixedSize(self.minimapSize, self.minimapSize)

    def set_highlight_area(self, normalized_x, normalized_y, normalized_width, normalized_height):
        """
        Method to set the highlight area on the minimap.
        The position and size of the rectangle are set based on the calculated normalized coordinates from the on_view method.

        Parameters:
        normalized_x (float): Normalized x-coordinate for the position.
        normalized_y (float): Normalized y-coordinate for the position.
        normalized_width (float): Normalized width for the size.
        normalized_height (float): Normalized height for the size.

        Returns:
        tuple: The calculated (x, y, width, height) coordinates.
        """

        if self.parent().img.image is not None:
            # Retrieve the height and width of the image
            img_height = self.parent().img.image.shape[0]
            img_width = self.parent().img.image.shape[1]

            # Calculate the position and size of the highlight area based on the normalized coordinates
            x = normalized_x * img_width
            y = normalized_y * img_height
            width = normalized_width * img_width
            height = normalized_height * img_height

            # Ensure the highlight area does not exceed the boundaries of the minimap
            if x + width > img_width:
                print("Error: Highlight area width exceeds image width.")
                width = img_width - x
            if y + height > img_height:
                print("Error: Highlight area height exceeds image height.")
                height = img_height - y

            # Set the position of the rectangle  area on the minimap
            # Move the rectangle to the calculated position
            self.highlight_area.setPos(x, y)

            # Set the size of the rectangle on the minimap
            # Adjust the rectangle's size to the calculated width and height
            self.highlight_area.setSize([width, height])

            # Return the calculated coordinates and dimensions of the rectangle
            return x, y, width, height
        else:
            print("Error: No image loaded in parent.")


    def sliderValueChanged(self, value):
        """
        Method to change the size of the minimap based on the slider value.
        This function will be called whenever the slider's value changes
        """
        # Calculate the new size of the minimap based on the slider value
        upscaleFactor = ((self.maximumSize - self.minimumSize) / 100)
        self.minimapSize = int(self.minimumSize + upscaleFactor * value)

        # this ensures that the aspect ratio is always correct
        if self.parent().img.image is not None:
            aspect_ratio = self.mini_image.width() / self.mini_image.height()
            self.setFixedSize(int(self.minimapSize * aspect_ratio), self.minimapSize)
        else:
            self.setFixedSize(self.minimapSize, self.minimapSize)

    def createSlider(self):
        """
        Method to create a custom context menu for the minimap. This menu contains a slider and an informative label.
        """
        # Create the custom context menu
        self.contextMenu = QMenu(self)

        # Create a QLabel and set its text
        label = QLabel()
        label.setText("Adjust window size")
        labelAction = QWidgetAction(self.contextMenu)
        labelAction.setDefaultWidget(label)
        self.contextMenu.addAction(labelAction)

        # Create a QSlider and add it to the menu
        self.slider = QSlider(QtCore.Qt.Horizontal)
        sliderAction = QWidgetAction(self.contextMenu)
        sliderAction.setDefaultWidget(self.slider)
        self.contextMenu.addAction(sliderAction)

        # Connect the slider's valueChanged signal to a function
        self.slider.valueChanged.connect(self.sliderValueChanged)

    def mousePressEvent(self, event):
        """
        Method to handle mouse press events. This overrides the default mousePressEvent method. Various information
        about the mouse event are passed to the method and handled accordingly. The method can distinguish between
        left and right mouse button clicks.

        The first part of the method checks if the right mouse button is clicked, in which case the custom context menu
        is displayed.

        The else branch of the method checks if the user left-clicks on the minimap, in which case it enables
        interactions such as navigating the main image view.

        Returns:
            Normalized (x, y) positions of the mouse click within the minimap.
        """
        # Check if the right mouse button was pressed
        if event.button() == QtCore.Qt.RightButton:
            # Show the custom context menu at the mouse position
            self.contextMenu.exec_(event.globalPos())
            # Delete hint after first interaction with the resize slider
            if self.rightClickInteraction:
                self.setWindowTitle("Minimap")
                self.rightClickInteraction = False
        else:

            # Obtain the position where the mouse was clicked within the minimap.
            viewboxPos = event.pos()

            # Save the translated position for later use
            self.lastClickPos = (viewboxPos.x(), viewboxPos.y())

            # Normalize the clicked position's coordinates to values between 0 and 1.
            normalized_x = (viewboxPos.x() - 9)/ self.viewbox.width()
            normalized_y = (viewboxPos.y() - 9)/ self.viewbox.height()
            self.normalizedClickPos = (normalized_x, normalized_y)

            # Change the view in the main window to the clicked position
            self.parent().center_view_on_position(normalized_x, normalized_y)


class ViewBoxNoRightDrag(pg.ViewBox):

    def __init__(self, parent=None, border=None, lockAspect=False, enableMouse=True,
                 invertY=False, enableMenu=True, name=None, invertX=False):
        pg.ViewBox.__init__(self, None, border, lockAspect, enableMouse, invertY,
                            enableMenu, name, invertX)
        self.parent = parent
        self.axHistoryPointer = -1

    def keyPressEvent(self, ev):
        """
        This routine should capture key presses in the current view box.
        The following events are implemented:
        +/= : moves forward in the zooming stack (if it exists)
        - : moves backward in the zooming stack (if it exists)

        """
        ev.accept()
        if ev.text() == "-":
            self.scaleBy([1.1, 1.1])
        elif ev.text() in ["+", "="]:
            self.scaleBy([0.9, 0.9])
        else:
            ev.ignore()


class ImageDraw(pg.ImageItem):
    """
    **Bases:** :class:`GraphicsObject <pyqtgraph.GraphicsObject>`
    GraphicsObject displaying an image. Optimized for rapid update (ie video display).
    This item displays either a 2D numpy array (height, width) or
    a 3D array (height, width, RGBa). This array is optionally scaled (see
    :func:`setLevels <pyqtgraph.ImageItem.setLevels>`) and/or colored
    with a lookup table (see :func:`setLookupTable <pyqtgraph.ImageItem.setLookupTable>`)
    before being displayed.
    ImageItem is frequently used in conjunction with
    :class:`HistogramLUTItem <pyqtgraph.HistogramLUTItem>` or
    :class:`HistogramLUTWidget <pyqtgraph.HistogramLUTWidget>` to provide a GUI
    for controlling the levels and lookup table used to display the image.
    """

    sigImageChanged = QtCore.Signal()

    def __init__(self, image=None, viewbox=None, parent=None, **kargs):
        super(ImageDraw, self).__init__()
        #self.image=None
        #self.viewbox=viewbox
        self.levels = np.array([0, 255])
        self.lut = None
        self.autoDownsample = False
        self.axisOrder = "row-major"
        self.removable = False

        self.parent = parent
        #kernel[1,1] = 1
        self.setDrawKernel(kernel_size=self.parent.brush_size)
        self.parent.current_stroke = []
        self.parent.in_stroke = False

    def mouseClickEvent(self, ev):
        if (self.parent.masksOn or
                self.parent.outlinesOn) and not self.parent.removing_region:
            is_right_click = ev.button() == QtCore.Qt.RightButton
            if self.parent.loaded \
                    and (is_right_click or ev.modifiers() & QtCore.Qt.ShiftModifier and not ev.double())\
                    and not self.parent.deleting_multiple:
                if not self.parent.in_stroke:
                    ev.accept()
                    self.create_start(ev.pos())
                    self.parent.stroke_appended = False
                    self.parent.in_stroke = True
                    self.drawAt(ev.pos(), ev)
                else:
                    ev.accept()
                    self.end_stroke()
                    self.parent.in_stroke = False
            elif not self.parent.in_stroke:
                y, x = int(ev.pos().y()), int(ev.pos().x())
                if y >= 0 and y < self.parent.Ly and x >= 0 and x < self.parent.Lx:
                    if ev.button() == QtCore.Qt.LeftButton and not ev.double():
                        idx = self.parent.cellpix[self.parent.currentZ][y, x]
                        if idx > 0:
                            if ev.modifiers() & QtCore.Qt.ControlModifier:
                                # delete mask selected
                                self.parent.remove_cell(idx)
                            elif ev.modifiers() & QtCore.Qt.AltModifier:
                                self.parent.merge_cells(idx)
                            elif self.parent.masksOn and not self.parent.deleting_multiple:
                                self.parent.unselect_cell()
                                self.parent.select_cell(idx)
                            elif self.parent.deleting_multiple:
                                if idx in self.parent.removing_cells_list:
                                    self.parent.unselect_cell_multi(idx)
                                    self.parent.removing_cells_list.remove(idx)
                                else:
                                    self.parent.select_cell_multi(idx)
                                    self.parent.removing_cells_list.append(idx)

                        elif self.parent.masksOn and not self.parent.deleting_multiple:
                            self.parent.unselect_cell()

    def mouseDragEvent(self, ev):
        ev.ignore()
        return

    def hoverEvent(self, ev):
        #QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        if self.parent.in_stroke:
            if self.parent.in_stroke:
                # continue stroke if not at start
                self.drawAt(ev.pos())
                if self.is_at_start(ev.pos()):
                    #self.parent.in_stroke = False
                    self.end_stroke()
        else:
            ev.acceptClicks(QtCore.Qt.RightButton)
            #ev.acceptClicks(QtCore.Qt.LeftButton)

    def create_start(self, pos):
        self.scatter = pg.ScatterPlotItem([pos.x()], [pos.y()], pxMode=False,
                                          pen=pg.mkPen(color=(255, 0, 0),
                                                       width=self.parent.brush_size),
                                          size=max(3 * 2,
                                                   self.parent.brush_size * 1.8 * 2),
                                          brush=None)
        self.parent.p0.addItem(self.scatter)

    def is_at_start(self, pos):
        thresh_out = max(6, self.parent.brush_size * 3)
        thresh_in = max(3, self.parent.brush_size * 1.8)
        # first check if you ever left the start
        if len(self.parent.current_stroke) > 3:
            stroke = np.array(self.parent.current_stroke)
            dist = (((stroke[1:, 1:] -
                      stroke[:1, 1:][np.newaxis, :, :])**2).sum(axis=-1))**0.5
            dist = dist.flatten()
            #print(dist)
            has_left = (dist > thresh_out).nonzero()[0]
            if len(has_left) > 0:
                first_left = np.sort(has_left)[0]
                has_returned = (dist[max(4, first_left + 1):] < thresh_in).sum()
                if has_returned > 0:
                    return True
                else:
                    return False
            else:
                return False

    def end_stroke(self):
        self.parent.p0.removeItem(self.scatter)
        if not self.parent.stroke_appended:
            self.parent.strokes.append(self.parent.current_stroke)
            self.parent.stroke_appended = True
            self.parent.current_stroke = np.array(self.parent.current_stroke)
            ioutline = self.parent.current_stroke[:, 3] == 1
            self.parent.current_point_set.append(
                list(self.parent.current_stroke[ioutline]))
            self.parent.current_stroke = []
            if self.parent.autosave:
                self.parent.add_set()
        if len(self.parent.current_point_set) and len(
                self.parent.current_point_set[0]) > 0 and self.parent.autosave:
            self.parent.add_set()
        self.parent.in_stroke = False

    def tabletEvent(self, ev):
        pass
        #print(ev.device())
        #print(ev.pointerType())
        #print(ev.pressure())

    def drawAt(self, pos, ev=None):
        mask = self.strokemask
        stroke = self.parent.current_stroke
        pos = [int(pos.y()), int(pos.x())]
        dk = self.drawKernel
        kc = self.drawKernelCenter
        sx = [0, dk.shape[0]]
        sy = [0, dk.shape[1]]
        tx = [pos[0] - kc[0], pos[0] - kc[0] + dk.shape[0]]
        ty = [pos[1] - kc[1], pos[1] - kc[1] + dk.shape[1]]
        kcent = kc.copy()
        if tx[0] <= 0:
            sx[0] = 0
            sx[1] = kc[0] + 1
            tx = sx
            kcent[0] = 0
        if ty[0] <= 0:
            sy[0] = 0
            sy[1] = kc[1] + 1
            ty = sy
            kcent[1] = 0
        if tx[1] >= self.parent.Ly - 1:
            sx[0] = dk.shape[0] - kc[0] - 1
            sx[1] = dk.shape[0]
            tx[0] = self.parent.Ly - kc[0] - 1
            tx[1] = self.parent.Ly
            kcent[0] = tx[1] - tx[0] - 1
        if ty[1] >= self.parent.Lx - 1:
            sy[0] = dk.shape[1] - kc[1] - 1
            sy[1] = dk.shape[1]
            ty[0] = self.parent.Lx - kc[1] - 1
            ty[1] = self.parent.Lx
            kcent[1] = ty[1] - ty[0] - 1

        ts = (slice(tx[0], tx[1]), slice(ty[0], ty[1]))
        ss = (slice(sx[0], sx[1]), slice(sy[0], sy[1]))
        self.image[ts] = mask[ss]

        for ky, y in enumerate(np.arange(ty[0], ty[1], 1, int)):
            for kx, x in enumerate(np.arange(tx[0], tx[1], 1, int)):
                iscent = np.logical_and(kx == kcent[0], ky == kcent[1])
                stroke.append([self.parent.currentZ, x, y, iscent])
        self.updateImage()

    def setDrawKernel(self, kernel_size=3):
        bs = kernel_size
        kernel = np.ones((bs, bs), np.uint8)
        self.drawKernel = kernel
        self.drawKernelCenter = [
            int(np.floor(kernel.shape[0] / 2)),
            int(np.floor(kernel.shape[1] / 2))
        ]
        onmask = 255 * kernel[:, :, np.newaxis]
        offmask = np.zeros((bs, bs, 1))
        opamask = 100 * kernel[:, :, np.newaxis]
        self.redmask = np.concatenate((onmask, offmask, offmask, onmask), axis=-1)
        self.strokemask = np.concatenate((onmask, offmask, onmask, opamask), axis=-1)
