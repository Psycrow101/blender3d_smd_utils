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
    bl_description = "Select unassigned vertices to vertex groups"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            ob.update_from_editmode()

            unassigned_verts = [not any(g.weight > 0.0 for g in v.groups) for v in ob.data.vertices]

            bm = bmesh.from_edit_mesh(ob.data)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            for i, select in enumerate(unassigned_verts):
                if select:
                    bm.verts[i].select = True

            for edge in bm.edges:
                if all(v.select for v in edge.verts):
                    edge.select = True

            for face in bm.faces:
                if all(v.select for v in face.verts):
                    face.select = True

            bmesh.update_edit_mesh(ob.data)

        context.area.tag_redraw()

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
