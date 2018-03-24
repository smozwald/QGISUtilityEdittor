# QGISUtilityEdittor
Use QGIS Python extensions to build and manage a basic utility network in QGIS

Create utility network by first creating node points on map. Each node auto-generates a UUID and must be assigned a type.
Create lines, which will snap to the closest points, and use the UUID from the points as from (for the start point of the line), and to (for the end point).
Adding more points will automatically divide lines.
Use additional trace extension in order to perform a typical trace from a specified node to supply nodes.

Current Issues:
-Need to re-start the editting tool in the QGIS UI each time a new layer is selected (e.g. switching between pipes and points).
-Trace tool at present only traces to one node in a breadth-first search. Need to rework search algorithm to find all supply nodes which will lead to the target node, and additionally display which lines are used to reach it.
