# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender_v2

bl_info = {
    'name': 'JewelryRender_v2',
    'category': 'Render',
    'author': 'Nikita Akimov',
    'version': (1, 1, 2),
    'blender': (2, 79, 0),
    'location': 'Properties window -> Render Panel > JewelryRender',
    'wiki_url': 'https://github.com/Korchy/Ozbend_JewelryRender_v2',
    'tracker_url': 'https://github.com/Korchy/Ozbend_JewelryRender_v2',
    'description': 'JewelryRender v2 - project manager to render jewelry'
}

from . import jewelryrender_ops
from . import jewelryrender_panel


def register():
    jewelryrender_ops.register()
    jewelryrender_panel.register()


def unregister():
    jewelryrender_panel.unregister()
    jewelryrender_ops.unregister()


if __name__ == '__main__':
    register()
