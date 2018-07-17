# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender_v2


import json
import os
import bpy
import math
import itertools
import re
import copy


class JewelryRender:

    objname = ''        # Name of current imported obj file
    obj = []            # list of current obj meshes
    obj_m_00 = []       # list of current obj meshes with dynamic metals (00)
    obj_g_00 = []       # list of current obj meshes with dynamic gems (00)
    obj_m_0x = []       # list of current obj meshes with mets (01 ... 99) dynamic
    obj_g_0x = []       # list of current obj meshes with gems (01 ... 99) dynamic
    obj_m_0x_s = []     # list of current obj meshes with mets (01 ... 99) stable
    obj_g_0x_s = []     # list of current obj meshes with gems (01 ... 99) stable
    gravi = []          # gravi meshes list
    mode = 'NOGRAVI'    # NOGRAVI, GRAVI
    variants = []       # render variants for current obj

    @staticmethod
    def processobjlist(context):
        # process next obj in list
        __class__.clear()
        if JewelryRenderOptions.objlist:
            __class__.objname = JewelryRenderOptions.objlist.pop()
            __class__.importobj(context, __class__.objname)
            if __class__.obj:
                __class__.transformobj(context)
                __class__.setstablematerialstoobj(context)
                __class__.makerendervariants()
                __class__.render(context)
            else:
                print('Error - no meshes in obj ')
                __class__.processobjlist(context)  # process next obj
        else:
            __class__.clear()
            print('-- FINISHED --')

    @staticmethod
    def importobj(context, filename):
        # import current obj
        bpy.ops.object.select_all(action='DESELECT')
        rez = bpy.ops.import_scene.obj(filepath=JewelryRenderOptions.options['source_obj_dir'] + os.sep + filename, use_smooth_groups=False, use_split_groups=True)
        if rez == {'FINISHED'}:
            __class__.obj = context.selected_objects
            __class__.gravi = __class__.getgravimesh()
            for mesh in __class__.obj:
                if mesh.name[:JewelryRenderOptions.materialidtextlength] == JewelryRenderOptions.materialmetid:     # met
                    if int(mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]) == 0:
                        __class__.obj_m_00.append(mesh)     # met00
                    else:
                        if mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength] in JewelryRenderOptions.materialslist_mets_ads\
                                and JewelryRenderOptions.materialslist_mets_ads[mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]]:
                            __class__.obj_m_0x.append(mesh)     # met0x dynamic
                        else:
                            __class__.obj_m_0x_s.append(mesh)   # met0x stable
                elif mesh.name[:JewelryRenderOptions.materialidtextlength] == JewelryRenderOptions.materialgemid:   # gem
                    if int(mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]) == 0:
                        __class__.obj_g_00.append(mesh)     # gem00
                    else:
                        if mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength] in JewelryRenderOptions.materialslist_gems_ads\
                                and JewelryRenderOptions.materialslist_gems_ads[mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]]:
                            __class__.obj_g_0x.append(mesh)     # gem0x dynamic
                        else:
                            __class__.obj_g_0x_s.append(mesh)   # gem0x stable
        else:
            print('Error importing ', filename)
            __class__.processobjlist(context)   # process next obj

    @staticmethod
    def setstablematerialstoobj(context):
        # set stable materials to meshes
        for mesh in __class__.obj_m_0x_s:
            if mesh.name[:JewelryRenderOptions.materialidlength] in bpy.data.materials:
                __class__.setmaterialtomesh(mesh, bpy.data.materials[mesh.name[:JewelryRenderOptions.materialidlength]])
        for mesh in __class__.obj_g_0x_s:
            if mesh.name[:JewelryRenderOptions.materialidlength] in bpy.data.materials:
                __class__.setmaterialtomesh(mesh, bpy.data.materials[mesh.name[:JewelryRenderOptions.materialidlength]])

    @staticmethod
    def transformobj(context):
        # scale
        bpy.ops.transform.resize(value=(JewelryRenderOptions.options['correction']['scale']['X'],
                                        JewelryRenderOptions.options['correction']['scale']['Y'],
                                        JewelryRenderOptions.options['correction']['scale']['Z']),
                                 constraint_orientation='LOCAL')
        # translate
        bpy.ops.transform.translate(value=(JewelryRenderOptions.options['correction']['translate']['X'],
                                           JewelryRenderOptions.options['correction']['translate']['Y'],
                                           JewelryRenderOptions.options['correction']['translate']['Z']),
                                    constraint_orientation='LOCAL')
        # rotate
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['X']*math.pi/180,
                                 axis=(1, 0, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['Y']*math.pi/180,
                                 axis=(0, 1, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['Z']*math.pi/180,
                                 axis=(0, 0, 1),
                                 constraint_orientation='LOCAL')
    @staticmethod
    def makerendervariants():
        # create a list with all variants for current obj to render
        # format: [[camera1, [[mesh1, current_mat], [mesh2, current_mat]...], 'GRAVI'], [camera1, [...], 'NOGRAVI'], [camera2,...]...]
        for camera in JewelryRenderOptions.cameraslist:
            # one metal material to all metal meshes
            for metmaterial in JewelryRenderOptions.materialslist_met:
                # met00
                objmetlist = []  # list: [mesh, material]
                for metmesh in __class__.obj_m_00:
                    objmetlist.append([metmesh, metmaterial])
                # every dynamic material list (gem0x, gem00, met0x)
                variants_mesh_list = []
                variants_mats_list = []
                # gem0x
                for mesh in __class__.obj_g_0x:
                    variants_mesh_list.append(mesh)
                    variants_mats_list.append(JewelryRenderOptions.materialslist_gems_ads[mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]])
                # met0x
                for mesh in __class__.obj_m_0x:
                    variants_mesh_list.append(mesh)
                    variants_mats_list.append(JewelryRenderOptions.materialslist_mets_ads[mesh.name[JewelryRenderOptions.materialidtextlength:JewelryRenderOptions.materialidlength]])
                # gem00
                for mesh in __class__.obj_g_00:
                    variants_mesh_list.append(mesh)
                    variants_mats_list.append(JewelryRenderOptions.materialslist_gem)
                # get all variants
                variants = list(itertools.product(*variants_mats_list))
                # get summary list
                for variant in variants:
                    objalllist = []
                    for i, mat in enumerate(variant):
                        objalllist.append([variants_mesh_list[i], mat])
                    objalllist.extend(objmetlist[:])
                    # mat id's to scene materials
                    objalllist_with_mats = []
                    for mesh_mat in objalllist:
                        objalllist_with_mats.append([mesh_mat[0], bpy.data.materials[mesh_mat[0].name[:JewelryRenderOptions.materialidtextlength] + str(mesh_mat[1]).zfill(2)]])
                    # add new variant to list
                    newvariant_ng = [camera, objalllist_with_mats, 'NOGRAVI']
                    newvariant_g = [camera, objalllist_with_mats, 'GRAVI']
                    if newvariant_ng not in __class__.variants:
                        __class__.variants.append(newvariant_ng.copy())
                    if __class__.gravi and newvariant_g not in __class__.variants:
                        __class__.variants.append(newvariant_g.copy())
        # print('-'*50)
        # for i in __class__.variants:
        #     print(i[0])
        #     for j in i[1]:
        #         print('    ', j[0].name, ' => ', j[1].name)
        #     print(i[2])
        # print('-'*50)

    @staticmethod
    def setscenevariant(context, variant):
        # set scene by current variant from __class__.variants
        # select camera
        context.scene.camera = variant[0]
        # materials to meshes
        for meshmat in variant[1]:
            __class__.setmaterialtomesh(meshmat[0], meshmat[1])
        # use Gravi or not
        if variant[2] == 'GRAVI':
            __class__.gravion()
            __class__.mode = 'GRAVI'
        else:   # 'NOGRAVI'
            __class__.gravioff()
            __class__.mode = 'NOGRAVI'

    @staticmethod
    def getgravimesh():
        return [gravi for gravi in bpy.data.objects if JewelryRenderOptions.options['gravi_mesh_name'] in gravi.name]

    @staticmethod
    def gravion():
        # on gravi
        if __class__.gravi:
            for gravi in __class__.gravi:
                gravinum = __class__.graviindex(gravi)  # 01 ...
                gravimatname = gravi.data.materials[0].name[:JewelryRenderOptions.materialidlength] + 'GRAVI' + gravinum
                # if not exists - make copy from gravi mesh and on gravi
                if gravimatname not in bpy.data.materials.keys():
                    # create copy from current (gravi off)
                    gravimat = gravi.data.materials[0].copy()
                    gravimat.name = gravimatname
                    gravimat.use_fake_user = False
                    # create link
                    input = gravimat.node_tree.nodes['Gravi_Mix'].inputs['Fac']
                    output = gravimat.node_tree.nodes['Gravi_Text'].outputs['Alpha']
                    gravimat.node_tree.links.new(output, input)
                # load texture mask
                texturename = os.path.splitext(__class__.objname)[0] + gravinum + '.png'
                if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], texturename)):
                    bpy.data.images.load(os.path.join(JewelryRenderOptions.options['source_obj_dir'], texturename), check_existing=True)
                    # set texture mask to gravi-mesh node tree and create links
                    bpy.data.materials[gravimatname].node_tree.nodes['Gravi_Text'].image = bpy.data.images[texturename]
                else:
                    print('Error - no texture file with gravi')
                # set mat with on gravi to gravi mesh
                gravi.data.materials[0] = bpy.data.materials[gravimatname]
        else:
            print('Error - no gravi mesh found ', bpy.data.objects.keys())

    @staticmethod
    def gravioff():
        # off gravi
        for gravi in __class__.gravi:
            material = [mat for mat in bpy.data.materials if gravi.data.materials[0].name[:JewelryRenderOptions.materialidlength] in mat.name and mat.use_fake_user]
            if material:
                __class__.setmaterialtomesh(gravi, material[0])

    @staticmethod
    def setmaterialtomesh(mesh, material):
        if mesh and material:
            if mesh.data.materials:
                mesh.data.materials[0] = material
            else:
                mesh.data.materials.append(material)

    @staticmethod
    def selectobj():
        if __class__.obj:
            for ob in __class__.obj:
                ob.select = True

    @staticmethod
    def graviindex(gravi):
        # 01 from Met01Gravi01
        return gravi.name[:12][10:]

    @staticmethod
    def moveobjtorendered(context, objname):
        # move processed obj-file to archive directory
        path = JewelryRenderOptions.options['rendered_obj_dir']
        if context.scene.jewelry_render_vars.res_to_dirs:
            path = JewelryRenderOptions.options['dest_dir']
        if os.path.exists(path):
            clearname = os.path.splitext(objname)[0]
            if context.scene.jewelry_render_vars.res_to_dirs:
                path = os.path.join(path, clearname)    # dir/obj_name/
                if not os.path.exists(path):
                    os.makedirs(path)
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.obj')):
                if os.path.exists(os.path.join(path, clearname + '.obj')):
                    os.remove(os.path.join(path, clearname + '.obj'))
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.obj'), os.path.join(path, clearname + '.obj'))
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.mtl')):
                if os.path.exists(os.path.join(path, clearname + '.mtl')):
                    os.remove(os.path.join(path, clearname + '.mtl'))
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.mtl'), os.path.join(path, clearname + '.mtl'))
            for gravi in __class__.gravi:
                if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + __class__.graviindex(gravi) + '.png')):
                    if os.path.exists(os.path.join(path, clearname + __class__.graviindex(gravi) + '.png')):
                        os.remove(os.path.join(path, clearname + __class__.graviindex(gravi) + '.png'))
                    os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + __class__.graviindex(gravi) + '.png'), os.path.join(path, clearname + __class__.graviindex(gravi) + '.png'))
        else:
            print('Error - rendered obj directory not exists')

    @staticmethod
    def removeobj():
        # remove obj meshes from scene
        if __class__.obj:
            for ob in __class__.obj:
                # ob.name = ob.name + '_rem'  # to prevent error while removing and then importing meshes with the same name
                bpy.data.objects.remove(ob, True)

    @staticmethod
    def render(context):
        # statrt render by variants
        if __class__.variants:
            currentvariant = __class__.variants.pop()
            # set scene to current variant
            __class__.setscenevariant(context, currentvariant)
            # statr render from events
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)
        else:
            # done - move obj files to rendered
            if __class__.objname:
                __class__.moveobjtorendered(context, __class__.objname)
            # and process next obj
            __class__.processobjlist(context)

    @staticmethod
    def clear():
        __class__.objname = ''
        if __class__.obj:
            __class__.removeobj()
        __class__.obj = []
        __class__.obj_m_00 = []
        __class__.obj_g_00 = []
        __class__.obj_m_0x = []
        __class__.obj_g_0x = []
        __class__.obj_m_0x_s = []
        __class__.obj_g_0x_s = []
        __class__.gravi = []
        __class__.mode = 'NOGRAVI'
        __class__.variants = []
        if __class__.onrenderfinished in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(__class__.onrenderfinished)
        if __class__.onrendercancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(__class__.onrendercancel)
        if __class__.onsceneupdate in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate)
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)

    @staticmethod
    def onsceneupdate(scene):
        # start next render
        if __class__.onsceneupdate in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate)
        status = bpy.ops.render.render('INVOKE_DEFAULT')
        if status == {'CANCELLED'}:
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)

    @staticmethod
    def onsceneupdate_saverender(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)
        __class__.saverenderrezult(scene.camera)
        # and start next render
        __class__.render(bpy.context)

    @staticmethod
    def onrenderfinished(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender not in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate_saverender)

    @staticmethod
    def onrendercancel(scene):
        __class__.clear()
        print('-- ABORTED BY USER --')

    @staticmethod
    def saverenderrezult(camera):
        path = JewelryRenderOptions.options['dest_dir']  # dir
        if os.path.exists(path):
            if bpy.context.scene.jewelry_render_vars.res_to_dirs:
                path = os.path.join(path, os.path.splitext(__class__.objname)[0])   # dir/obj_name/
                if not os.path.exists(path):
                    os.makedirs(path)
            path = os.path.join(path, os.path.splitext(__class__.objname)[0])   # dir/ + filename
            # + mat from mesh (not gravi)
            for mesh in sorted(__class__.obj, reverse=True, key=lambda x: x.name):
                if JewelryRenderOptions.options['gravi_mesh_name'] not in mesh.name:
                    if mesh in __class__.obj_m_00 or mesh in __class__.obj_m_0x or mesh in __class__.obj_g_00 or mesh in __class__.obj_g_0x:    # only for meshes with dynamic materials
                        if mesh.data.materials:
                            path += '_' + mesh.data.materials[0].name[:JewelryRenderOptions.materialidlength]   # + mat from mesh material
                        else:
                            path += '_' + mesh.name[:JewelryRenderOptions.materialidlength]  # + mat from mesh name (no material assigned to mesh)
            # + mat from gravi (if no other meshes)
            if __class__.gravi:
                if __class__.gravi[0].data.materials[0].name[:JewelryRenderOptions.materialidlength] not in path:
                    path += __class__.gravi[0].data.materials[0].name[:JewelryRenderOptions.materialidlength]
            # + camera
            path += '_' + camera.name     # + camera
            if __class__.mode == 'NOGRAVI':
                path += '_noeng'
            path += '.png'
            for currentarea in bpy.context.window_manager.windows[0].screen.areas:
                if currentarea.type == 'IMAGE_EDITOR':
                    overridearea = bpy.context.copy()
                    overridearea['area'] = currentarea
                    bpy.ops.image.save_as(overridearea, copy=True, filepath=path)
                    break
        else:
            print('Error - no destination directory')


class JewelryRenderOptions:

    options = None
    objlist = []    # list of filenames
    cameraslist = []
    materialslist = []              # all meterials in scene
    materialslist_met = []          # all mets maretials id used in obj (after filtration by options)   [1, 2]
    materialslist_gem = []          # all gems maretials id used in obj (after filtration by options)   [1, 2]
    materialslist_mets_ads = {}     # dict with mets_ads filter (from options)  {'01': [1, 2], "02": [1]}
    materialslist_gems_ads = {}     # dict with gems_ads filter (from options)  {'01': [1, 2], "02": [1]}
    materialidlength = 5            # identifier length (ex: MET01, GEM01)
    materialidtextlength = 3        # identifier material length (ex: MET, GEM)
    materialmetid = 'Met'
    materialgemid = 'Gem'

    @staticmethod
    def readfromfile(dir):
        with open(dir + os.sep + 'options.json') as currentFile:
            __class__.options = json.load(currentFile)

    @staticmethod
    def parse_num_list(num_list_string):
        # from '1, 3-5, 8' to [1, 3, 4, 5, 8]
        linearr = [s.strip() for s in re.split(r'[,;]+| ,', num_list_string) if s]
        linearrframes = [int(i) for i in linearr if '-' not in i]
        linearrdiapasones = sum([list(range(int(i.split('-')[0]), int(i.split('-')[1]) + 1)) for i in linearr if '-' in i], [])
        linearrframes.extend(linearrdiapasones)
        return list(set(linearrframes))
