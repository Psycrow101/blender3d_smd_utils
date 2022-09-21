import bpy
import bmesh
import math
from bpy.types import Operator

bl_info = {
    "name": "Normalize UV",
    "author": "Psycrow",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "UV/Image Editor > UVs",
    "description": "Normalize UV for selected faces",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "UV"
}

class NormalizeUV(Operator):
    bl_idname = "uv.normalize_uv"
    bl_label = "Normalize UV"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.edit_object and context.edit_object.type == 'MESH')

    def execute(self, context):
        obj = context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.active

        for face in bm.faces:
            if not face.select:
                continue

            av_x, av_y = 0, 0
            for loop in face.loops:
                uv = loop[uv_layer].uv
                av_x += uv.x
                av_y += uv.y

            av_x = -math.floor(av_x / len(face.loops))
            av_y = -math.floor(av_y / len(face.loops))

            for loop in face.loops:
                uv = loop[uv_layer].uv
                uv.x += av_x
                uv.y += av_y

        bmesh.update_edit_mesh(me, True)

        return {'FINISHED'}

def menu_func_normilize(self, context):
    self.layout.operator(NormalizeUV.bl_idname,
        text=NormalizeUV.bl_label)


classes = (
    NormalizeUV,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.IMAGE_MT_uvs.append(menu_func_normilize)


def unregister():
    bpy.types.IMAGE_MT_uvs.remove(menu_func_normilize)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
