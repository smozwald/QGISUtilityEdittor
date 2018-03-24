# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UtilityEdittingV2
                                 A QGIS plugin
 Edit Utility Networks
                              -------------------
        begin                : 2018-01-19
        git sha              : $Format:%H$
        copyright            : (C) 2018 by sam O
        email                : xx
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
import math
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from utility_editting_dockwidget import UtilityEdittingV2DockWidget
import os.path


class UtilityEdittingV2:
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
            'UtilityEdittingV2_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Utility Editor V2')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'UtilityEdittingV2')
        self.toolbar.setObjectName(u'UtilityEdittingV2')

        #print "** INITIALIZING UtilityEdittingV2"

        self.pluginIsActive = False
        self.dockwidget = None


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
        return QCoreApplication.translate('UtilityEdittingV2', message)


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

        icon_path = ':/plugins/UtilityEdittingV2/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Widget for Editting'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING UtilityEdittingV2"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD UtilityEdittingV2"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Utility Editor V2'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""
        
        ##Define the point and line features to be used.
        self.pipe_layer = QgsVectorLayer("C:/Users/SAM/Desktop/Uni/Internship/15JanTask/Pipes.shp", "Pipes", "ogr")
        self.point_layer = QgsVectorLayer("C:/Users/SAM/Desktop/Uni/Internship/15JanTask/Point_Features.shp", "Point_Features", "ogr")
        
        # ##Measure distances
        self.distance = QgsDistanceArea()
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrsId(4326)
        self.distance.setSourceCrs(crs)
        self.distance.setEllipsoidalMode(True)
        self.distance.setEllipsoid('WGS84')
        
        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING UtilityEdittingV2"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = UtilityEdittingV2DockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
            ##Connect and disconnect plugin
            QObject.connect(self.dockwidget.Activate, SIGNAL("clicked()"),self.activated)
            QObject.connect(self.dockwidget.Deactivate, SIGNAL("clicked()"),self.deactivated)
            
    def activated(self): 
        QgsMessageLog.logMessage("Getting there.")
        self.iface.actionSelect().trigger()
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("selectionChanged(QgsMapLayer *)"), self.connect_signals)
        QObject.connect(self.iface.mapCanvas(), SIGNAL("selectionChanged(QgsMapLayer *)"), self.connect_signals)		
		
    def deactivated(self):       
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("selectionChanged(QgsMapLayer *)"), self.connect_signals)
    
    def connect_signals(self, layer):
        """Connect signals to selected layer."""
        self.layer = layer
        self.layer.committedFeaturesAdded.connect(self.feat_added)
            
    def feat_added(self, layer, new_features):
    
        """Check if new point is splitting a line and if so create a new pipe line and adjust geometries."""
        if self.layer.name() == self.point_layer.name():
            ##See if a point is close enough to intersect a line. Create index of pipes.
            provider = self.pipe_layer.dataProvider()
            sp_index = QgsSpatialIndex()
            pipe_feat = QgsFeature()
            pipe_add = provider.getFeatures()
            while pipe_add.nextFeature(pipe_feat):
                sp_index.insertFeature(pipe_feat)
            
            ##Find nearest neighbour and if distance is less than 5, place point on line and then intersect.
            for feat in new_features:
                geom=feat.geometry().asPoint()
                line = sp_index.nearestNeighbor (geom, 1)
                
                request = QgsFeatureRequest()
                request.setFilterFid(line[0])
                closest_line = self.pipe_layer.getFeatures(request).next()
                ##Get start and end of line
                line_geom =closest_line.geometry().asPolyline()
                line_start = QgsPoint(line_geom[0])
                line_end =  QgsPoint(line_geom[1])
                
                int_pt = self.point_snap(geom, line_start, line_end)
                ##If within tolerance
                dist = self.min_dist(geom, int_pt)
                if dist < 15:
                    self.intersect_pipe(feat, int_pt, closest_line)
                else:
                    QgsMessageLog.logMessage("Point outside of tolerance to be able to snap to line.")
            
        elif self.layer.name() == self.pipe_layer.name():
            
            ##Create a spatial index of points to find nearest neighbours of new lines.
            provider = self.point_layer.dataProvider()
            sp_index = QgsSpatialIndex()
            point_feat = QgsFeature()
            point_add = provider.getFeatures()
            while point_add.nextFeature(point_feat):
                sp_index.insertFeature(point_feat)
                
                
            for feat in new_features:
                ##See if added feature correctly corresponds to features
                geom = feat.geometry().asPolyline()
                line_start = geom[0]
                line_end = geom[-1]
                
                ##Find nearest neighbour to each point in point layer. Check they aren't the same.
                start_pt = sp_index.nearestNeighbor (line_start, 1)
                end_pt = sp_index.nearestNeighbor (line_end, 1)
                request = QgsFeatureRequest()
                request.setFilterFid(start_pt[0])
                start_pt_feat = self.point_layer.getFeatures(request).next()
                request.setFilterFid(end_pt[0])
                end_pt_feat = self.point_layer.getFeatures(request).next()
                start_pt_guid = start_pt_feat.attributes()[1]
                start_pt_geom = start_pt_feat.geometry().asPoint()
                end_pt_guid = end_pt_feat.attributes()[1]
                end_pt_geom = end_pt_feat.geometry().asPoint()
                
                start_dist = self.min_dist(line_start, start_pt_geom)
                end_dist = self.min_dist(line_end, end_pt_geom)
               
                ##If feature is within tolerable distance of points, add to map.
                if (start_dist < 15 and end_dist < 15):
                    if start_pt_geom != line_start or end_pt_geom != line_end:
                        self.alter_pipe(feat, start_pt_guid, start_pt_geom, end_pt_guid, end_pt_geom)
                ##Also check for GUID if they're equal.
                else: 
                    QgsMessageLog.logMessage("Feature outside of tolerable snap distance. Feature deleted.")
                    self.pipe_layer.startEditing()
                    self.pipe_layer.deleteFeature(feat.id())
                    self.pipe_layer.commitChanges()
            
    def alter_pipe(self, feat, start_guid, start_geom, end_guid, end_geom):
        """Will check pipes on commit. Will then look at nearest points and snap them to these. Also update GUIDs."""
        self.pipe_layer.startEditing()
        
        ##Set from and to guids. If "" value entered, will not be updated.
        if not start_guid == "":
            self.pipe_layer.changeAttributeValue(feat.id(), 1, start_guid)
        if not end_guid == "":
            self.pipe_layer.changeAttributeValue(feat.id(), 2, end_guid)
        
        newgeom = QgsGeometry.fromPolyline([QgsPoint(start_geom), QgsPoint(end_geom)])
        self.pipe_layer.changeGeometry(feat.id(), newgeom)
        self.pipe_layer.commitChanges()
        
    def intersect_pipe(self, feat, int_pt, old_line):
        """Intersects a pipe feature, altering the original feature to have the intersect point as the end point, and creating a second feature for the rest of the line."""
        self.point_layer.startEditing()
        
        new_geom = QgsGeometry.fromPoint(int_pt)
        self.point_layer.changeGeometry(feat.id(), new_geom)
        self.point_layer.commitChanges()
        
        ##Create a new pipe layer, first duplicating old layer.
        self.pipe_layer.startEditing()
        fields = self.pipe_layer.fields()
        old_attrs = old_line.attributes()
        old_start = old_line.geometry().asPolyline()[0]
        old_end = old_line.geometry().asPolyline()[1]
        
        if (QgsPoint(old_start) != int_pt):   #If-else used to ensure only one feature with the correct geometries is added, otherwise repetitve overlapping features occur.
            new_guid = QUuid.createUuid().toString()
            
            new_line = QgsFeature()
            ##Set new line geometry to start at the new point and end at old line end.
            new_line.setGeometry(QgsGeometry.fromPolyline([int_pt, QgsPoint(old_end)]))
            new_line.setFields(fields)
            new_line.setAttributes([new_guid, feat.attributes()[1], old_line.attributes()[2]]) #Set attributes of line, based on new guid value, intersecting point guid and old guid.
            
            ##Error occurs involving repetitive lines being made with identical start and end guids. If this occurs, these new lines should be deleted.
            self.pipe_layer.addFeatures([new_line])
            QgsMessageLog.logMessage(str(new_line.attributes()))
            self.pipe_layer.commitChanges()
            
            ##Alter the two geometries for first and second line.
            self.alter_pipe(old_line, "", old_start, feat.attributes()[1], int_pt)
        else:
            self.pipe_layer.stopEditing()
        
        
         
    def point_snap(self, new_pt, start_pt, end_pt):
        """Use start and end point of line and a new pt to find minimum perpendicular distance. Assumes line only has the two end vertices."""
        line_sqr = end_pt.sqrDist(start_pt)

        k = (((new_pt.x() - start_pt.x()) * (end_pt.x() - start_pt.x()) + (new_pt.y() - start_pt.y()) * (end_pt.y() - start_pt.y()))) / (line_sqr)
        new_x = start_pt.x() + k * (end_pt.x() - start_pt.x())
        new_y = start_pt.y() + k * (end_pt.y() - start_pt.y())
        line_pt = QgsPoint(new_x, new_y)
        
        return line_pt
        
    def min_dist (self, pt1, pt2):
        """Calculate minimum distance between two points."""
        dist = math.sqrt ((pt2.x() - pt1.x())**2 + (pt2.y()-pt1.y())**2)
        return dist
    
    # def point_added (self, fid):      ##See Below
        # pass
        
    # def pipe_added (self, fid):   #Was intended to update when feature was added. DIdn't work
        # """See if line is within a close enough distance to a valve or weld, and if it is then snapping its start and end point to the valves."""
        # QgsMessageLog.logMessage(str(fid))
        # ##Retrieve the line based on new fid start and end point of the added line.
        # request = QgsFeatureRequest()
        # request.setFilterFid(fid)
        # feat = self.pipe_layer.getFeatures(request).next()
        # QgsMessageLog.logMessage(str(feat.id()) + str(feat.getGeometry().getType))
        # # pipe_features = self.pipe_layer.getFeatures()
        # # for feature in pipe_features:
            # # QgsMessageLog.logMessage (str(feature.id()))
            # # QgsMessageLog.logMessage(str(fid))
            # # if feature.id() == fid:
                # # geom = feature.geometry()
                # # QgsMessageLog.logMessage(str(geom.asLine()))