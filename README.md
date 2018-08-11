# QGISUtilityEdittor
Use QGIS Python extensions to build and manage a basic utility network in QGIS. This project was a part of an internship I completed during a Master of Science in Geography at KU Leuven/Vrije Universiteit Brussel. It was based on a client proposal as to whether open-source GIS solutions could be used in combination with more advanced proprietary analytical toosl in order to display networks. The PDF file Technical_Analysis_Excerpt details this project, and how the plugins function. 

Create utility network by first creating node points on map. Each node auto-generates a UUID and must be assigned a type.
Create lines, which will snap to the closest points, and use the UUID from the points as from (for the start point of the line), and to (for the end point).
Adding more points will automatically divide lines.
Use additional trace extension in order to perform a typical trace from a specified node to supply nodes.

Current Issues:
-Need to re-start the editting tool in the QGIS UI each time a new layer is selected (e.g. switching between pipes and points).
-Trace tool at present only traces to one node in a breadth-first search. Need to rework search algorithm to find all supply nodes which will lead to the target node, and additionally display which lines are used to reach it.

## Instructions
Plugins may be installed by utilizing plugin builder, an additional plugin for QGIS. 
