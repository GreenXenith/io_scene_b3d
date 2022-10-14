#!/usr/bin/python3
# by Joric, https://github.com/joric/io_scene_b3d

import os

import bpy
from bpy_extras.image_utils import load_image

from .B3dParser import B3DDebugParser, B3DTree

ctx = None

def flip(v):
    return ((v[0],v[2],v[1]) if len(v)<4 else (v[0], v[1],v[3],v[2]))

def flip_all(v):
    return [y for y in [flip(x) for x in v]]

material_mapping = {}
weighting = {}

def import_mesh(node, parent):
    global material_mapping

    mesh = bpy.data.meshes.new(node.name)

    # join face arrays
    faces = []
    for face in node.faces:
        faces.extend(face.indices)

    # create mesh from data
    mesh.from_pydata(flip_all(node.vertices), [], flip_all(faces))

    # assign normals
    mesh.vertices.foreach_set('normal', unpack_list(node.normals))

    # create object from mesh
    ob = bpy.data.objects.new(node.name, mesh)

    # assign uv coordinates
    bpymesh = ob.data
    uvs = [(0,0) if len(uv)==0 else (uv[0], 1-uv[1]) for uv in node.uvs]
    uvlist = [i for poly in bpymesh.polygons for vidx in poly.vertices for i in uvs[vidx]]
    bpymesh.uv_layers.new().data.foreach_set('uv', uvlist)

    # adding object materials (insert-ordered)
    for _, value in material_mapping.items():
        ob.data.materials.append(bpy.data.materials[value])

    # assign material_indexes
    poly = 0
    for face in node.faces:
        for _ in face.indices:
            ob.data.polygons[poly].material_index = face.brush_id
            poly += 1

    return ob

def select_recursive(root):
    for c in root.children:
        select_recursive(c)
    root.select_set(state=True)

def make_armature_recursive(root, a, parent_bone):
    bone = a.data.edit_bones.new(root.name)
    v = root.matrix_world.to_translation()
    bone.tail = v
    # bone.head = (v[0]-0.01,v[1],v[2]) # large handles!
    bone.parent = parent_bone
    if bone.parent:
        bone.head = bone.parent.tail
    parent_bone = bone
    for c in root.children:
        make_armature_recursive(c, a, parent_bone)

def make_armatures():
    global ctx
    global imported_armatures, weighting

    for dummy_root in imported_armatures:
        objName = 'armature'
        a = bpy.data.objects.new(objName, bpy.data.armatures.new(objName))
        ctx.scene.collection.objects.link(a)
        for i in bpy.context.selected_objects: i.select_set(state=False)
        a.select_set(state=True)
        a.show_in_front = True
        a.data.display_type = 'OCTAHEDRAL'
        bpy.context.view_layer.objects.active = a

        bpy.ops.object.mode_set(mode='EDIT',toggle=False)
        make_armature_recursive(dummy_root, a, None)
        bpy.ops.object.mode_set(mode='OBJECT',toggle=False)

        # set ob to mesh object
        ob = dummy_root.parent
        a.parent = ob

        # delete dummy objects hierarchy
        for i in bpy.context.selected_objects: i.select_set(state=False)
        select_recursive(dummy_root)
        bpy.ops.object.delete(use_global=True)

        # apply armature modifier
        modifier = ob.modifiers.new(type="ARMATURE", name="armature")
        modifier.object = a

        # create vertex groups
        for bone in a.data.bones.values():
            group = ob.vertex_groups.new(name=bone.name)
            if bone.name in weighting.keys():
                for vertex_id, weight in weighting[bone.name]:
                    group_indices = [vertex_id]
                    group.add(group_indices, weight, 'REPLACE')
        a.parent.data.update()

def import_bone(node, parent=None):
    global imported_armatures, weighting
    # add dummy objects to calculate bone positions later
    ob = bpy.data.objects.new(node.name, None)

    # fill weighting map for later use
    w = []
    for vert_id, weight in node['bones']:
        w.append((vert_id, weight))
    weighting[node.name] = w

    # check parent, add root armature
    if parent and parent.type=='MESH':
        imported_armatures.append(ob)

    return ob

def import_node_recursive(node, parent=None):
    ob = None

    if 'vertices' in node and 'faces' in node:
        ob = import_mesh(node, parent)
    elif 'bones' in node:
        ob = import_bone(node, parent)
    elif node.name:
        ob = bpy.data.objects.new(node.name, None)

    if ob:
        ctx.scene.collection.objects.link(ob)

        if parent:
            ob.parent = parent

        ob.rotation_mode='QUATERNION'
        ob.rotation_quaternion = flip(node.rotation)
        ob.scale = flip(node.scale)
        ob.location = flip(node.position)

    for x in node.nodes:
        import_node_recursive(x, ob)

def load_b3d(filepath,
             context,
             IMPORT_CONSTRAIN_BOUNDS=10.0,
             IMAGE_SEARCH=True,
             APPLY_MATRIX=True,
             global_matrix=None):

    global ctx
    global material_mapping

    ctx = context
    data = B3DTree().parse(filepath)

    # load images
    images = {}
    dirname = os.path.dirname(filepath)
    for i, texture in enumerate(data['textures'] if 'textures' in data else []):
        texture_name = os.path.basename(texture['name'])
        for mat in data.materials:
            if mat.tids[0]==i:
                images[i] = (texture_name, load_image(texture_name, dirname, check_existing=True,
                    place_holder=False, recursive=IMAGE_SEARCH))

    # create materials
    material_mapping = {}
    for i, mat in enumerate(data.materials if 'materials' in data else []):
        material = bpy.data.materials.new(mat.name)
        material_mapping[i] = material.name
        material.diffuse_color = mat.rgba
        material.blend_method = 'MULTIPLY' if mat.rgba[3] < 1.0 else 'OPAQUE'

        tid = mat.tids[0] if len(mat.tids) else -1

        if tid in images:
            name, image = images[tid]
            texture = bpy.data.textures.new(name=name, type='IMAGE')
            material.use_nodes = True
            bsdf = material.node_tree.nodes["Principled BSDF"]
            texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
            texImage.image = image
            material.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

    global imported_armatures, weighting
    imported_armatures = []
    weighting = {}

    import_node_recursive(data)
    make_armatures()

def load(operator,
         context,
         filepath="",
         constrain_size=0.0,
         use_image_search=True,
         use_apply_transform=True,
         global_matrix=None,
         ):

    load_b3d(filepath,
             context,
             IMPORT_CONSTRAIN_BOUNDS=constrain_size,
             IMAGE_SEARCH=use_image_search,
             APPLY_MATRIX=use_apply_transform,
             global_matrix=global_matrix,
             )

    return {'FINISHED'}

#filepath = 'D:/Projects/github/io_scene_b3d/testing/gooey.b3d'
filepath = 'C:/Games/GnomE/media/models/ded/ded.b3d'
#filepath = 'C:/Games/GnomE/media/models/gnome/model.b3d'
#filepath = 'C:/Games/GnomE/media/levels/level1.b3d'
#filepath = 'C:/Games/GnomE/media/models/gnome/go.b3d'
#filepath = 'C:/Games/GnomE/media/models/flag/flag.b3d'

if __name__ == "__main__":
    p = B3DDebugParser()
    p.parse(filepath)

