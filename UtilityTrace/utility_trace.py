# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UtilityTrace
                                 A QGIS plugin
 Trace Utility
                              -------------------
        begin                : 2018-02-15
        git sha              : $Format:%H$
        copyright            : (C) 2018 by a
        email                : a
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
from qgis.utils import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from utility_trace_dialog import UtilityTraceDialog
import os.path


class UtilityTrace:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'UtilityTrace_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Utility Trace')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'UtilityTrace')
        self.toolbar.setObjectName(u'UtilityTrace')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('UtilityTrace', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = UtilityTraceDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/UtilityTrace/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Trace Utilities'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Utility Trace'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
            
        self.dlg.comboBox.addItems(layer_list)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            
            ##Select node
            selected_node = layer.selectedFeatures()[0] ##Can improve to trace multiple features
            
            #Line layer is selected. 
            #TODO Make sure it is a line layer.
            selectedLayerIndex = self.dlg.comboBox.currentIndex()
            line_layer = layers[selectedLayerIndex]
            
            supply_found = False ##When supply found, true will be returned
            supply_node = ""
            
            ##Find the points on the line where the line end is equal to the node geometry.
            lines = self.find_line(selected_node.geometry().asPoint(), line_layer)
            #TODO also initialize an array here which tracks the lines that are taken. This should split into multiple arrays if multiple paths taken.
            
            while not supply_found:
                ##Find nodes where the pipes start
                nodes = self.find_node (layer, lines, line_layer)
                QgsMessageLog.logMessage(str(nodes))
                
                ##Assesss if nodes are supply nodes or not.
                supply_node, supply_found = self.node_check(layer, nodes)
                ##If supply has been found, break rest of while loop
                if supply_found == True:
                    break
                
                ##If no supply node found, find new lines and repeat.
                lines = []
                request = QgsFeatureRequest()
                request.setFilterFids(nodes)
                current_nodes = layer.getFeatures(request)
                for node in current_nodes:
                    lines = lines + self.find_line(node.geometry().asPoint(), line_layer)
                    
                ##If ever there are no lines with end point at nodes it is likely there is no supply node at the source of the nodes.
                if lines == []:
                    QgsMessageLog.logMessage("No supply node found. Check the logical layout of the network.")
                    break
                
                
            QgsMessageLog.logMessage(supply_node)
                
            
    def find_line (self, node_geom, line_layer):
        """Find every line which has a node as an end point. Return as array."""
        lines_searched = []
        for feat in line_layer.getFeatures():
            end_geom = feat.geometry().asPolyline()[-1]
            if end_geom == node_geom:
                lines_searched.append(feat.id())
        return lines_searched
        
    def find_node (self, layer, lines, line_layer):
        """Return the start node for a line."""
        nodes_searched = []
        request = QgsFeatureRequest()
        request.setFilterFids(lines)
        full_lines = line_layer.getFeatures(request)
        for feat in full_lines:
            start_uuid = feat.attributes()[1]
            ##Find nodes matching start geom
            for node in layer.getFeatures():
                node_uuid = node.attributes()[1]
                if node_uuid == start_uuid:
                    nodes_searched.append(node.id())
                    break
        return nodes_searched

    def node_check (self, layer, node_list):
        """Find if a node is supply node, and return the node and update supply_found."""
        supply = False
        supply_nodes = ""
        request = QgsFeatureRequest()
        request.setFilterFids(node_list)
        full_nodes = layer.getFeatures(request)
        for node in full_nodes:
            type = node.attributes()[0]
            if type == "Supply":
                supply_nodes = supply_nodes + " " + node.attributes()[1]
                supply = True
        return supply_nodes, supply 