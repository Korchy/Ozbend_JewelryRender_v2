# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender_v2

import bpy
from .jewelryrender import JewelryRender
from .jewelryrender import JewelryRenderOptions
import os

class JewelryRenderStart(bpy.types.Operator):
    bl_idname = 'jewelryrender2.start'
    bl_label = 'Start JewelryRender'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # load options
        if bpy.data.filepath:
            JewelryRenderOptions.readfromfile(os.path.dirname(bpy.data.filepath))
        else:
            print('Options file mast be in the same directory with blend-file')
            return {'CANCELLED'}
        if JewelryRenderOptions.options:
            context.screen.scene.render.resolution_x = JewelryRenderOptions.options['resolution_x']
            context.screen.scene.render.resolution_y = JewelryRenderOptions.options['resolution_y']
            context.screen.scene.cycles.samples = JewelryRenderOptions.options['samples']
            # search for *.obj
            if JewelryRenderOptions.options['source_obj_dir'] and os.path.exists(JewelryRenderOptions.options['source_obj_dir']):
                JewelryRenderOptions.objlist = [file for file in os.listdir(JewelryRenderOptions.options['source_obj_dir']) if file.endswith(".obj")]
            # serch for cameras
            if JewelryRenderOptions.options['cameras']:
                # from options.json
                JewelryRenderOptions.cameraslist = [obj for obj in context.screen.scene.objects if obj.type == 'CAMERA' and int(obj.name[-2:]) in JewelryRenderOptions.options['cameras']]
            else:
                # no selection - all cameras from scene
                JewelryRenderOptions.cameraslist = [obj for obj in context.screen.scene.objects if obj.type == 'CAMERA']
            # search for materials
            # gems
            JewelryRenderOptions.materialslist = [material for material in bpy.data.materials if material.use_fake_user]
            gems_filter = []
            # try gems_ads filter
            gems_ads_filter = ''
            if JewelryRenderOptions.options['gems_ads']:
                for gem in JewelryRenderOptions.options['gems_ads']:
                    if JewelryRenderOptions.options['gems_ads'][gem]:
                        gems_ads_filter += (',' if gems_ads_filter else '') + JewelryRenderOptions.options['gems_ads'][gem]
                        JewelryRenderOptions.materialslist_gems_ads[gem] = JewelryRenderOptions.parse_num_list(JewelryRenderOptions.options['gems_ads'][gem])
            # if gems_ads_filter:
            #     gems_filter = JewelryRenderOptions.parse_num_list(gems_ads_filter)
            # If not "gems_ads" - use "gems" filter
            if not gems_filter:
                if JewelryRenderOptions.options['gems']:
                    gems_filter = JewelryRenderOptions.parse_num_list(JewelryRenderOptions.options['gems'])
            if gems_filter:
                # from options.json
                JewelryRenderOptions.materialslist_gem = [int(material.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]) for material in JewelryRenderOptions.materialslist if
                                                          material.name[:JewelryRenderOptions.materialidtextlength] == JewelryRenderOptions.materialgemid
                                                          and int(material.name[-2:]) in gems_filter]
            else:
                # no selection - all gems from scene
                JewelryRenderOptions.materialslist_gem = [int(material.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]) for material in JewelryRenderOptions.materialslist if
                                                          material.name[:JewelryRenderOptions.materialidtextlength] == JewelryRenderOptions.materialgemid]
            # mets
            mets_filter = []
            # try mets_ads filter
            mets_ads_filter = ''
            if JewelryRenderOptions.options['mets_ads']:
                for met in JewelryRenderOptions.options['mets_ads']:
                    if JewelryRenderOptions.options['mets_ads'][met]:
                        mets_ads_filter += (',' if mets_ads_filter else '') + JewelryRenderOptions.options['mets_ads'][met]
                        JewelryRenderOptions.materialslist_mets_ads[met] = JewelryRenderOptions.parse_num_list(JewelryRenderOptions.options['mets_ads'][met])
            # if mets_ads_filter:
            #    mets_filter = JewelryRenderOptions.parse_num_list(mets_ads_filter)
            # If not "mets_ads" - use "mets" filter
            if not mets_filter:
                if JewelryRenderOptions.options['mets']:
                    mets_filter = JewelryRenderOptions.parse_num_list(JewelryRenderOptions.options['mets'])
            if mets_filter:
                # from options.json
                JewelryRenderOptions.materialslist_met = [int(material.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]) for material in JewelryRenderOptions.materialslist if
                                                          material.name[:JewelryRenderOptions.materialidtextlength] == JewelryRenderOptions.materialmetid
                                                          and int(material.name[-2:]) in mets_filter]
            else:
                # no selection - all mets from scene
                JewelryRenderOptions.materialslist_met = [int(material.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]) for material in JewelryRenderOptions.materialslist if
                                                          material.name[:JewelryRenderOptions.materialidtextlength] == JewelryRenderOptions.materialmetid]


            # print('materialslist_gem', JewelryRenderOptions.materialslist_gem)
            # print('materialslist_gems_ads', JewelryRenderOptions.materialslist_gems_ads)
            # print('materialslist_met', JewelryRenderOptions.materialslist_met)
            # print('materialslist_mets_ads', JewelryRenderOptions.materialslist_mets_ads)
            # return

            # start processing obj by list
            print('-- STARTED --')
            JewelryRender.processobjlist(context)
        return {'FINISHED'}


class JewelryRenderVars(bpy.types.PropertyGroup):
    res_to_dirs = bpy.props.BoolProperty(
        name='Result To Directories',
        description='Put results to named directories',
        default=True
    )


def register():
    bpy.utils.register_class(JewelryRenderStart)
    bpy.utils.register_class(JewelryRenderVars)
    bpy.types.Scene.jewelry_render_vars = bpy.props.PointerProperty(type=JewelryRenderVars)


def unregister():
    del bpy.types.Scene.jewelry_render_vars
    bpy.utils.unregister_class(JewelryRenderVars)
    bpy.utils.unregister_class(JewelryRenderStart)
