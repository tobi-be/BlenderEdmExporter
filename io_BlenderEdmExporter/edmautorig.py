import bpy
from mathutils import Vector, Matrix

    
class EDMAutoRigObject(bpy.types.Operator):
    """Auto rig"""
    bl_idname = "object.edmautorigobject"
    bl_label = "Auto Rig Object"
    bl_options = {'REGISTER', 'UNDO'}
   

    def execute(self, context):

        objects = context.view_layer.objects
        obj = context.object
        if obj.type!='MESH' and obj.type!= 'EMPTY':
            print(obj.name+" is an armature")
            return

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.parent_clear(type ='CLEAR_KEEP_TRANSFORM')
        
        armatures =[]
        m=obj.matrix_world
        scaling= obj.scale
        
        l=1.5*obj.dimensions[2]
        if l < 0.02:
            l=0.02
        
        sx = Matrix.Scale(1.0/scaling[0], 4, (1.0, 0.0, 0.0))
        sy = Matrix.Scale(1.0/scaling[1], 4, (0.0, 1.0, 0.0))
        sz = Matrix.Scale(1.0/scaling[2], 4, (0.0, 0.0, 1.0))
        scaling = sx@sy@sz
        
        name = obj.name
        for i in bpy.data.objects:
            if i.type=='ARMATURE':
                if i.data.EDMArmatureExport:
                    armatures.append(i)
        if len(armatures) >1:
            exportErrorStr = "Use only one armature! Don't know where to parent"
            print(exportErrorStr)
            return None
        if len(armatures) == 0:
            exportErrorStr = "No armature found! Can't parent"
            print(exportErrorStr)
            return None
        armature = armatures[0]
        
        bones=armature.data.bones
        for bone in bones:
            if bone.parent==None and bone.layers[0]==True:
                rootBone=bone
                break
        objects.active = armature    
        bpy.ops.object.editmode_toggle()

        if not name in bones:
            bone = armature.data.edit_bones.new(name)
            bone.use_deform = False
            bone.use_relative_parent = True
            bone.parent = armature.data.edit_bones[rootBone.name]
        else:
            bone = armature.data.edit_bones[name]
            
        bone.head = (0, 0, 0)
        bone.tail = (0, 0, l) 
        bone.transform(scaling)
        bone.transform(m)
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.select_set(True)
        obj.parent=armature
        obj.parent_type = "BONE"
        obj.parent_bone=name
        bpy.context.view_layer.objects.active = obj

        return {'FINISHED'}
