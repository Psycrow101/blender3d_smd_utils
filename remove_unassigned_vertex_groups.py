import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

bl_info = {
    "name": "Remove Unassigned Vertex Groups",
    "author": "Psycrow",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "Properties Editor > Object data > Vertex Groups > Specials menu",
    "description": "Remove unassigned vertex groups",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Mesh"
}


class OBJECT_OT_REMOVE_UNASSIGNED_VG(Operator):
    bl_idname = "object.select_unassigned_vg"
    bl_label = "Remove Unassigned Vertex Groups"
    bl_description = "Remove unassigned vertex groups"
    bl_options = {'REGISTER', 'UNDO'}

    remove_empty: BoolProperty(
        name="Remove Empty Groups",
        description="Remove vertex groups with no assigned vertices",
        default=True
    )

    remove_non_bone: BoolProperty(
        name="Remove Non-Bone Groups",
        description="Remove vertex groups that don't correspond to bones",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "remove_empty")
        layout.prop(self, "remove_non_bone")

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            ob.update_from_editmode()
            arm = ob.find_armature()

            bones_names = [b.name for b in arm.data.bones] if arm else []
            vg_to_remove = []

            for vg in ob.vertex_groups:
                if self.remove_non_bone and vg.name not in bones_names:
                    vg_to_remove.append(vg)
                elif self.remove_empty:
                    if not any(vg.index in [g.group for g in v.groups] for v in ob.data.vertices):
                        vg_to_remove.append(vg)

            for vg in vg_to_remove:
                ob.vertex_groups.remove(vg)

        return {'FINISHED'}


def menu_func_remove_unavg(self, context):
    if context.object.vertex_groups:
        self.layout.operator(OBJECT_OT_REMOVE_UNASSIGNED_VG.bl_idname,
            text=OBJECT_OT_REMOVE_UNASSIGNED_VG.bl_label,
            icon='X')

classes = (
    OBJECT_OT_REMOVE_UNASSIGNED_VG,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.MESH_MT_vertex_group_context_menu.append(menu_func_remove_unavg)


def unregister():
    bpy.types.MESH_MT_vertex_group_context_menu.remove(menu_func_remove_unavg)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
