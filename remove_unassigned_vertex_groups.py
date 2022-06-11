import bpy
from bpy.types import Operator

bl_info = {
    "name": "Remove Unassigned Vertex Groups",
    "author": "Psycrow",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties Editor > Object data > Vertex Groups > Specials menu",
    "description": "Remove unassigned Vertex Groups",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Mesh"
}


class OBJECT_OT_REMOVE_UNASSIGNED_VG(Operator):
    bl_idname = "object.select_unassigned_vg"
    bl_label = "Remove Unassigned Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def execute(self, context):
        ob = context.object
        ob.update_from_editmode()
        arm = ob.find_armature()

        if arm:
            bones_names = [b.name for b in arm.data.bones]
        else:
            bones_names = []

        for vg in ob.vertex_groups:
            if vg.name not in bones_names:
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
