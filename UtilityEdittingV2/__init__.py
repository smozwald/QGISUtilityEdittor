# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UtilityEdittingV2
                                 A QGIS plugin
 Edit Utility Networks
                             -------------------
        begin                : 2018-01-19
        copyright            : (C) 2018 by sam O
        email                : xx
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load UtilityEdittingV2 class from file UtilityEdittingV2.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .utility_editting import UtilityEdittingV2
    return UtilityEdittingV2(iface)
