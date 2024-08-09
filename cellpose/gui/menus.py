"""
Copyright © 2023 Howard Hughes Medical Institute, Authored by Carsen Stringer and Marius Pachitariu.
"""

import qtpy
from qtpy.QtWidgets import QAction
from . import io
from .. import models


def mainmenu(parent):
    main_menu = parent.menuBar()
    file_menu = main_menu.addMenu("&File")
    # load processed data
    loadImg = QAction("&Load image (*.tif, *.png, *.jpg)", parent)
    loadImg.setShortcut("Ctrl+L")
    loadImg.triggered.connect(lambda: io._load_image(parent))
    file_menu.addAction(loadImg)

    parent.autoloadMasks = QAction("Autoload masks from _masks.tif file", parent,
                                   checkable=True)
    parent.autoloadMasks.setChecked(False)
    file_menu.addAction(parent.autoloadMasks)

    parent.disableAutosave = QAction("Disable autosave _seg.npy file", parent,
                                     checkable=True)
    parent.disableAutosave.setChecked(False)
    file_menu.addAction(parent.disableAutosave)

    parent.loadMasks = QAction("Load &masks (*.tif, *.png, *.jpg)", parent)
    parent.loadMasks.setShortcut("Ctrl+M")
    parent.loadMasks.triggered.connect(lambda: io._load_masks(parent))
    file_menu.addAction(parent.loadMasks)
    parent.loadMasks.setEnabled(False)

    loadManual = QAction("Load &processed/labelled image (*_seg.npy)", parent)
    loadManual.setShortcut("Ctrl+P")
    loadManual.triggered.connect(lambda: io._load_seg(parent))
    file_menu.addAction(loadManual)

    parent.saveSet = QAction("&Save masks and image (as *_seg.npy)", parent)
    parent.saveSet.setShortcut("Ctrl+S")
    parent.saveSet.triggered.connect(lambda: io._save_sets(parent))
    file_menu.addAction(parent.saveSet)
    parent.saveSet.setEnabled(False)

    parent.savePNG = QAction("Save masks as P&NG/tif", parent)
    parent.savePNG.setShortcut("Ctrl+N")
    parent.savePNG.triggered.connect(lambda: io._save_png(parent))
    file_menu.addAction(parent.savePNG)
    parent.savePNG.setEnabled(False)

    parent.saveOutlines = QAction("Save &Outlines as text for imageJ", parent)
    parent.saveOutlines.setShortcut("Ctrl+O")
    parent.saveOutlines.triggered.connect(lambda: io._save_outlines(parent))
    file_menu.addAction(parent.saveOutlines)
    parent.saveOutlines.setEnabled(False)

    parent.saveROIs = QAction("Save outlines as .zip archive of &ROI files for ImageJ",
                              parent)
    parent.saveROIs.setShortcut("Ctrl+R")
    parent.saveROIs.triggered.connect(lambda: io._save_rois(parent))
    file_menu.addAction(parent.saveROIs)
    parent.saveROIs.setEnabled(False)

    parent.saveFlows = QAction("Save &Flows and cellprob as tif", parent)
    parent.saveFlows.setShortcut("Ctrl+F")
    parent.saveFlows.triggered.connect(lambda: io._save_flows(parent))
    file_menu.addAction(parent.saveFlows)
    parent.saveFlows.setEnabled(False)

    # Save settings action from main

    parent.saveSettings = QAction("Save Settings as .&json", parent)
    parent.saveSettings.setShortcut("Ctrl+J")
    parent.saveSettings.triggered.connect(lambda: io._save_settings(parent))
    file_menu.addAction(parent.saveSettings)
    parent.saveSettings.setEnabled(True)

    """
    This adds a new menu item for saving features as a .csv file. 
    The user can activate this function to export specific data directly from the GUI.
    The function `_save_features_as_csv` from the `io` module is called when the user clicks on the menu item.
    It is disabled by default and only activated if an image is segmented and of the type tif/tiff.
    """
    parent.saveFeaturesCsv = QAction("Save Features as .&csv", parent)
    parent.saveFeaturesCsv.setShortcut("Ctrl+Shift+C")
    parent.saveFeaturesCsv.triggered.connect(lambda: io._save_features_csv(parent))
    file_menu.addAction(parent.saveFeaturesCsv)
    parent.saveFeaturesCsv.setEnabled(False)

    """
    This creates a new menu item for the minimap that the user can activate.
    It is deactivated by default and has to be checked.
    The minimap_window function is called from gui.py when the user clicks on the menu item.
    """
    parent.minimapWindow = QAction("&Minimap", parent, checkable=True)
    parent.minimapWindow.setChecked(False)
    parent.minimapWindow.triggered.connect(parent.minimap_window)
    file_menu.addAction(parent.minimapWindow)


def editmenu(parent):
    main_menu = parent.menuBar()
    edit_menu = main_menu.addMenu("&Edit")
    parent.undo = QAction("Undo previous mask/trace", parent)
    parent.undo.setShortcut("Ctrl+Z")
    parent.undo.triggered.connect(parent.undo_action)
    parent.undo.setEnabled(False)
    edit_menu.addAction(parent.undo)

    parent.redo = QAction("Undo remove mask", parent)
    parent.redo.setShortcut("Ctrl+Y")
    parent.redo.triggered.connect(parent.undo_remove_action)
    parent.redo.setEnabled(False)
    edit_menu.addAction(parent.redo)

    parent.ClearButton = QAction("Clear all masks", parent)
    parent.ClearButton.setShortcut("Ctrl+0")
    parent.ClearButton.triggered.connect(parent.clear_all)
    parent.ClearButton.setEnabled(False)
    edit_menu.addAction(parent.ClearButton)

    parent.remcell = QAction("Remove selected cell (Ctrl+CLICK)", parent)
    parent.remcell.setShortcut("Ctrl+Click")
    parent.remcell.triggered.connect(parent.remove_action)
    parent.remcell.setEnabled(False)
    edit_menu.addAction(parent.remcell)

    parent.mergecell = QAction("FYI: Merge cells by Alt+Click", parent)
    parent.mergecell.setEnabled(False)
    edit_menu.addAction(parent.mergecell)


def modelmenu(parent):
    main_menu = parent.menuBar()
    io._init_model_list(parent)
    model_menu = main_menu.addMenu("&Models")
    parent.addmodel = QAction("Add custom torch model to GUI", parent)
    #parent.addmodel.setShortcut("Ctrl+A")
    parent.addmodel.triggered.connect(parent.add_model)
    parent.addmodel.setEnabled(True)
    model_menu.addAction(parent.addmodel)

    parent.removemodel = QAction("Remove selected custom model from GUI", parent)
    #parent.removemodel.setShortcut("Ctrl+R")
    parent.removemodel.triggered.connect(parent.remove_model)
    parent.removemodel.setEnabled(True)
    model_menu.addAction(parent.removemodel)

    parent.newmodel = QAction("&Train new model with image+masks in folder", parent)
    parent.newmodel.setShortcut("Ctrl+T")
    parent.newmodel.triggered.connect(parent.new_model)
    parent.newmodel.setEnabled(False)
    model_menu.addAction(parent.newmodel)

    openTrainHelp = QAction("Training instructions", parent)
    openTrainHelp.triggered.connect(parent.train_help_window)
    model_menu.addAction(openTrainHelp)


def helpmenu(parent):
    main_menu = parent.menuBar()
    help_menu = main_menu.addMenu("&Help")

    openHelp = QAction("&Help with GUI", parent)
    openHelp.setShortcut("Ctrl+H")
    openHelp.triggered.connect(parent.help_window)
    help_menu.addAction(openHelp)

    openGUI = QAction("&GUI layout", parent)
    openGUI.setShortcut("Ctrl+G")
    openGUI.triggered.connect(parent.gui_window)
    help_menu.addAction(openGUI)

    openTrainHelp = QAction("Training instructions", parent)
    openTrainHelp.triggered.connect(parent.train_help_window)
    help_menu.addAction(openTrainHelp)


