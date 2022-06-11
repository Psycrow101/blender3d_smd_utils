import bpy
from bpy.props import (StringProperty,
                       PointerProperty,
                       FloatProperty,
                       )

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from mathutils import Vector
import os.path

bl_info = {
    "name": "SMD Helper",
    "author": "Psycrow",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "3D Viewport",
    "description": "Support tools for working with SMD",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Tools"
}


class SmdTexturesPathProp(PropertyGroup):
    path: StringProperty(
        name="",
        description="Path to Textures Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')


class SmdKeyframesScaleProp(PropertyGroup):
    value: FloatProperty(
        name="",
        description="Keyframes scale",
        default=1.0,
        step=0.1,
        subtype='POWER')


class WM_OT_SmdLoadTextures(bpy.types.Operator):
    bl_idname = "wm.smd_load_textures"
    bl_label = "Load Textures"

    def execute(self, context):
        scene = context.scene

        selected = context.selected_objects

        for ob in selected:
            if ob.type != 'MESH':
                continue

            mesh = ob.data
            for mat in mesh.materials:
                mat.use_nodes = True
                bsdf_node = mat.node_tree.nodes.get('Principled BSDF')
                if not bsdf_node:
                    continue

                img_path = os.path.join(scene.smd_tex_path_tool.path, mat.name)

                try:
                    img = bpy.data.images.load(img_path)
                except RuntimeError as e:
                    continue

                tex_img = mat.node_tree.nodes.new('ShaderNodeTexImage')
                tex_img.image = img
                bsdf_node.inputs['Specular'].default_value = 0.0
                mat.node_tree.links.new(bsdf_node.inputs['Base Color'], tex_img.outputs['Color'])

        return {'FINISHED'}


class WM_OT_SmdKeyframesScale(bpy.types.Operator):
    bl_idname = "wm.smd_keyframes_scale"
    bl_label = "Scale"

    def execute(self, context):
        view_layer = context.view_layer
        obj = view_layer.objects.active
        action = obj.animation_data.action
        scale = obj.smd_keyframes_scale_tool.value

        for fcurve in action.fcurves:
            data = fcurve.data_path.split(".")

            if data[-1] == 'location':
                for p in fcurve.keyframe_points:
                    p.co[1] *= scale

        return {'FINISHED'}


class WM_OT_CreateProxyArmature(bpy.types.Operator):
    bl_idname = "wm.smd_create_proxy_arm"
    bl_label = "Create Proxy Armature"

    def execute(self, context):
        view_layer = context.view_layer
        arm_obj = view_layer.objects.active

        proxy_arm_obj = arm_obj.copy()
        proxy_arm_obj.data = arm_obj.data.copy()
        proxy_arm_obj.name = arm_obj.name + '_proxy'
        context.collection.objects.link(proxy_arm_obj)

        bpy.ops.object.mode_set(mode='EDIT')
        for b in proxy_arm_obj.data.edit_bones:
            b.parent = None
        bpy.ops.object.mode_set(mode='OBJECT')

        for b in arm_obj.pose.bones:
            c = b.constraints.new('COPY_TRANSFORMS')
            c.target = proxy_arm_obj
            c.subtarget = b.name

        return {'FINISHED'}


class WM_OT_LinkTargetArmature(bpy.types.Operator):
    bl_idname = "wm.smd_link_target_arm"
    bl_label = "Link Target Armature"

    def execute(self, context):
        view_layer = context.view_layer
        arm_obj = view_layer.objects.active

        for sel_obj in context.selected_objects:
            if sel_obj.type != 'ARMATURE' or sel_obj == arm_obj:
                continue

            bones_map = {}
            for b in sel_obj.data.bones:
                bones_map[b.name] = _find_closest_bone(b, arm_obj.data.bones).name

            for b in sel_obj.pose.bones:
                c = b.constraints.new('CHILD_OF')
                c.target = arm_obj
                c.subtarget = bones_map[b.name]

        return {'FINISHED'}


class OBJECT_PT_SMDHelperPanel(Panel):
    bl_idname = "OBJECT_PT_SMD_helper_panel"
    bl_label = "SMD Helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SMD"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        view_layer = context.view_layer

        col = layout.column(align=True)

        col.label(text="Textures Path")
        col.prop(scene.smd_tex_path_tool, "path", text="")
        col.operator("wm.smd_load_textures")
        col.separator()

        if view_layer.objects and view_layer.objects.active:
            obj = view_layer.objects.active
            if obj.animation_data and obj.animation_data.action:
                col.label(text="Keyframes Scale")
                row = col.row(align=True)
                row.prop(obj.smd_keyframes_scale_tool, "value", text="")
                row.operator("wm.smd_keyframes_scale")
                col.separator()

            if obj.type == 'ARMATURE':
                col.operator("wm.smd_create_proxy_arm")

                selected_arm_num = 0
                for sel_obj in context.selected_objects:
                    if sel_obj.type == 'ARMATURE' and sel_obj != obj:
                        selected_arm_num += 1
                if selected_arm_num > 0:
                    col.operator("wm.smd_link_target_arm")



classes = (
    SmdTexturesPathProp,
    SmdKeyframesScaleProp,
    WM_OT_SmdLoadTextures,
    WM_OT_SmdKeyframesScale,
    WM_OT_CreateProxyArmature,
    WM_OT_LinkTargetArmature,
    OBJECT_PT_SMDHelperPanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.smd_tex_path_tool = PointerProperty(type=SmdTexturesPathProp)
    bpy.types.Object.smd_keyframes_scale_tool = PointerProperty(type=SmdKeyframesScaleProp)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.smd_tex_path_tool
    del bpy.types.Object.smd_keyframes_scale_tool


def _find_closest_bone(bone, other_bones):
    closest_bone, closest_dist = other_bones[0], (other_bones[0].head_local - bone.head_local).length
    for b in other_bones:
        dist = (b.head_local - bone.head_local).length
        if dist < closest_dist:
            closest_bone, closest_dist = b, dist
    return closest_bone


if __name__ == "__main__":
    register()
