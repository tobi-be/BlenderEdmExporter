import bpy

from .edmutils import *


def edmbake(con):
    print(con.object.type)
    print(con.object.animation_data.action.name)
    if con.object.type != 'ARMATURE':
        print(con.object.name+" is not an armature")
        return
    armature = con.object
    bones = armature.data.bones
    action_old = con.object.animation_data.action
    action = action_old.copy()
    action.name = action_old.name+"_bake"
    con.object.animation_data.action = action
    scalekeyframedBones = {}
    rotationkeyframedBones = {}
    locationkeyframedBones = {}
    for fcu in action.fcurves:
        type, name, prop = parseAnimationPath(fcu)
        print(prop)
        if type == "pose.bones":
            if bones[name].layers[0] == True:  # only layer 1 is exported
                if prop == 'rotation_quaternion' or prop == 'rotation_euler':
                    rotationkeyframedBones[name] = 1
                if prop == 'scale':
                    scalekeyframedBones[name] = 1
                if prop == 'location':
                    locationkeyframedBones[name] = 1

    constrainedBones = []
    for b in armature.pose.bones:
        if len(b.constraints) > 0:
            constrainedBones.append(b)

    for b in constrainedBones:
        print(b.name)
        for c in b.constraints:
            # print("    "+c.name+" "+c.type)
            print("    "+c.type)
            if c.type == 'IK' and not c.mute:
                if c.target != None:
                    if c.target.type == 'ARMATURE':
                        if c.subtarget != None:
                            rotationkeyframedBones[b.name] = 1
                            if c.use_stretch:
                                scalekeyframedBones[b.name] = 1
                            for i in range(1, c.chain_count):
                                bp = b.parent
                                if not bp == None:
                                    rotationkeyframedBones[bp.name] = 1
                                    if c.use_stretch:
                                        scalekeyframedBones[bp.name] = 1
                                    b = bp

            if c.type == 'CLAMP_TO' and not c.mute:
                if c.target != None:
                    locationkeyframedBones[b.name] = 1
                    rotationkeyframedBones[b.name] = 1
                    scalekeyframedBones[b.name] = 1

            if c.type == 'SPLINE_IK' and not c.mute:
                if c.target != None:
                    locationkeyframedBones[b.name] = 1
                    rotationkeyframedBones[b.name] = 1
                    scalekeyframedBones[b.name] = 1
                    for i in range(1, c.chain_count):
                        bp = b.parent
                        if not bp == None:
                            locationkeyframedBones[bp.name] = 1
                            rotationkeyframedBones[bp.name] = 1
                            scalekeyframedBones[bp.name] = 1

            if c.type == 'STRETCH_TO' and not c.mute:
                if c.target != None:
                    if c.target.type == 'ARMATURE':
                        if c.subtarget != None:
                            rotationkeyframedBones[b.name] = 1
                            scalekeyframedBones[b.name] = 1
                    else:
                        rotationkeyframedBones[b.name] = 1
                        scalekeyframedBones[b.name] = 1

            if c.type == 'LIMIT_ROTATION' and not c.mute:
                rotationkeyframedBones[b.name] = 1

            if c.type == 'LIMIT_LOCATION' and not c.mute:
                locationkeyframedBones[b.name] = 1

            if (c.type == 'TRACK_TO'
                or c.type == 'LOCKED_TRACK'
                or c.type == 'DAMPED_TRACK'
                or c.type == 'TRANSFORM'
                or c.type == 'COPY_TRANSFORMS'
                    or c.type == 'COPY_ROTATION') and not c.mute:
                if c.target != None:
                    if c.target.type == 'ARMATURE':
                        if c.subtarget != None:
                            rotationkeyframedBones[b.name] = 1
                    else:
                        rotationkeyframedBones[b.name] = 1

            if (c.type == 'COPY_LOCATION'
                or c.type == 'TRANSFORM'
                or c.type == 'COPY_TRANSFORMS'
                    or c.type == 'LIMIT_DISTANCE') and not c.mute:
                if c.target != None:
                    if c.target.type == 'ARMATURE':
                        if c.subtarget != None:
                            locationkeyframedBones[b.name] = 1
                    else:
                        locationkeyframedBones[b.name] = 1

            if (c.type == 'TRANSFORM'
                or c.type == 'COPY_TRANSFORMS'
                or c.type == 'COPY_SCALE'
                    or c.type == 'LIMIT_SCALE') and not c.mute:
                if c.target != None:
                    if c.target.type == 'ARMATURE':
                        if c.subtarget != None:
                            scalekeyframedBones[b.name] = 1
                    else:
                        scalekeyframedBones[b.name] = 1

            if c.type == 'MAINTAIN_VOLUME' and not c.mute:
                scalekeyframedBones[b.name] = 1

    for i in range(action.EDMBakeStartFrame, action.EDMBakeEndFrame+1):
        bpy.context.scene.frame_set(i)
        for name in rotationkeyframedBones:
            armature.keyframe_insert(
                'pose.bones["'+name+'"].rotation_quaternion', index=-1, frame=i, group=name, options={'INSERTKEY_VISUAL'})
        for name in scalekeyframedBones:
            armature.keyframe_insert(
                'pose.bones["'+name+'"].scale', index=-1, frame=i, group=name, options={'INSERTKEY_VISUAL'})
        for name in locationkeyframedBones:
            armature.keyframe_insert(
                'pose.bones["'+name+'"].location', index=-1, frame=i, group=name, options={'INSERTKEY_VISUAL'})


class EDMBakeAction(bpy.types.Operator):
    """Bake Action"""
    bl_idname = "action.edmbakeaction"
    bl_label = "Bake Action"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        edmbake(context)

        return {'FINISHED'}
