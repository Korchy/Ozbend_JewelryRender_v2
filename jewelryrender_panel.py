# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender_v2

import bpy


class JewelryRenderPanel(bpy.types.Panel):
    bl_idname = 'jewelryrender2.panel'
    bl_label = 'JewelryRender2'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        self.layout.operator('jewelryrender2.start', icon='RENDER_REGION', text='Serial Material Render')


def register():
    bpy.utils.register_class(JewelryRenderPanel)


def unregister():
    bpy.utils.unregister_class(JewelryRenderPanel)
