# Plugins may register an icon builder in their manifest: a callable
# that receives a 24x24 monochrome canvas. Without one, the app tile in
# the Cover Flow desktop stays empty.

def _icon(canvas):
    canvas.rect(4, 4, 6, 6)
    canvas.rect(14, 4, 6, 6)
    canvas.rect(4, 14, 6, 6)
    canvas.rect(14, 14, 6, 6)


PLUGIN = {
    "name": "Sample",
    "version": "0.2",
    "description": "Example external application",
    "icon": _icon,
}
