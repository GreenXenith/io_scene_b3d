# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Blitz 3D format (.b3d)",
    "author": "Joric, GreenXenith",
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import-Export for Blitz3D scenes or objects",
    "doc_url": "https://github.com/GreenXenith/io_scene_b3d/blob/master/README.md",
    "tracker_url": "https://github.com/GreenXenith/io_scene_b3d/issues",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

if "bpy" in locals():
    import importlib
    if "import_b3d" in locals():
        importlib.reload(import_b3d)
    if "export_b3d" in locals():
        importlib.reload(export_b3d)


import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        axis_conversion,
        )



@orientation_helper(axis_forward="Y", axis_up="Z")
class ImportB3D(bpy.types.Operator, ImportHelper):
    """Import from B3D file format (.b3d)"""
    bl_idname = "import_scene.b3d"
    bl_label = "Import B3D"
    bl_options = {"UNDO"}

    filename_ext = ".b3d"
    filter_glob: StringProperty(default="*.b3d", options={"HIDDEN"})

    constrain_size: FloatProperty(
            name="Size Constraint",
            description="Scale the model by 10 until it reaches the "
                        "size constraint (0 to disable)",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=10.0,
            )
    use_image_search: BoolProperty(
            name="Image Search",
            description="Search subdirectories for any associated images "
                        "(Warning, may be slow)",
            default=True,
            )
    use_apply_transform: BoolProperty(
            name="Apply Transform",
            description="Workaround for object transformations "
                        "importing incorrectly",
            default=True,
            )

    def execute(self, context):
        from . import import_b3d

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return import_b3d.load(self, context, **keywords)

class B3D_PT_import_warning(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "B3D Import Warning"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "IMPORT_SCENE_OT_b3d"

    def draw(self, context):
        self.layout.label(text="This importer is old and experimental.", icon="ERROR")
        self.layout.label(text="Your mileage may vary.")

class ExportB3D(bpy.types.Operator, ExportHelper):
    """Export to B3D file format (.b3d)"""
    bl_idname = "export_scene.b3d"
    bl_label = "Export B3D"

    filename_ext = ".b3d"
    filter_glob: StringProperty(default="*.b3d", options={"HIDDEN"})

    use_local_transform: BoolProperty(
        name="Use Local Transform",
        description="Use local transforms with armatures",
        default=False,
    )

    export_ambient: BoolProperty(
        name="Export Ambient Light",
        description="Export world light color",
        default=False,
    )

    enable_mipmaps: BoolProperty(
        name="Enable Mipmaps",
        description="Enables the mipmap flag on UV maps",
        default=False,
    )

    forward: EnumProperty(
        items = [
            ("+x", "+X", ""),
            ("-x", "-X", ""),
            ("+y", "+Y", ""),
            ("-y", "-Y", ""),
        ],
        name="Forward",
        description="Choose which direction is forward",
    )

    use_selection: BoolProperty(
        name="Selected Objects",
        description="Export selected and visible objects only",
        default=True,
    )

    use_visible: BoolProperty(
        name="Visible Objects",
        description="Export visible objects only",
        default=False
    )

    use_collection: BoolProperty(
        name="Active Collection",
        description="Export only objects from the active collection (and its children)",
        default=False,
    )

    object_mesh: BoolProperty(
        name="Mesh",
        description="Export meshes",
        default=True,
    )

    object_armature: BoolProperty(
        name="Armature",
        description="Export armatures",
        default=True,
    )

    object_light: BoolProperty(
        name="Lamp",
        description="Export lamps",
        default=False,
    )

    object_camera: BoolProperty(
        name="Camera",
        description="Export cameras (panoramic not supported)",
        default=False,
    )

    export_texcoords: BoolProperty(
        name="UVs",
        description="Export UVs (texture coordinates) with meshes",
        default=True,
    )

    export_materials: BoolProperty(
        name="Materials",
        description="Export materials with meshes",
        default=True,
    )

    export_normals: BoolProperty(
        name="Normals",
        description="Export vertex normals with meshes",
        default=True,
    )

    export_colors: BoolProperty(
        name="Vertex Colors",
        description="Export vertex colors with meshes",
        default=False,
    )

    def draw(self, context):
        pass

    def execute(self, context):
        from . import export_b3d

        export_settings = {}

        export_settings["use_local_transform"] = self.use_local_transform
        export_settings["export_ambient"] = self.export_ambient
        export_settings["enable_mipmaps"] = self.enable_mipmaps
        export_settings["forward"] = self.forward

        export_settings["use_selection"] = self.use_selection
        export_settings["use_visible"] = self.use_visible
        export_settings["use_collection"] = self.use_collection

        export_settings["export_texcoords"] = self.export_texcoords
        export_settings["export_materials"] = self.export_materials
        export_settings["export_normals"] = self.export_normals
        export_settings["export_colors"] = self.export_colors

        export_settings["object_mesh"] = self.object_mesh
        export_settings["object_armature"] = self.object_armature
        export_settings["object_light"] = self.object_light
        export_settings["object_camera"] = self.object_camera

        return export_b3d.save(self, context, self.filepath, export_settings)

class B3D_PT_export_include(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "EXPORT_SCENE_OT_b3d"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        operator = context.space_data.active_operator

        sublayout = layout.column(heading="Limit to")
        sublayout.prop(operator, "use_selection")
        sublayout.prop(operator, "use_visible")
        sublayout.prop(operator, "use_collection")

        sublayout = layout.column(heading="Object Types")
        sublayout.prop(operator, "object_mesh")
        sublayout.prop(operator, "object_armature")
        sublayout.prop(operator, "object_light")
        sublayout.prop(operator, "object_camera")

class B3D_PT_export_mesh(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Mesh"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "EXPORT_SCENE_OT_b3d"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        operator = context.space_data.active_operator

        layout.prop(operator, "export_texcoords")
        layout.prop(operator, "export_materials")
        layout.prop(operator, "export_normals")
        layout.prop(operator, "export_colors")

class B3D_PT_export_other(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Other"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "EXPORT_SCENE_OT_b3d"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        operator = context.space_data.active_operator

        layout.prop(operator, "use_local_transform")
        layout.prop(operator, "export_ambient")
        layout.prop(operator, "enable_mipmaps")
        layout.prop(operator, "forward")

# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportB3D.bl_idname, text="Blitz3D (.b3d)")

def menu_func_import(self, context):
    self.layout.operator(ImportB3D.bl_idname, text="Blitz3D (.b3d)")

classes = (
    ImportB3D,
    B3D_PT_import_warning,
    ExportB3D,
    B3D_PT_export_include,
    B3D_PT_export_mesh,
    B3D_PT_export_other,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
