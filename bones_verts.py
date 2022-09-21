import bpy
from bpy.types import Operator
from mathutils import Matrix

bl_info = {
    "name": "Verts Bones",
    "author": "Psycrow",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "Viewport Object Menu -> Animation -> Verts Bones",
    "description": "Creates bones for each mesh vertex",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Object"
}


class OBJECT_OT_VertsBones(Operator):
    bl_idname = 'object.verts_bones'
    bl_label = bl_info['name']
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')

    def execute(self, context):
        view_layer = context.view_layer
        collection = view_layer.active_layer_collection.collection

        ob = context.object
        bpy.ops.object.mode_set(mode='EDIT')
        verts_co = [v.co.copy() for v in ob.data.vertices]

        bpy.ops.object.mode_set(mode='OBJECT')
        arm = bpy.data.armatures.new('verts_arm')
        arm_obj = bpy.data.objects.new('verts_arm', arm)
        arm_obj.matrix_local = ob.matrix_local.copy()
        arm_obj.show_in_front = True

        ob.matrix_local = Matrix.Identity(4)
        ob.parent = arm_obj

        collection.objects.link(arm_obj)
        view_layer.objects.active = arm_obj
        arm_obj.select_set(True)

        modifier = ob.modifiers.new(type='ARMATURE', name='Armature')
        modifier.object = arm_obj

        bpy.ops.object.mode_set(mode='EDIT')
        for i, co in enumerate(verts_co):
            b = arm.edit_bones.new(f'v{i}')
            b.head = co
            b.tail = (co.x, co.y, co.z + 0.1)

        bpy.ops.object.mode_set(mode='OBJECT')
        for i in range(len(verts_co)):
            vg = ob.vertex_groups.new(name=f'v{i}')
            vg.add([i], 1.0, 'REPLACE')

        return {'FINISHED'}

def menu_func_verts_bones(self, context):
  self.layout.operator(OBJECT_OT_VertsBones.bl_idname,
      text=OBJECT_OT_VertsBones.bl_label)


classes = (
    OBJECT_OT_VertsBones,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_animation.append(menu_func_verts_bones)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object_animation.remove(menu_func_verts_bones)


if __name__ == "__main__":
    register()
