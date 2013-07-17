#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore, QtGui
import collections
import DIMputs as my_DI
from PyQt4.QtCore import *

        
class MainWindow(QtGui.QWidget):
    updateSignal = QtCore.pyqtSignal()
    def __init__(self, parent=None):
    
    
        self.path = ""
        self.cur_rein_num = 0
        self.data = None
        self.format = ""
        self.cell_limit = float("inf")

        super(MainWindow, self).__init__(parent)

        # upper buttons
        pathLabel = QtGui.QLabel("Path:")
        self.pathLabel = QtGui.QLabel(self.path)
        self.pathLabel.setFrameStyle(QtGui.QFrame.StyledPanel | 
                                     QtGui.QFrame.Sunken)
        self.pathLabel.setToolTip("Current File")
        self.pathButton = QtGui.QPushButton("P&ath...")
        self.pathButton.setToolTip("Set the item you want to inspect")
        self.connect(self.pathButton, QtCore.SIGNAL("clicked()"), self.setPath)
        

        # cell limit label and text field
        cell_limit_label = QtGui.QLabel("Cell Limit:")
        self.cell_limit_chooser = QtGui.QSpinBox()
        self.cell_limit_chooser.setMaximum(99999)
        cell_limit_label.setToolTip("Limits the number of elements per cell")
        self.cell_limit_chooser.setToolTip("Set to zero to show all elements")

        # format drop down menu
        self.format_drop = QtGui.QToolButton(self)
        self.format_drop.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.format_drop.setMenu(QtGui.QMenu(self.format_drop))
        self.format_drop.setText("Format")

        self.format_syntax = QtGui.QPushButton("Syntax")
        self.format_phrase = QtGui.QPushButton("Phrase")
        self.format_hieroCube = QtGui.QPushButton("Hiero Cube")
        self.format_phraseStackFlag = QtGui.QPushButton("Phrase Stack (flag)")
        self.format_phraseStackVerbose = QtGui.QPushButton("Phrase Stack (verbose)")
        

        format_action_syntax = QtGui.QWidgetAction(self.format_drop)
        format_action_syntax.setDefaultWidget(self.format_syntax)

        format_action_phrase = QtGui.QWidgetAction(self.format_drop)
        format_action_phrase.setDefaultWidget(self.format_phrase)
        
        format_action_hieroCube = QtGui.QWidgetAction(self.format_drop)
        format_action_hieroCube.setDefaultWidget(self.format_hieroCube)
        
        format_action_phraseStackFlag = QtGui.QWidgetAction(self.format_drop)
        format_action_phraseStackFlag.setDefaultWidget(self.format_phraseStackFlag)
        
        format_action_phraseStackVerbose = QtGui.QWidgetAction(self.format_drop)
        format_action_phraseStackVerbose.setDefaultWidget(self.format_phraseStackVerbose)
        

        self.format_drop.menu().addAction(format_action_syntax)
        self.format_drop.menu().addAction(format_action_phrase)
        self.format_drop.menu().addAction(format_action_hieroCube)
        self.format_drop.menu().addAction(format_action_phraseStackFlag)
        self.format_drop.menu().addAction(format_action_phraseStackVerbose)

        
        self.format_syntax.clicked.connect(self.set_format_syntax)
        self.format_phrase.clicked.connect(self.set_format_phrase)
        self.format_hieroCube.clicked.connect(self.set_format_hieroCube)
        self.format_phraseStackFlag.clicked.connect(self.set_format_phraseStackFlag)
        self.format_phraseStackVerbose.clicked.connect(self.set_format_phraseStackVerbose)



        # table
        self.table_widget = HoverTable(self)
        self.w = []  # future popup window
        # self.table_widget = QtGui.QTableWidget(self)

        # lower buttons        
        self.buttonBox = QtGui.QDialogButtonBox()
        self.sentence_spinbox = QtGui.QSpinBox(parent=self.buttonBox)
        self.sentence_spinbox.setMaximum(999999)

        self.goto_button = self.buttonBox.addButton(
            "&GoTo", QtGui.QDialogButtonBox.ActionRole)
        self.next_button = self.buttonBox.addButton(
            "&Next", QtGui.QDialogButtonBox.ActionRole)
        self.prev_button = self.buttonBox.addButton(
            "&Prev", QtGui.QDialogButtonBox.ActionRole)
        self.next_button.clicked.connect(self.next_parse)
        self.prev_button.clicked.connect(self.prev_parse)
        self.goto_button.clicked.connect(self.cur_parse)
        self.quit_button = self.buttonBox.addButton(
            "&Quit", QtGui.QDialogButtonBox.ActionRole)
        self.quit_button.clicked.connect(
            QtCore.QCoreApplication.instance().quit)
        
        # Disable navigation buttons until data is loaded: see setPath for reactivation
        self.goto_button.setDisabled(True)
        self.next_button.setDisabled(True)
        self.prev_button.setDisabled(True)
        

        


        # Layouting

        layout = QtGui.QVBoxLayout()

        topLayout = QtGui.QHBoxLayout()
        topLayout.addWidget(self.format_drop)
        topLayout.addWidget(cell_limit_label)
        topLayout.addWidget(self.cell_limit_chooser)
        self.cell_limit_chooser.valueChanged.connect(self.setCellLimit)
        topLayout.addWidget(pathLabel)
        topLayout.addWidget(self.pathLabel, 1)
        topLayout.addWidget(self.pathButton)

        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addWidget(self.buttonBox)

        layout.addLayout(topLayout)
        layout.addWidget(self.table_widget)
        layout.addLayout(bottomLayout)

        self.sentence_spinbox.valueChanged.connect(self.set_cur_rein_num)

        self.setLayout(layout)
        self.updateSignal.connect(self.update_table)
        
        QtCore.QObject.connect(
        self.table_widget,
        QtCore.SIGNAL("cellDoubleClicked(int, int)"),
        self.popup)
        

    def setCellLimit(self, value):
        if value == 0:
            value = float("inf")
        self.cell_limit = value
            
            
    def setPath(self):
        path = QtGui.QFileDialog.getOpenFileName(self,
                "Select File", self.pathLabel.text())
        if path:
            self.goto_button.setDisabled(False)
            self.prev_button.setDisabled(False)
            self.next_button.setDisabled(False)
            self.pathLabel.setText(QtCore.QDir.toNativeSeparators(path))
            self.path = unicode(path)
            self.data = my_DI.DataInput(self.path)
            if self.format == "syntax":
                self.data.read_syntax()
            elif self.format == "phrase":
                self.data.read_phrase()
            elif self.format == "hieroCube":
                self.data.read_hiero_cubes(self.cell_limit)
            elif self.format == "phraseStackFlag":
                self.data.read_phrase_stack_flag(self.cell_limit)
            elif self.format == "phraseStackVerbose":
                self.data.read_phrase_stack_verbose(self.cell_limit)
            


    def next_parse(self):
        self.cur_rein_num += 1
        if self.cur_rein_num < 0:
            self.cur_rein_num = len(self.data.sentences) + self.cur_rein_num
        if self.cur_rein_num >= len(self.data.sentences):
            self.cur_rein_num = 0 
        self.sentence_spinbox.setValue(self.cur_rein_num)
        self.populate(self.cur_rein_num)
            
    def prev_parse(self):
        self.cur_rein_num -= 1
        if self.cur_rein_num < 0:
            self.cur_rein_num = len(self.data.sentences) + self.cur_rein_num
        if self.cur_rein_num >= len(self.data.sentences):
            self.cur_rein_num = 0
        self.sentence_spinbox.setValue(self.cur_rein_num)
        self.populate(self.cur_rein_num)
    
    def cur_parse(self):
        if self.cur_rein_num >= len(self.data.sentences):
            self.cur_rein_num = 0
        self.sentence_spinbox.setValue(self.cur_rein_num)
        self.populate(self.cur_rein_num)
        
        
    def set_cur_rein_num(self, value):
        self.cur_rein_num = value  # self.sentence_spinbox.value()

    def populate(self, cur_rein_num):
        cur_sent = self.data.sentences[cur_rein_num]
        nrows, ncols = cur_sent.length + 1, cur_sent.length + 1
        nrows, ncols = ncols, nrows  # switcher
        self.table_widget.setSortingEnabled(False)
        self.table_widget.setRowCount(nrows)
        self.table_widget.setColumnCount(ncols)
        for i in range(nrows):
            for j in range(ncols):
                try:
                    # item = TableItem("%s:%s \n %s"
                    #                  % (i+1, j+1, cur_sent.spans[(i,j)]))
                    item = str(i) + ".." + str(j) + "  \n"
                    if isinstance(cur_sent.spans[(i, j)], basestring):
                        item += cur_sent.spans[(i, j)] + "\n"
                    else:
                        for rule in cur_sent.spans[(i, j)]:
                            item += str(rule) + "\n"
                        if cur_sent.spans[(i, j)] == []:
                            if j - i < 0:
                                item = ""
                            else:
                                item = "-"
                    item = TableItem(item.decode("utf-8"))
                    

                except KeyError:
                    if j - i < 0:
                        item = QtGui.QTableWidgetItem("")
                    else:
                        item = QtGui.QTableWidgetItem("-")
                self.table_widget.setItem(i, j, item)
                self.table_widget.setColumnWidth(j, 40)
#                self.connect(
#                    self.table_widget, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem)"),
#                    self.popup)

        self.updateSignal.emit()
        self.table_widget.setSortingEnabled(True)
        
    def update_table(self):
        self.table_widget.sortItems(0, QtCore.Qt.DescendingOrder)




    def set_format_syntax(self):
        self.format = "syntax"
        self.format_drop.setText("Syntax")

    def set_format_phrase(self):
        self.format = "phrase"
        self.format_drop.setText("Phrase")
        
    def set_format_hieroCube(self):
        self.format = "hieroCube"
        self.format_drop.setText("Hiero Cube")
        
    def set_format_phraseStackFlag(self):
        self.format = "phraseStackFlag"
        self.format_drop.setText("Phrase Stack (flag)")
        
    def set_format_phraseStackVerbose(self):
        self.format = "phraseStackVerbose"
        self.format_drop.setText("Phrase Stack (verbose)")
    
        
        
#    @QtCore.pyqtSlot(QtGui.QTableWidgetItem, result=QtCore.QObject)
#    def popup(self, item):
#    @pyqtSlot(int, int, result=QtCore.QObject)
#    @pyqtSignature("popup(int int)")
    def popup(self, r, c):
#        """ C++: QObject popup(int, int) """
#        self.w = PopUpCell(item.text)
        self.w.append(PopUpCell(self.table_widget.item(r, c).text()))
        # self.w.setGeometry(QRect(100, 100, 400, 200))
        self.w[-1].show()
        

class HoverTable(QtGui.QTableWidget):
    
    def __init__(self, parent=None):
        super(HoverTable, self).__init__(parent)
        self.setMouseTracking(True)
        self.horizontalHeader().setClickable(False)
#        self.verticalHeader().setDefaultSectionSize(self.verticalHeader.fontMetrics().height()+2);
        


class PopUpCell(QtGui.QWidget):
    def __init__(self, cell_text):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        text_list = map(lambda x: x, cell_text.split("\n"))
        wind_cont = QtGui.QTextEdit()  # "<br/>".join(text_list[1:]))
        wind_cont.setReadOnly(True)
        wind_cont.setWindowTitle(text_list[0])
        wind_cont.setPlainText(cell_text)  # "\n".join(text_list))
        layout.addWidget(wind_cont)
        self.setWindowTitle(text_list[0])
        self.setLayout(layout)
        self.resize(960, 320)


    

        
class TableItem(QtGui.QTableWidgetItem):
    
    def __init__(self, cell_text, type=1000):
        super(TableItem, self).__init__(cell_text)
        if len(cell_text.split("\n")) > 20:
            self.setToolTip("\n".join(cell_text.split("\n")[:19]))
        else:
            self.setToolTip(cell_text)
        self.cell_text = cell_text


