import bpy
from bpy.types import Operator

bl_info = {
    "name": "Strong Vertex Group Assign",
    "author": "Psycrow",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties Editor > Object data > Vertex Groups > Specials menu",
    "description": "Assign selected vertexes and ramove from all other groups",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Mesh"
}

class OBJECT_OT_STRONG_ASSIGN(Operator):
    bl_idname = "object.strong_assign"
    bl_label = "Strong Assign"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def execute(self, context):
        ob = context.object
        ob.update_from_editmode()

        activeGroup = ob.vertex_groups.active
        selectedVertsIndexes = [v.index for v in ob.data.vertices if v.select]

        bpy.ops.object.mode_set(mode = 'OBJECT')
        for g in ob.vertex_groups:
            g.remove(selectedVertsIndexes)
        activeGroup.add(selectedVertsIndexes, 1.0, 'REPLACE')
        bpy.ops.object.mode_set(mode = 'EDIT')

        return {'FINISHED'}

def menu_func_strong_assign(self, context):
    ob = context.object
    if ob.vertex_groups and ob.mode == 'EDIT':
        self.layout.operator(OBJECT_OT_STRONG_ASSIGN.bl_idname,
            text=OBJECT_OT_STRONG_ASSIGN.bl_label)


classes = (
    OBJECT_OT_STRONG_ASSIGN,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.DATA_PT_vertex_groups.append(menu_func_strong_assign)


def unregister():
    bpy.types.DATA_PT_vertex_groups.remove(menu_func_strong_assign)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
