def classFactory(iface):
    from .plugin import Shp2SSAPPlugin
    return Shp2SSAPPlugin(iface)
