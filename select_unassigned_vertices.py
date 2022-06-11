import bpy
import bmesh
from bpy.types import Operator

bl_info = {
    "name": "Select Unassigned Vertices",
    "author": "Psycrow",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties Editor > Object data > Vertex Groups > Specials menu",
    "description": "Select unassigned vertices",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Mesh"
}


class OBJECT_OT_SELECT_UNASSIGNED_VERTS(Operator):
    bl_idname = "object.select_unassigned_vertices"
    bl_label = "Select Unassigned Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def execute(self, context):
        ob = context.object
        ob.update_from_editmode()

        unassigned_verts = []

        for v in ob.data.vertices:
            is_assigned = False
            for g in v.groups:
                if g.weight > 0.0:
                    is_assigned = True
                    break

            unassigned_verts.append(is_assigned)

        bm = bmesh.from_edit_mesh(ob.data)
        for i, v in enumerate(bm.verts):
            if not unassigned_verts[i]:
                v.select = True

        # force update selected vertices on view_layer
        context.view_layer.objects.active = context.view_layer.objects.active

        return {'FINISHED'}


def menu_func_select_unav(self, context):
    if context.object.mode == 'EDIT':
        self.layout.operator(OBJECT_OT_SELECT_UNASSIGNED_VERTS.bl_idname,
            text=OBJECT_OT_SELECT_UNASSIGNED_VERTS.bl_label,
            icon='GROUP_VERTEX')

classes = (
    OBJECT_OT_SELECT_UNASSIGNED_VERTS,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.MESH_MT_vertex_group_context_menu.append(menu_func_select_unav)


def unregister():
    bpy.types.MESH_MT_vertex_group_context_menu.remove(menu_func_select_unav)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
