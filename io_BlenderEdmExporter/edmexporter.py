import bpy
import struct
import mathutils
import tempfile
import bmesh
from math import radians
from .edmutils import *
printnodes = False
stringLookUp = []
warningStrs = []
exportErrorStr = ""


def getStringIndex(string):
    for i in range(len(stringLookUp)):
        if stringLookUp[i] == string:
            return i
    stringLookUp.append(string)
    return len(stringLookUp)-1


def writeUChar(file, value):
    file.write(struct.pack('<B', value))


def writeUShort(file, value):
    file.write(struct.pack("<H", value))


def writeUInt(file, value):
    file.write(struct.pack("<I", value))


def writeInt(file, value):
    file.write(struct.pack("<i", value))


def writeFloat(file, value):
    file.write(struct.pack("<f", float(value)))


def writeDouble(file, value):
    file.write(struct.pack("<d", value))


def writeString(file, value):
    data = value.encode("windows-1251")
    writeUInt(file, len(data))
    file.write(data)


def writeVec2f(file, vector):
    writeFloat(file, vector[0])
    writeFloat(file, vector[1])


def writeVec3f(file, vector):
    writeFloat(file, vector[0])
    writeFloat(file, vector[1])
    writeFloat(file, vector[2])


def writeVec3d(file, vector):
    writeDouble(file, vector[0])
    writeDouble(file, vector[1])
    writeDouble(file, vector[2])


def writeVecf(file, vector):
    for i in vector:
        writeFloat(file, i)


def writeVecd(file, vector):
    for i in vector:
        writeDouble(file, vector)


def swapMatrix(matrix):
    nmatrix = mathutils.Matrix([matrix[0], matrix[2], -matrix[1], matrix[3]])
    return nmatrix


def swapLocation(vec):
    vec2 = mathutils.Vector([vec[0], vec[1], vec[2]])
    return vec2


def writeMatrixf(file, matrix):
    for i in range(4):
        for j in range(4):
            writeFloat(file, matrix[j][i])


def writeMatrixd(file, matrix):
    for i in range(4):
        for j in range(4):
            writeDouble(file, matrix[j][i])


def writeQuaternion(file, quat):
    writeDouble(file, quat[1])
    writeDouble(file, quat[2])
    writeDouble(file, quat[3])
    writeDouble(file, quat[0])


def writePropertySet(file, properties):
    writeUInt(file, len(properties))
    for p in properties:
        p.write(file)


def writeStringLookUp(file):
    N = 0
    for s in stringLookUp:
        N += len(s)+1
    writeUInt(file, N)
    for s in stringLookUp:
        dat = s.encode("windows-1251")
        file.write(dat)
        writeUChar(file, 0)


def writeNodeBase(file, node):
    writeUInt(file, getStringIndex(node.type))
    writeString(file, node.name)
    writeUInt(file, 0)
    writePropertySet(file, node.PropertySet)


def writeWarning(warning_str):
    print(warning_str)
    warningStrs.append(warning_str)


def get_animation_data(fcurves, datatype,a,b):
    data = []
    N=len(fcurves[0].keyframe_points)
    for i in range(N):
        q = datatype()
        for fcu in fcurves:
            q[fcu.array_index] = fcu.keyframe_points[i].co[1]
            # range anpassen
            frame = a+b*fcurves[0].keyframe_points[i].co[0]
        data.append({"frame":frame, "value": q})
    return data


class EDMAnimationData:
    RotationData = 0
    PositionData = 0

    def __init__(self, frame, value):
        if isinstance(value, mathutils.Quaternion):
            EDMAnimationData.RotationData += 1
        if isinstance(value, mathutils.Vector):
            EDMAnimationData.PositionData += 1
        self.frame = frame
        self.value = value

    def write(self, file):
        writeDouble(file, self.frame)
        if isinstance(self.value, mathutils.Quaternion):
            writeQuaternion(file, self.value)
        if isinstance(self.value, float):
            writeFloat(file, self.value)
        if isinstance(self.value, mathutils.Vector):
            if len(self.value) == 3:
                writeVec3d(file, self.value)
            if len(self.value) == 2:
                writeVec2f(file, self.value)


class EDMAnimationSet:
    def __init__(self, argument, data1, data2):
        self.argument = argument
        self.data1 = data1
        self.data2 = data2

    def write(self, file):
        writeUInt(file, self.argument)
        writeUInt(file, len(self.data1))
        for d in self.data1:
            d.write(file)
        if (len(self.data2) > 0):
            writeUInt(file, len(self.data2))
            for d in self.data2:
                d.write(file)


class EDMProperty:
    NPropVec2f = 0
    NPropVec3f = 0
    NPropf = 0
    NPropUint = 0

    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value
        if self.type == "model::Property<unsigned int>":
            EDMProperty.NPropUint += 1
        if self.type == "model::Property<float>":
            EDMProperty.NPropf += 1
        if self.type == "model::Property<osg::Vec2f>":
            EDMProperty.NPropVec2f += 1
        if self.type == "model::Property<osg::Vec3f>":
            EDMProperty.NPropVec3f += 1

    def write(self, file):
        # animierte Properties noch nicht implementiert
        writeUInt(file, getStringIndex(self.type))
        writeUInt(file, getStringIndex(self.name))
        if self.type == "model::Property<unsigned int>":
            writeUInt(file, self.value)
        if self.type == "model::Property<float>":
            writeFloat(file, self.value)
        if self.type == "model::Property<osg::Vec2f>":
            writeVec2f(file, self.value)
        if self.type == "model::Property<osg::Vec3f>":
            writeVec3f(file, self.value)


class EDMAnimatedProperty:
    NAnimatedFloat = 0

    def __init__(self, name, type, data):
        self.name = name
        self.type = type
        self.data = data
        if self.type == "model::AnimatedProperty<float>":
            EDMAnimatedProperty.NAnimatedFloat += 1

    def write(self, file):
        print("write Animated Bla")
        writeUInt(file, getStringIndex(self.type))
        writeUInt(file, getStringIndex(self.name))
        if self.type == "model::AnimatedProperty<float>":
            self.data.write(file)
        if self.type == "model::AnimatedProperty<osg::Vec2f>":
            self.data.write(file)


class EDMTexture:
    N = 0

    def __init__(self, index, filename):
        EDMTexture.N += 1
        self.index = index
        self.filename = filename
        self.unknown1 = -1
        self.unknown2 = [2, 2, 10, 6]
        self.matrix = mathutils.Matrix.Identity(4)

    def write(self, file):
        writeUInt(file, self.index)
        writeInt(file, self.unknown1)
        writeUInt(file, getStringIndex(self.filename))
        writeUInt(file, self.unknown2[0])
        writeUInt(file, self.unknown2[1])
        writeUInt(file, self.unknown2[2])
        writeUInt(file, self.unknown2[3])
        writeMatrixf(file, self.matrix)


class EDMFakeLightMaterial:
    def __init__(self, filename):
        self.nameIndex = 0  # setzen
        self.materialId = EDMMaterial.NPropertiesSets
        self.name = ""
        self.materialName = "fake_omni_lights2"
        self.uniforms = []
        self.animatedUniforms = []
        self.textures = []
        self.TextureCoordinateChannels = [-1 for i in range(12)]  # ints
        self.VertexFormat = [0 for i in range(26)]  # chars
        self.shadows = 1
        self.DepthBias = 0  # Uint
        self.textures.append(EDMTexture(0, filename))  # always?
        self.Blending = 0  # char
        EDMMaterial.NPropertiesSets += 1

    def write(self, file):
        writeUInt(file, 10)
        writeUInt(file, getStringIndex("BLENDING"))
        writeUChar(file, self.Blending)
        writeUInt(file, getStringIndex("DEPTH_BIAS"))
        writeUInt(file, self.DepthBias)
        writeUInt(file, getStringIndex("VERTEX_FORMAT"))
        writeUInt(file, 26)
        for i in range(26):
            writeUChar(file, self.VertexFormat[i])
        writeUInt(file, getStringIndex("TEXTURE_COORDINATES_CHANNELS"))
        writeUInt(file, 12)
        for i in range(12):
            writeInt(file, self.TextureCoordinateChannels[i])
        writeUInt(file, getStringIndex("MATERIAL_NAME"))
        writeUInt(file, getStringIndex(self.materialName))
        writeUInt(file, getStringIndex("NAME"))
        writeUInt(file, getStringIndex(self.name))
        writeUInt(file, getStringIndex("SHADOWS"))
        writeUChar(file, self.shadows)
        writeUInt(file, getStringIndex("TEXTURES"))
        writeUInt(file, len(self.textures))
        for t in self.textures:
            t.write(file)
        writeUInt(file, getStringIndex("UNIFORMS"))
        writePropertySet(file, self.uniforms)
        writeUInt(file, getStringIndex("ANIMATED_UNIFORMS"))
        writePropertySet(file, self.animatedUniforms)


class EDMMaterial:
    NPropertiesSets = 0
    MaterialActionIndex = 0

    def __init__(self, material, weights):
        self.sourcematerial = material
        self.nameIndex = 0  # setzen
        self.materialId = EDMMaterial.NPropertiesSets
        self.name = material.name
        self.uniforms = []
        self.animatedUniforms = []
        self.textures = []
        self.TextureCoordinateChannels = [-1 for i in range(13)]  # ints
        self.VertexFormat = [0 for i in range(26)]  # chars
        self.VertexFormat[0] = 4
        self.VertexFormat[4] = 2  # uvs
        self.shadows = 3  # ??
        self.DepthBias = 0  # Uint
        self.Blending = 0  # char
        self.materialName = ""
        self.VertexFormat[1] = 0
        self.VertexFormat[3] = 0
        self.VertexFormat[2] = 0
        self.VertexFormat[3] = 0

        self.animatedSelfIlluminationData = None
        self.animatedDiffuseValueData = None
        self.animatedDiffuseShiftData = None
        self.animatedNormalShiftData = None
        DiffuseShiftFcus = []
        NormalShiftFcus = []
        if material.animation_data != None:
            action = material.animation_data.action
            if action != None:
                for fcu in action.fcurves:
                    if fcu.data_path == "EDMSelfIllumination":
                        ok = True
                        # print("Selfillum gefunde")
                        if action.EDMAutoRange:
                            tMin, tMax = action.frame_range
                        else:
                            tMin = action.EDMStartFrame
                            tMax = action.EDMEndFrame
                        if tMin != tMax:
                            b = 2.0/(tMax-tMin)
                        else:
                            b = 1
                        a = -tMin*b-1.0
                        data = []
                        for points in fcu.keyframe_points:
                            frame = a+b*points.co[0]  # range anpassen
                            data.append(EDMAnimationData(frame, points.co[1]))
                        if material.EDMSelfIlluminationArgument+1 > EDMMaterial.MaterialActionIndex:
                            EDMMaterial.MaterialActionIndex = material.EDMSelfIlluminationArgument+1
                        self.animatedSelfIlluminationData = EDMAnimatedProperty(
                            "selfIlluminationValue", "model::AnimatedProperty<float>", EDMAnimationSet(material.EDMSelfIlluminationArgument, data, []))
                        
                    if fcu.data_path == "EDMDiffuseValue":
                        ok = True
                        # print("Selfillum gefunde")
                        if action.EDMAutoRange:
                            tMin, tMax = action.frame_range
                        else:
                            tMin = action.EDMStartFrame
                            tMax = action.EDMEndFrame
                        if tMin != tMax:
                            b = 2.0/(tMax-tMin)
                        else:
                            b = 1
                        a = -tMin*b-1.0
                        data = []
                        for points in fcu.keyframe_points:
                            frame = a+b*points.co[0]  # range anpassen
                            data.append(EDMAnimationData(frame, points.co[1]))
                        if material.EDMSelfIlluminationArgument+1 > EDMMaterial.MaterialActionIndex:
                            EDMMaterial.MaterialActionIndex = material.EDMDiffuseValueArgument+1
                        self.animatedDiffuseValueData = EDMAnimatedProperty(
                            "diffuseValue", "model::AnimatedProperty<float>", EDMAnimationSet(material.EDMDiffuseValueArgument, data, []))
                        
                    if fcu.data_path == "EDMDiffuseShift":
                        ok = True
                        DiffuseShiftFcus.append(fcu)

                if len(DiffuseShiftFcus) == 2:
                    if action.EDMAutoRange:
                        tMin, tMax = action.frame_range
                    else:
                        tMin = action.EDMStartFrame
                        tMax = action.EDMEndFrame
                    if tMin != tMax:
                        b = 2.0/(tMax-tMin)
                    else:
                        b = 1
                    a = -tMin*b-1.0
                    data = []
                    for i in range(len(DiffuseShiftFcus[0].keyframe_points)):
                        # range anpassen
                        frame = a+b * \
                            DiffuseShiftFcus[0].keyframe_points[i].co[0]
                        data.append(EDMAnimationData(frame, mathutils.Vector(
                            [DiffuseShiftFcus[0].keyframe_points[i].co[1], DiffuseShiftFcus[1].keyframe_points[i].co[1]])))
                    if material.EDMDiffuseShiftArgument+1 > EDMMaterial.MaterialActionIndex:
                        EDMMaterial.MaterialActionIndex = material.EDMDiffuseShiftArgument+1
                    self.animatedDiffuseShiftData = EDMAnimatedProperty(
                        "diffuseShift", "model::AnimatedProperty<osg::Vec2f>", EDMAnimationSet(material.EDMDiffuseShiftArgument, data, []))

        if weights:
            self.VertexFormat[21] = 4
        if material.EDMMaterialType == 'Glass':
            self.materialName = "glass_material"
            self.textures.append(EDMTexture(0, material.EDMDiffuseMapName))
            self.TextureCoordinateChannels[0] = 0
            self.Blending = 1  # char
            self.VertexFormat[1] = 3  # normals
            self.VertexFormat[2] = 0
            self.VertexFormat[3] = 0
            if material.EDMUseNormalMap:
                self.VertexFormat[2] = 3
                self.VertexFormat[3] = 3
                self.textures.append(EDMTexture(1, material.EDMNormalMapName))
                self.uniforms.append(EDMProperty(
                    "normalMapValue", "model::Property<float>", material.EDMNormalMapValue))
                self.TextureCoordinateChannels[1] = 0
            if material.EDMUseDamageMap:
                self.TextureCoordinateChannels[5] = 0
                self.textures.append(EDMTexture(5, material.EDMDamageMapName))
            self.uniforms = []
            self.uniforms.append(EDMProperty(
                "specPower", "model::Property<float>", material.EDMSpecularPower))
            self.uniforms.append(EDMProperty(
                "specFactor", "model::Property<float>", material.EDMSpecularFactor))
            self.uniforms.append(EDMProperty(
                "reflectionBlurring", "model::Property<float>", material.EDMReflectionBlurring))
            self.uniforms.append(EDMProperty(
                "reflectionValue", "model::Property<float>", material.EDMReflectionValue))

            self.uniforms.append(EDMProperty(
                "diffuseValue", "model::Property<float>", material.EDMDiffuseValue))
            if self.animatedDiffuseShiftData == None:
                self.uniforms.append(EDMProperty(
                    "diffuseShift", "model::Property<osg::Vec2f>", material.EDMDiffuseShift))
            else:
                self.animatedUniforms.append(self.animatedDiffuseShiftData)

        if material.EDMMaterialType == 'Solid':
            self.materialName = "def_material"
            self.textures.append(EDMTexture(0, material.EDMDiffuseMapName))
            self.TextureCoordinateChannels[0] = 0
            self.VertexFormat[1] = 3  # normals
            if material.EDMBlending == '0':
                self.Blending = 0  # char
            if material.EDMBlending == '1':
                self.Blending = 1  # char
            if material.EDMBlending == '2':
                self.Blending = 2  # char
            if material.EDMBlending == '3':
                self.Blending = 3  # char

            if material.EDMShadows == '0':
                self.SHADOWS = 0  # char
            if material.EDMShadows == '1':
                self.SHADOWS = 1  # char
            if material.EDMShadows == '2':
                self.SHADOWS = 2  # char
            if material.EDMShadows == '3':
                self.SHADOWS = 3  # char

            if material.EDMUseNormalMap:
                self.VertexFormat[2] = 3
                self.VertexFormat[3] = 3
                self.textures.append(EDMTexture(1, material.EDMNormalMapName))
                self.uniforms.append(EDMProperty(
                    "normalMapValue", "model::Property<float>", material.EDMNormalMapValue))
                self.TextureCoordinateChannels[1] = 0
            if material.EDMUseSpecularMap:
                self.textures.append(EDMTexture(
                    2, material.EDMSpecularMapName))
                self.uniforms.append(EDMProperty(
                    "specMapValue", "model::Property<float>", material.EDMSpecularMapValue))
                self.TextureCoordinateChannels[2] = 0

            self.uniforms.append(EDMProperty(
                "specPower", "model::Property<float>", material.EDMSpecularPower))
            self.uniforms.append(EDMProperty(
                "specFactor", "model::Property<float>", material.EDMSpecularFactor))
            self.uniforms.append(EDMProperty(
                "reflectionBlurring", "model::Property<float>", material.EDMReflectionBlurring))
            self.uniforms.append(EDMProperty(
                "reflectionValue", "model::Property<float>", material.EDMReflectionValue))

            self.uniforms.append(EDMProperty(
                "diffuseValue", "model::Property<float>", material.EDMDiffuseValue))
            if material.EDMUseDiffuseShift:
                if self.animatedDiffuseShiftData == None:
                    self.uniforms.append(EDMProperty(
                        "diffuseShift", "model::Property<osg::Vec2f>", material.EDMDiffuseShift))
                else:
                    self.animatedUniforms.append(self.animatedDiffuseShiftData)
            if material.EDMUseDamageMap:
                self.TextureCoordinateChannels[5] = 0
                self.textures.append(EDMTexture(5, material.EDMDamageMapName))
                if material.EDMUseDamageNormalMap:
                    self.TextureCoordinateChannels[10] = 0
                    self.textures.append(EDMTexture(
                        10, material.EDMDamageNormalMapName))
                    self.VertexFormat[24] = 3
                    self.VertexFormat[25] = 3
            if material.EDMUseSelfIllumination:
                self.TextureCoordinateChannels[8] = 0
                self.textures.append(EDMTexture(
                    8, material.EDMSelfIlluminationMapName))
                if self.animatedSelfIlluminationData == None:
                    self.uniforms.append(EDMProperty(
                        "selfIlluminationValue", "model::Property<float>", material.EDMSelfIllumination))
                else:
                    self.animatedUniforms.append(
                        self.animatedSelfIlluminationData)

        if material.EDMMaterialType == 'Mirror':
            self.materialName = "mirror_material"
            self.textures.append(EDMTexture(0, material.EDMDiffuseMapName))
            self.TextureCoordinateChannels[0] = 0
            self.VertexFormat[1] = 3  # normals
            self.shadows = 1  # ??
            self.Blending = 0  # char
            if material.EDMUseNormalMap:
                self.VertexFormat[2] = 3
                self.VertexFormat[3] = 3
                self.textures.append(EDMTexture(1, material.EDMNormalMapName))
                self.uniforms.append(EDMProperty(
                    "normalMapValue", "model::Property<float>", material.EDMNormalMapValue))
                self.TextureCoordinateChannels[1] = 0
            if material.EDMUseSpecularMap:
                self.textures.append(EDMTexture(
                    2, material.EDMSpecularMapName))
                self.uniforms.append(EDMProperty(
                    "specMapValue", "model::Property<float>", material.EDMSpecularMapValue))
                self.TextureCoordinateChannels[2] = 0

            self.uniforms.append(EDMProperty(
                "specPower", "model::Property<float>", material.EDMSpecularPower))
            self.uniforms.append(EDMProperty(
                "specFactor", "model::Property<float>", material.EDMSpecularFactor))
            self.uniforms.append(EDMProperty(
                "reflectionBlurring", "model::Property<float>", material.EDMReflectionBlurring))
            self.uniforms.append(EDMProperty(
                "reflectionValue", "model::Property<float>", material.EDMReflectionValue))
            self.uniforms.append(EDMProperty(
                "diffuseValue", "model::Property<float>", material.EDMDiffuseValue))

        if material.EDMMaterialType == 'self_illu':
            self.materialName = "self_illum_material"
            self.textures.append(EDMTexture(
                0, material.EDMDiffuseMapName))  # always?
            self.TextureCoordinateChannels[0] = 0
            self.Blending = 0  # char
            self.shadows = 3
            self.DepthBias = 0
            self.VertexFormat[1] = 3  # normals
            self.VertexFormat[4] = 2  # uvs
            if material.EDMUseNormalMap:
                self.VertexFormat[2] = 3
                self.VertexFormat[3] = 3
                self.textures.append(EDMTexture(1, material.EDMNormalMapName))
                self.uniforms.append(EDMProperty(
                    "normalMapValue", "model::Property<float>", material.EDMNormalMapValue))
                self.TextureCoordinateChannels[1] = 0
            if material.EDMUseSpecularMap:
                self.textures.append(EDMTexture(
                    2, material.EDMSpecularMapName))
                self.uniforms.append(EDMProperty(
                    "specMapValue", "model::Property<float>", material.EDMSpecularMapValue))
                self.TextureCoordinateChannels[2] = 0
            if self.animatedSelfIlluminationData == None:
                self.uniforms.append(EDMProperty(
                    "selfIlluminationValue", "model::Property<float>", material.EDMSelfIllumination))
            else:
                self.animatedUniforms.append(self.animatedSelfIlluminationData)

            if self.animatedDiffuseShiftData == None:
                self.uniforms.append(EDMProperty(
                    "diffuseShift", "model::Property<osg::Vec2f>", material.EDMDiffuseShift))
            else:
                self.animatedUniforms.append(self.animatedDiffuseShiftData)

            self.uniforms.append(EDMProperty(
                "specPower", "model::Property<float>", material.EDMSpecularPower))
            self.uniforms.append(EDMProperty(
                "specFactor", "model::Property<float>", material.EDMSpecularFactor))
            self.uniforms.append(EDMProperty(
                "reflectionValue", "model::Property<float>", material.EDMReflectionValue))
            self.uniforms.append(EDMProperty(
                "selfIlluminationColor", "model::Property<osg::Vec3f>", material.EDMIlluminationColor))
            self.uniforms.append(EDMProperty(
                "multiplyDiffuse", "model::Property<float>", material.EDMmultiplyDiffuse))
            self.uniforms.append(EDMProperty(
                "phosphor", "model::Property<float>", material.EDMPhosphor))

        if material.EDMMaterialType == 'transp_self_illu':
            self.materialName = "transparent_self_illum_material"
            self.textures.append(EDMTexture(0, material.EDMDiffuseMapName))
            self.TextureCoordinateChannels[0] = 0
            self.VertexFormat[4] = 2  # uvs
            if material.EDMSumBlend:
                self.Blending = 3
            else:
                self.Blending = 1

            if self.animatedSelfIlluminationData == None:
                self.uniforms.append(EDMProperty(
                    "selfIlluminationValue", "model::Property<float>", material.EDMSelfIllumination))
            else:
                self.animatedUniforms.append(self.animatedSelfIlluminationData)
            if material.EDMUseDiffuseShift:
                if self.animatedDiffuseShiftData == None:
                    self.uniforms.append(EDMProperty(
                        "diffuseShift", "model::Property<osg::Vec2f>", material.EDMDiffuseShift))
                else:
                    self.animatedUniforms.append(self.animatedDiffuseShiftData)

            self.uniforms.append(EDMProperty(
                "diffuseValue", "model::Property<float>", material.EDMDiffuseValue))
            # self.uniforms.append(EDMProperty("diffuseShift", "model::Property<osg::Vec2f>" ,mathutils.Vector([0.0,0.0])))
        if material.EDMMaterialType == 'additive_self_illu':
            self.materialName = "additive_self_illum_material"
            self.textures.append(EDMTexture(
                0, material.EDMDiffuseMapName))  # always?
            self.TextureCoordinateChannels[0] = 0
            self.Blending = 3  # char
            self.shadows = 0
            self.DepthBias = 0
            self.VertexFormat[1] = 3  # normals
            self.VertexFormat[4] = 2  # uvs

            if material.EDMUseNormalMap:
                self.VertexFormat[2] = 3
                self.VertexFormat[3] = 3
                self.textures.append(EDMTexture(1, material.EDMNormalMapName))
                self.uniforms.append(EDMProperty(
                    "normalMapValue", "model::Property<float>", material.EDMNormalMapValue))
                self.TextureCoordinateChannels[1] = 0
            if material.EDMUseSpecularMap:
                self.textures.append(EDMTexture(
                    2, material.EDMSpecularMapName))
                self.uniforms.append(EDMProperty(
                    "specMapValue", "model::Property<float>", material.EDMSpecularMapValue))
                self.TextureCoordinateChannels[2] = 0
            if self.animatedSelfIlluminationData == None:
                self.uniforms.append(EDMProperty(
                    "selfIlluminationValue", "model::Property<float>", material.EDMSelfIllumination))
            else:
                self.animatedUniforms.append(self.animatedSelfIlluminationData)
            if material.EDMUseDiffuseShift:
                if self.animatedDiffuseShiftData == None:
                    self.uniforms.append(EDMProperty(
                        "diffuseShift", "model::Property<osg::Vec2f>", material.EDMDiffuseShift))
                else:
                    self.animatedUniforms.append(self.animatedDiffuseShiftData)

            self.uniforms.append(EDMProperty(
                "specPower", "model::Property<float>", material.EDMSpecularPower))
            self.uniforms.append(EDMProperty(
                "specFactor", "model::Property<float>", material.EDMSpecularFactor))
            self.uniforms.append(EDMProperty(
                "reflectionValue", "model::Property<float>", material.EDMReflectionValue))
            self.uniforms.append(EDMProperty(
                "selfIlluminationColor", "model::Property<osg::Vec3f>", material.EDMIlluminationColor))
            self.uniforms.append(EDMProperty(
                "diffuseValue", "model::Property<float>", material.EDMDiffuseValue))
            self.uniforms.append(EDMProperty(
                "multiplyDiffuse", "model::Property<float>", material.EDMmultiplyDiffuse))
            self.uniforms.append(EDMProperty(
                "phosphor", "model::Property<float>", material.EDMPhosphor))
        if material.EDMMaterialType == 'bano':
            self.materialName = "bano_material"
            self.textures.append(EDMTexture(0, material.EDMDiffuseMapName))
            self.TextureCoordinateChannels[0] = 0
            self.VertexFormat[1] = 3  # normals
            self.VertexFormat[4] = 2  # uvs
            self.uniforms.append(EDMProperty(
                "selfIlluminationValue", "model::Property<float>", material.EDMSelfIllumination))
            self.Blending = 3  # char
            self.shadows = 0
            self.DepthBias = 0
            if self.animatedDiffuseValueData == None:
                self.uniforms.append(EDMProperty(
                    "diffuseValue", "model::Property<float>", material.EDMDiffuseValue))
            else:
                self.animatedUniforms.append(self.animatedDiffuseValueData)
            # self.uniforms.append(EDMProperty("diffuseShift", "model::Property<osg::Vec2f>" ,material.EDMDiffuseShift))
            self.uniforms.append(EDMProperty(
                "banoDistCoefs", "model::Property<osg::Vec3f>", material.EDMBanoDistCoefs))
        if material.EDMMaterialType == 'forest':
            self.materialName = "forest_material"
            self.textures.append(EDMTexture(0, material.EDMDiffuseMapName))
            self.TextureCoordinateChannels[0] = 0
            self.VertexFormat[4] = 2  # uvs
            self.Blending = 2  # char
            self.shadows = 0
            self.DepthBias = 0

            self.uniforms.append(EDMProperty(
                "specPower", "model::Property<float>", 0))
            self.uniforms.append(EDMProperty(
                "reflectionValue", "model::Property<float>", 0))
            self.uniforms.append(EDMProperty(
                "selfIlluminationValue", "model::Property<float>", 0))
            self.uniforms.append(EDMProperty(
                "diffuseValue", "model::Property<float>", 0.75))
            self.uniforms.append(EDMProperty(
                "specFactor", "model::Property<float>", 30))

        EDMMaterial.NPropertiesSets += 1

    def write(self, file):
        writeUInt(file, 10)
        writeUInt(file, getStringIndex("BLENDING"))
        writeUChar(file, self.Blending)
        writeUInt(file, getStringIndex("DEPTH_BIAS"))
        writeUInt(file, self.DepthBias)
        writeUInt(file, getStringIndex("VERTEX_FORMAT"))
        writeUInt(file, 26)
        for i in range(26):
            writeUChar(file, self.VertexFormat[i])
        writeUInt(file, getStringIndex("TEXTURE_COORDINATES_CHANNELS"))
        writeUInt(file, 13)
        for i in range(13):
            writeInt(file, self.TextureCoordinateChannels[i])
        writeUInt(file, getStringIndex("MATERIAL_NAME"))
        writeUInt(file, getStringIndex(self.materialName))
        writeUInt(file, getStringIndex("NAME"))
        writeUInt(file, getStringIndex(self.name))
        writeUInt(file, getStringIndex("SHADOWS"))
        writeUChar(file, self.shadows)
        writeUInt(file, getStringIndex("TEXTURES"))
        writeUInt(file, len(self.textures))
        for t in self.textures:
            t.write(file)
        writeUInt(file, getStringIndex("UNIFORMS"))
        writePropertySet(file, self.uniforms)
        writeUInt(file, getStringIndex("ANIMATED_UNIFORMS"))
        writePropertySet(file, self.animatedUniforms)


class RootNode:
    N = 0

    def __init__(self):
        RootNode.N += 1
        self.name = "Scene Root"
        self.type = "model::RootNode"
        self.BoundingMin = mathutils.Vector([0, 0, 0])  # ???
        self.BoundingMax = mathutils.Vector([0, 0.0, 0.0])  # ???
        self.UserMin = mathutils.Vector([0, 0, 0])  # ???
        self.UserMax = mathutils.Vector([0, 0.0, 0.0])  # ???
        self.u1 = mathutils.Vector([1.0e38, 1.0e38, 1.0e38])
        self.u2 = mathutils.Vector([-1.0e38, -1.0e38, -1.0e38])
        self.materials = []
        self.NAnimationArgs = 4
        self.PropertySet = []
        self.PropertySet.append(EDMProperty(
            "__VERSION__", "model::Property<unsigned int>", 3))

    def updateBoundingBox(self, obj):
        for i in range(8):
            corner = mathutils.Vector(
                [obj.bound_box[i][0], obj.bound_box[i][1], obj.bound_box[i][2]])
            box_corner = obj.matrix_world @ corner
            self.BoundingMin[0] = min(box_corner[1], self.BoundingMin[0])
            self.BoundingMax[0] = max(box_corner[1], self.BoundingMax[0])
            self.BoundingMin[1] = min(box_corner[2], self.BoundingMin[1])
            self.BoundingMax[1] = max(box_corner[2], self.BoundingMax[1])
            self.BoundingMin[2] = min(box_corner[0], self.BoundingMin[2])
            self.BoundingMax[2] = max(box_corner[0], self.BoundingMax[2])

    def write(self, file):
        writeNodeBase(file, self)
        writeVec3d(file, self.BoundingMin)
        writeVec3d(file, self.BoundingMax)
        writeVec3d(file, self.UserMin)
        writeVec3d(file, self.UserMax)
        writeVec3d(file, self.u1)
        writeVec3d(file, self.u2)
        writeUInt(file, len(self.materials))
        for m in self.materials:
            m.write(file)
        writeUInt(file, 0)
        writeUInt(file, self.NAnimationArgs)


class TransformNode:
    N = 0

    def __init__(self, obj):
        TransformNode.N += 1
        print(obj.name)
        self.name = obj.name+"transform"
        self.type = "model::TransformNode"
        if isinstance(obj, bpy.types.Bone) and obj.parent != None:
            self.matrix = obj.parent.matrix_local.inverted() @ obj.matrix_local
        else:
            self.matrix = obj.matrix_local
        self.PropertySet = []
        self.parentid = -1

    def write(self, file):
        writeNodeBase(file, self)
        writeMatrixd(file, self.matrix)


class ConnectorNode:
    N = 0

    def __init__(self, obj):
        ConnectorNode.N += 1
        self.name = obj.name
        self.type = "model::Connector"
        self.PropertySet = []
        self.parentData = -1
        self.unknown = 0

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, self.parentData)
        writeUInt(file, self.unknown)


class EDMLight:
    def __init__(self, obj):
        self.name = obj.name
        self.type = "model::LightNode"
        self.PropertySet = []
        self.LightPropertySet = []
        self.parentData = 0
        self.Color = obj.EDMLightColor
        self.Brightness = obj.EDMLightBrightness
        self.animatedBrightnessData = None
        self.Distance = obj.EDMLightDistance
        self.isSpot = 0
        self.PropertySet.append(EDMProperty(
            "__VERSION__", "model::Property<unsigned int>", 1))
        self.LightPropertySet.append(EDMProperty(
            "Color", "model::Property<osg::Vec3f>", self.Color))
        if obj.animation_data != None:
            action = obj.animation_data.action
            if action != None:
                for fcu in action.fcurves:
                    # print(fcu.data_path)
                    if fcu.data_path == "EDMLightBrightness":
                        ok = True
                        print("Brightnessanimation gefunde")
                        if action.EDMAutoRange:
                            tMin, tMax = action.frame_range
                        else:
                            tMin = action.EDMStartFrame
                            tMax = action.EDMEndFrame
                        if tMin != tMax:
                            b = 2.0/(tMax-tMin)
                        else:
                            b = 1
                        a = -tMin*b-1.0
                        data = []
                        for points in fcu.keyframe_points:
                            frame = a+b*points.co[0]  # range anpassen
                            data.append(EDMAnimationData(frame, points.co[1]))
                        if obj.EDMBrightnessArgument+1 > EDMMaterial.MaterialActionIndex:
                            EDMMaterial.MaterialActionIndex = obj.EDMBrightnessArgument+1
                        self.animatedBrightnessData = EDMAnimatedProperty(
                            "Brightness", "model::AnimatedProperty<float>", EDMAnimationSet(obj.EDMBrightnessArgument, data, []))
        if self.animatedBrightnessData == None:
            self.LightPropertySet.append(EDMProperty(
                "Brightness", "model::Property<float>", self.Brightness))
        else:
            self.LightPropertySet.append(self.animatedBrightnessData)
        if obj.EDMisSpot:
            self.isSpot = 1
            self.LightPropertySet.append(EDMProperty(
                "Phi", "model::Property<float>", obj.EDMLightPhi))
            self.LightPropertySet.append(EDMProperty(
                "Theta", "model::Property<float>", obj.EDMLightTheta))
        else:
            self.LightPropertySet.append(
                EDMProperty("", "model::Property<float>", 0))
            self.LightPropertySet.append(
                EDMProperty("", "model::Property<float>", 0))
        self.LightPropertySet.append(EDMProperty(
            "Distance", "model::Property<float>", self.Distance))
        # print(len(self.LightPropertySet))

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, self.parentData)
        writeUChar(file, self.isSpot)
        writePropertySet(file, self.LightPropertySet)
        writeUChar(file, 0)


class EDMNode:
    N = 0

    def __init__(self):
        EDMNode.N += 1
        self.name = ""
        self.type = "model::Node"
        self.PropertySet = []
        self.parentid = -1

    def write(self, file):
        writeNodeBase(file, self)


class ArgAnimationNode:
    NRotation = 0
    NPosition = 0
    N = 0

    def __init__(self, obj):
        ArgAnimationNode.N += 1
        self.name = obj.name
        self.type = "model::ArgAnimationNode"
        self.matrix = mathutils.Matrix.Identity(4)
        if isinstance(obj, bpy.types.Bone) and obj.parent != None:
            M = obj.parent.matrix_local.inverted() @ obj.matrix_local
        else:
            M = obj.matrix_local
        self.vector = M.to_translation()
        self.Q1 = M.to_quaternion()
        # self.Q1=mathutils.Quaternion([0.0,0.0,0.0,1.0])
        self.Q2 = mathutils.Quaternion([1.0, 0.0, 0.0, 0.0])
        self.scale = mathutils.Vector([1.0, 1.0, 1.0])
        self.positionAnimations = []
        self.rotationAnimations = []
        self.scaleAnimations = []
        self.PropertySet = []
        self.parentid = -1

    def write(self, file):
        writeNodeBase(file, self)
        writeMatrixd(file, self.matrix)
        writeVec3d(file, self.vector)
        writeQuaternion(file, self.Q1)
        writeQuaternion(file, self.Q2)
        writeVec3d(file, self.scale)
        writeUInt(file, len(self.positionAnimations))
        for p in self.positionAnimations:
            p.write(file)
        writeUInt(file, len(self.rotationAnimations))
        for r in self.rotationAnimations:
            r.write(file)
        # writeUInt(file,0)
        writeUInt(file, len(self.scaleAnimations))
        for r in self.scaleAnimations:
            r.write(file)


class AnimatedBoneNode:
    N = 0

    def __init__(self, obj):
        AnimatedBoneNode.N += 1
        self.name = obj.name
        self.type = "model::ArgAnimatedBone"
        self.matrix = mathutils.Matrix.Identity(4)
        if isinstance(obj, bpy.types.Bone) and obj.parent != None:
            M = obj.parent.matrix_local.inverted() @ obj.matrix_local
        else:
            M = obj.matrix_local
        self.vector = M.to_translation()
        self.Q1 = M.to_quaternion()
        self.Q2 = mathutils.Quaternion([1.0, 0.0, 0.0, 0.0])
        self.scale = mathutils.Vector([1.0, 1.0, 1.0])
        self.positionAnimations = []
        self.rotationAnimations = []
        self.scaleAnimations = []
        self.PropertySet = []
        self.parentid = -1
        self.matrix_inv = obj.matrix_local.inverted()

    def write(self, file):
        writeNodeBase(file, self)
        writeMatrixd(file, self.matrix)
        writeVec3d(file, self.vector)
        writeQuaternion(file, self.Q1)
        writeQuaternion(file, self.Q2)
        writeVec3d(file, self.scale)
        writeUInt(file, len(self.positionAnimations))
        for p in self.positionAnimations:
            p.write(file)
        writeUInt(file, len(self.rotationAnimations))
        for r in self.rotationAnimations:
            r.write(file)
        # writeUInt(file,0)
        writeUInt(file, len(self.scaleAnimations))
        for r in self.scaleAnimations:
            r.write(file)
        writeMatrixd(file, self.matrix_inv)


class VisibilityData:
    def __init__(self, argument):
        self.keys = []


class VisibilityKey:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class VisibilityNode:
    N = 0

    def __init__(self, parentid):
        VisibilityNode.N += 1
        self.name = "VisibilityNode"
        self.type = "model::ArgVisibilityNode"
        self.parentid = parentid
        self.PropertySet = []
        self.data = {}

    def addKey(self, argument, start, end):
        if not argument in self.data:
            self.data[argument] = VisibilityData(argument)
        self.data[argument].keys.append(VisibilityKey(start, end))

    def addFCurve(self, argument, fcu):
        on = False
        framestart = 0
        frameend = 0
        tMin, tMax = fcu.range()
        b = 2.0/(tMax-tMin)
        a = -tMin*b-1.0
        for i in fcu.keyframe_points:
            if i.co.y == 0:
                if not on:
                    framestart = a+b*i.co.x
                on = True
            if i.co.y == 1:
                if on:
                    frameend = a+b*i.co.x
                    self.addKey(argument, framestart, frameend)
                on = False
        if on:
            self.addKey(argument, framestart, 1000000.0)

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, len(self.data))
        for argument, v in self.data.items():
            writeUInt(file, argument)
            writeUInt(file, len(v.keys))
            for key in v.keys:
                writeDouble(file, key.start)
                writeDouble(file, key.end)


class BoneNode:
    N = 0

    def __init__(self, obj):
        BoneNode.N += 1
        self.name = obj.name
        self.type = "model::Bone"
        if isinstance(obj, bpy.types.Bone) and obj.parent != None:
            M = obj.parent.matrix_local.inverted() @ obj.matrix_local
        else:
            M = obj.matrix_local
        self.matrix = M
        self.matrix_inv = obj.matrix_local.inverted()
        self.PropertySet = []
        self.parentid = -1

    def write(self, file):
        writeNodeBase(file, self)
        writeMatrixd(file, self.matrix)
        writeMatrixd(file, self.matrix_inv)


class EDMVertex:
    def __init__(self, vert, uv, normal, tangent, bitangent):
        self.co = vert.co
        self.normal = normal
        # self.tangent=mathutils.Vector([0.0,0.0,0.0])
        self.tangent = tangent
        # self.bitangent=mathutils.Vector([0.0,0.0,0.0])
        self.bitangent = bitangent
        self.groups = [0, 0, 0, 0]  # groups angucken
        self.weights = [0.0, 0.0, 0.0, 0.0]  # auch angucken
        if len(vert.groups) > 4:
            writeWarning(
                "Too much weights per vertex! Use Weights->Limit Total in Weight Paint mode to reduce limit to 4")
        else:
            sum = 0
            count = 0
            for g in vert.groups:
                self.groups[count] = g.group
                self.weights[count] = g.weight
                sum += g.weight
                count += 1
            if sum > 0:
                for i in range(4):
                    self.weights[i] = self.weights[i]/sum
            for i in range(4):
                self.groups[i] = self.groups[i]
        self.uv = uv


def createMesh(me, simple, twoside):
    newverts = []
    tris = []
    #me.calc_normals()

    if not simple:
        # print("Length UV layer: " +str(len(me.uv_layers)))
        me.calc_tangents(uvmap=me.uv_layers[0].name)
        uv_layer = me.uv_layers.active.data
        # me.update(calc_edges=True, calc_edges_loose=True)
    vlist = []
    for v in me.vertices:
        vlist.append([])

    def addTriSimple(vertIDs):
        tri = []
        for loop_index in vertIDs:
            id = me.loops[loop_index].vertex_index  # ursprünglicher vertex
            found = False
            ivert = 0
            for i in vlist[id]:
                ivert = i
                found = True
            if found == False:
                ivert = len(newverts)
                vlist[id].append(ivert)
                newverts.append(EDMVertex(me.vertices[id], mathutils.Vector([0, 0]), mathutils.Vector(
                    [0, 0, 0]), mathutils.Vector([0, 0, 0]), mathutils.Vector([0, 0, 0])))
            tri.append(ivert)
        return tri

    def addTri(vertIDs, invert):
        tri = []
        for loop_index in vertIDs:
            id = me.loops[loop_index].vertex_index  # ursprünglicher vertex
            tangent = me.loops[loop_index].tangent
            bitangent = me.loops[loop_index].bitangent
            normal = me.loops[loop_index].normal
            if invert:
                normal = -normal
            uv = mathutils.Vector(
                [uv_layer[loop_index].uv[0], 1.0-uv_layer[loop_index].uv[1]])  # uv
            found = False
            ivert = 0
            for i in vlist[id]:
                # should look also at normals to use smoothinggroups?
                if newverts[i].uv == uv and newverts[i].normal == normal:
                    ivert = i
                    found = True
            if found == False:
                ivert = len(newverts)
                vlist[id].append(ivert)
                newverts.append(
                    EDMVertex(me.vertices[id], uv, normal, tangent, bitangent))
            tri.append(ivert)
        return tri
    for poly in me.polygons:
        loop = range(poly.loop_start, poly.loop_start + poly.loop_total)
        if simple:
            tri = addTriSimple([loop[0], loop[1], loop[2]])
            tris.append(tri)
        else:
            tri = addTri([loop[0], loop[1], loop[2]], False)
            tris.append(tri)
            if twoside:
                tri2 = addTri([loop[0], loop[2], loop[1]], True)
                tris.append(tri2)
        if len(loop) == 4:
            if simple:
                tri = addTriSimple([loop[0], loop[2], loop[3]])
                tris.append(tri)
            else:
                tri = addTri([loop[0], loop[2], loop[3]], False)
                tris.append(tri)
                if twoside:
                    tri2 = addTri([loop[0], loop[3], loop[2]], True)
                    tris.append(tri2)
    if not simple:
        me.free_tangents()
    # print(len(newverts))
    return newverts, tris


def writeMesh(file, verts, tris, normals, tangents, uvs, groups, weights, damageTangents):
    stride = 3
    if groups:
        stride += 1
    if normals:
        stride += 3
    if tangents:
        stride += 6
    if uvs:
        stride += 2
    if weights:
        stride += 4
    if damageTangents:
        stride += 6
    writeUInt(file, len(verts))
    writeUInt(file, stride)
    for v in verts:
        writeFloat(file, v.co[0])
        writeFloat(file, v.co[1])
        writeFloat(file, v.co[2])
        if groups:
            for i in range(4):  # safety rework groups
                if v.groups[i] == -1:
                    v.groups[i] = 0
            writeUChar(file, v.groups[0])
            writeUChar(file, v.groups[1])
            writeUChar(file, v.groups[2])
            writeUChar(file, v.groups[3])
        if normals:
            writeVec3f(file, v.normal)
            # writeFloat(file,v.normal[1])
            # writeFloat(file,v.normal[2])
        if tangents:
            writeVec3f(file, v.tangent)
            writeVec3f(file, v.bitangent)
        if uvs:
            writeVec2f(file, v.uv)
        if weights:
            writeFloat(file, v.weights[0])
            writeFloat(file, v.weights[1])
            writeFloat(file, v.weights[2])
            writeFloat(file, v.weights[3])
        if damageTangents:
            writeVec3f(file, v.tangent)
            writeVec3f(file, v.bitangent)
    writeUChar(file, 2)  # Alle Indizes sind UInts (0Chars, 1 Shorts)
    writeUInt(file, 3*len(tris))
    writeUInt(file, 5)
    for t in tris:
        writeUInt(file, t[0])
        writeUInt(file, t[1])
        writeUInt(file, t[2])


class FakeOmniLightNode:
    N = 0

    def __init__(self, obj):
        self.name = obj.name
        self.type = "model::FakeOmniLightsNode"
        self.PropertySet = []
        self.materialId = 0
        self.parentData = 0
        self.p1 = obj.FakeLightP1
        self.uv1 = obj.FakeLightUV1
        self.uv2 = obj.FakeLightUV2
        self.scale = obj.FakeLightScale
        self.material = EDMFakeLightMaterial(obj.FakeOmniLightTextureName)
        self.material.uniforms.append(EDMProperty(
            "sizeFactors", "model::Property<osg::Vec3f>", mathutils.Vector([3, 50000, 0])))
        self.material.uniforms.append(EDMProperty(
            "shiftToCamera", "model::Property<float>", obj.FakeLightShift))
        self.N = 1

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, 0)  # dummy
        writeUInt(file, self.material.materialId)  # materialID
        writeUInt(file, self.N)  # numer of parentings
        writeUInt(file, self.parentData)  # ParentID
        writeUInt(file, 1)  # Dataindex begins with 1 and not with 0
        writeUInt(file, 1)  # Number of datablocks
        # PositionOffset:
        writeVec3d(file, self.p1)
        # UVs
        writeVec2f(file, self.uv1)
        writeVec2f(file, self.uv2)
        writeFloat(file, self.scale)
        writeUInt(file, 0)


class RenderNode:
    giBytes = 0
    gvBytes = 0

    def __init__(self, obj):
        mesh = obj.data
        if obj.EDMAlternativeName == "":
            self.name = obj.name
        else:
            self.name = obj.EDMAlternativeName
        self.type = "model::RenderNode"
        self.PropertySet = []
        self.unknown = 0
        self.materialID = 0
        self.parentData = 0
        verts, tris = createMesh(mesh, False, obj.EDMTwoSides)
        # bpy.data.meshes.remove(mesh)
        self.verts = verts
        self.tris = tris
        self.sourcematerial = obj.material_slots[0].material
        self.parentDataDamageArg = -1
        print(obj.name)
        if self.sourcematerial.EDMUseDamageMap:
            self.parentDataDamageArg = obj.EDMDamageArgument
        self.material = EDMMaterial(self.sourcematerial, False)
        self.stride = 15  # automatisch aus Material ermitteln
        RenderNode.giBytes += 12*len(self.tris)
        RenderNode.gvBytes += 4*self.stride*len(self.tris)

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, 0)
        writeUInt(file, self.material.materialId)
        writeUInt(file, 1)  # NParentdata
        writeUInt(file, self.parentData)
        writeInt(file, self.parentDataDamageArg)
        exportNormals = self.material.VertexFormat[1] != 0
        exportTangents = self.material.VertexFormat[2] != 0
        exportDamageTangents = self.material.VertexFormat[24] != 0
        writeMesh(file, self.verts, self.tris, exportNormals,
                  exportTangents, True, True, False, exportDamageTangents)
        # writeMesh(file,verts,tris,normals,tangents,uvs,groups,weights):


class SkinNode:
    giBytes = 0
    gvBytes = 0

    def __init__(self, obj, boneid):
        # print("create SkinNode")
        selected = obj.select_get()
        obj.select_set(True)

        mesh = obj.data
        if obj.EDMAlternativeName == "":
            self.name = obj.name
        else:
            self.name = obj.EDMAlternativeName
        self.type = "model::SkinNode"
        self.PropertySet = []
        self.unknown = -1
        self.bones = []
        effgroup = self.TextureCoordinateChannels = [
            -1 for i in obj.vertex_groups]
        count = -1
        for g in obj.vertex_groups:
            if g.name in boneid:
                count = count+1
                effgroup[g.index] = count
                self.bones.append(boneid[g.name])

        if len(self.bones) > 0:
            self.bones.insert(0, self.bones[0])
        self.sourcematerial = obj.material_slots[0].material
        self.material = EDMMaterial(self.sourcematerial, True)
        self.stride = 13
        verts, tris = createMesh(mesh, False, obj.EDMTwoSides)
        self.verts = verts
        print(obj.name)
        for v in verts:
            for i in range(4):
                v.groups[i] = effgroup[v.groups[i]]
        self.tris = tris
        RenderNode.giBytes += 12*len(self.tris)
        RenderNode.gvBytes += 4*self.stride*len(self.tris)

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, 0)
        writeUInt(file, self.material.materialId)
        writeUInt(file, len(self.bones))
        for b in self.bones:
            writeUInt(file, b)
        writeInt(file, self.unknown)  # use bonemap?
        exportNormals = True
        exportNormals = self.material.VertexFormat[1] != 0
        exportTangents = self.material.VertexFormat[2] != 0
        if self.sourcematerial.EDMMaterialType == 'transp_self_illu':
            exportNormals = False
        writeMesh(file, self.verts, self.tris, exportNormals,
                  exportTangents, True, True, True, False)


class ShellNode:
    ciBytes = 0
    cvBytes = 0

    def __init__(self, obj):
        mesh = obj.data
        if obj.EDMAlternativeName == "":
            self.name = obj.name
        else:
            self.name = obj.EDMAlternativeName
        self.type = "model::ShellNode"
        self.PropertySet = []
        self.parentData = 0
        self.VertexFormat = [0 for i in range(26)]  # chars
        self.VertexFormat[0] = 3
        self.stride = 3
        verts, tris = createMesh(mesh, True, False)
        self.verts = verts
        self.tris = tris
        ShellNode.ciBytes += 12*len(self.tris)
        ShellNode.cvBytes += 4*self.stride*len(self.tris)

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, self.parentData)
        writeUInt(file, 26)
        for i in range(26):
            # print(self.VertexFormat[i])
            writeUChar(file, self.VertexFormat[i])
        writeMesh(file, self.verts, self.tris, False,
                  False, False, False, False, False)
        # writeMesh(file,verts,tris,normals,tangents,uvs,groups,weights):


class SegmentsNode:
    ciBytes = 0
    cvBytes = 0

    def __init__(self, obj):
        mesh = obj.data
        if obj.EDMAlternativeName == "":
            self.name = obj.name
        else:
            self.name = obj.EDMAlternativeName
        self.type = "model::SegmentsNode"
        self.PropertySet = []
        self.parentData = 0
        self.segments = []
        for e in mesh.edges:
            self.segments.append(
                [mesh.vertices[e.vertices[0]].co, mesh.vertices[e.vertices[1]].co])
        # print(len(self.segments))

    def write(self, file):
        writeNodeBase(file, self)
        writeUInt(file, self.parentData)
        writeUInt(file, len(self.segments))
        for i in self.segments:
            writeVec3f(file, i[0])
            writeVec3f(file, i[1])
            # print(i[0])
            # print(i[1])


class EDMModel:
    def __init__(self):
        self.nodes = []
        self.stringtable = []
        self.file = 0
        self.nodes.append(EDMNode())
        self.parents = [-1]
        self.rootNode = RootNode()
        self.indexA = {}
        self.Connectors = []
        self.RenderNodes = []
        self.SkinNodes = []
        self.ShellNodes = []
        self.SegmentsNodes = []
        self.LightNodes = []

    def writeIndexA(self, file):
        for n in self.nodes:
            if n.type in self.indexA:
                self.indexA[n.type] += 1
            else:
                self.indexA[n.type] = 1
        for n in self.RenderNodes:
            if n.type in self.indexA:
                self.indexA[n.type] += 1
            else:
                self.indexA[n.type] = 1
        self.indexA["model::RootNode"] = 1
        writeUInt(file, len(self.indexA))
        for k, v in self.indexA.items():
            writeUInt(file, getStringIndex(k))
            writeUInt(file, v)

    def writeIndexB(self, file):
        count = 0
        pos = file.tell()
        writeUInt(file, 0)
        writeUInt(file, getStringIndex("__gi_bytes"))
        writeUInt(file, SkinNode.giBytes+RenderNode.giBytes)
        writeUInt(file, getStringIndex("__gv_bytes"))
        writeUInt(file, SkinNode.gvBytes+RenderNode.gvBytes)
        count += 2
        if ShellNode.ciBytes > 0:
            writeUInt(file, getStringIndex("__ci_bytes"))
            writeUInt(file, ShellNode.ciBytes)
            count += 1
        if ShellNode.cvBytes > 0:
            writeUInt(file, getStringIndex("__cv_bytes"))
            writeUInt(file, ShellNode.cvBytes)
            count += 1
        if EDMProperty.NPropVec3f > 0:
            writeUInt(file, getStringIndex("model::Property<osg::Vec3f>"))
            writeUInt(file, EDMProperty.NPropVec3f)
            count += 1
        if EDMProperty.NPropVec2f > 0:
            writeUInt(file, getStringIndex("model::Property<osg::Vec2f>"))
            writeUInt(file, EDMProperty.NPropVec2f)
            count += 1
        if EDMProperty.NPropUint > 0:
            writeUInt(file, getStringIndex("model::Property<unsigned int>"))
            writeUInt(file, EDMProperty.NPropUint)
            count += 1
        if EDMProperty.NPropf > 0:
            writeUInt(file, getStringIndex("model::Property<float>"))
            writeUInt(file, EDMProperty.NPropf)
            count += 1
        if EDMMaterial.NPropertiesSets > 0:
            writeUInt(file, getStringIndex("model::PropertiesSet"))
            writeUInt(file, EDMMaterial.NPropertiesSets)
            count += 1
        # Counter schreiben
        pos2 = file.tell()
        file.seek(pos)
        writeUInt(file, count)
        file.seek(pos2)

    def write(self, filename):
        print("Write EDM-File")
        body = tempfile.TemporaryFile()
        self.writeIndexA(body)
        self.writeIndexB(body)
        self.rootNode.write(body)
        # Schreibe Nodes
        # print("Write Nodes")
        writeUInt(body, len(self.nodes))
        for n in self.nodes:
            n.write(body)
        for n in self.nodes:
            writeInt(body, n.parentid)
        # RenderItems:
        pos = body.tell()
        groupcount = 0
        writeUInt(body, 0)
        if len(self.Connectors) > 0:
            groupcount += 1
            writeUInt(body, getStringIndex("CONNECTORS"))
            writeUInt(body, len(self.Connectors))
            for c in self.Connectors:
                c.write(body)
        if len(self.ShellNodes)+len(self.SegmentsNodes) > 0:
            groupcount += 1
            writeUInt(body, getStringIndex("SHELL_NODES"))
            writeUInt(body, len(self.ShellNodes)+len(self.SegmentsNodes))
            for s in self.ShellNodes:
                s.write(body)
            for s in self.SegmentsNodes:
                s.write(body)

        if len(self.RenderNodes)+len(self.SkinNodes) > 0:
            # print("Write Rendernodes")
            groupcount += 1
            writeUInt(body, getStringIndex("RENDER_NODES"))
            writeUInt(body, len(self.RenderNodes)+len(self.SkinNodes))
            for r in self.RenderNodes:
                r.write(body)
            for s in self.SkinNodes:
                # print("Write Skinnode")
                s.write(body)
        if len(self.LightNodes) > 0:
            groupcount += 1
            writeUInt(body, getStringIndex("LIGHT_NODES"))
            writeUInt(body, len(self.LightNodes))
            for l in self.LightNodes:
                l.write(body)
        pos2 = body.tell()
        body.seek(pos)
        writeUInt(body, groupcount)
        body.seek(pos2)

        file = open(filename, "wb")
        # print("Write Header")
        writeUChar(file, ord('E'))
        writeUChar(file, ord('D'))
        writeUChar(file, ord('M'))
        writeUShort(file, 10)
        writeStringLookUp(file)
        # appendBody
        body.seek(0, 0)
        file.write(body.read())
        file.close()
        body.close()


def checkKeyframes(curves):
    frames = []
    N = len(curves[0].keyframe_points)
    for i in range(1, len(curves)):
        if N != len(curves[i].keyframe_points):
            writeWarning("Inconsistend Keyframes: {} Action: {}".format(
                curves[0].data_path, curves[0].id_data.name))
            return None
    for i in range(N):
        x0 = curves[0].keyframe_points[i].co[0]
        for j in range(1, len(curves)):
            if x0 != curves[j].keyframe_points[i].co[0]:
                writeWarning("Inconsistend Keyframes: {} Action: {}".format(
                    curves[0].data_path, curves[0].id_data.name))
                return None
    return N


def getOffsetTransform(a, b, shift):
    # Prüfen ob wirklich eine Transformation vorliegt
    # print(a.name)
    t = TransformNode(a)
    if shift:
        mat = a.matrix_local
        transpose = mat.col[3]
        mat = mat@(mathutils.Matrix.Rotation(-radians(90.0), 4, 'Z') @
                   mathutils.Matrix.Rotation(-radians(90.0), 4, 'Y')).inverted()
        mat.col[3] = transpose
        t.matrix = b.matrix_local.inverted() @ mat
    else:
        t.matrix = b.matrix_local.inverted() @ a.matrix_local
    # print(t.matrix)
    dx = t.matrix.to_translation()
    dl = dx[0]*dx[0]+dx[1]*dx[1]+dx[2]*dx[2]
    return t


def resetData():
    stringLookUp.clear()
    EDMAnimationData.RotationData = 0
    EDMAnimationData.PositionData = 0
    EDMProperty.NPropVec2f = 0
    EDMProperty.NPropVec3f = 0
    EDMProperty.NPropf = 0
    EDMProperty.NPropUint = 0
    EDMTexture.N = 0
    EDMMaterial.NPropertiesSets = 0
    RootNode.N = 0
    TransformNode.N = 0
    ConnectorNode.N = 0
    EDMNode.N = 0
    ArgAnimationNode.NRotation = 0
    ArgAnimationNode.NPosition = 0
    ArgAnimationNode.N = 0
    AnimatedBoneNode.N = 0
    BoneNode.N = 0
    RenderNode.giBytes = 0
    RenderNode.gvBytes = 0
    SkinNode.giBytes = 0
    SkinNode.gvBytes = 0
    ShellNode.ciBytes = 0
    ShellNode.cvBytes = 0


def getVisibilityFCurves(obj):
    fcus = []
    arguments = []
    for item in obj.visanimation:
        action = item.obj
        if action == None:
            return None, None
        if not action.exportToEDM:
            return None, None
        for fcu in action.fcurves:
            type, name, prop = parseAnimationPath(fcu)
            if type == "Visibility":
                fcus.append(fcu)
                arguments.append(action.animationArgument)

    return fcus, arguments


def hasMaterial(obj):
    if len(obj.material_slots) == 0:
        writeWarning("Object '{}' has no Material".format(obj.name))
        return False
    else:
        return True


def meshIsOk(obj, warnings):
    me = obj.data
    if len(me.uv_layers) == 0:
        if warnings:
            writeWarning(
                "'{}' Mesh has no UV-Map. Mesh is not exported".format(obj.name))
        return False
    if len(me.polygons) == 0:
        if warnings:
            writeWarning(
                "Object '{}' does not contain polygons".format(obj.name))
        return False
    for p in me.polygons:
        if len(p.vertices) != 4 and len(p.vertices) != 3:
            if warnings:
                writeWarning(
                    "'{}' is not a tri or quad. Mesh is not exported".format(obj.name))
            return False
    return True

def get_geometric_fcurves(l,propname):
    fcurves = []
    for fcu in l:
        type, name, prop = parseAnimationPath(fcu)
        if prop == propname:
            known = True
            fcurves.append(fcu)
    return fcurves

def get_rotation_fcurves(l):
    fcurves = get_geometric_fcurves(l,"rotation_quaternion")
    if len(fcurves) != 4:
        if len(fcurves) != 0:
            writeWarning(
                "Incomplete rotation keyframes. Please use all four quaternionchannels")
        fcurves = []
    return fcurves

def get_translation_fcurves(l):
    fcurves = get_geometric_fcurves(l,"location")
    if len(fcurves) != 3:
        if len(fcurves) != 0:
            writeWarning(
                "Incomplete position keyframes. Please use all three positionchannels")
        fcurves = []
    return fcurves

def get_scale_fcurves(l):
    fcurves = get_geometric_fcurves(l,"scale")
    if len(fcurves) != 3:
        if len(fcurves) != 0:
            writeWarning(
                "Incomplete scale keyframes. Please use all three scalechannels")
        fcurves = []
    return fcurves

def createEDMModel(export_render, export_collision):
    resetData()
    # layer = bpy.context.view_layer
    actionindex = 0

    def update_actionindex(arg, actionindex):
        if arg+1 > actionindex:
            actionindex = arg+1
        return actionindex
    
    # layer.update()
    global warningStrs
    warningStrs = []
    armatures = []
    global exportErrorStr
    exportErrorStr = ""
    for i in bpy.data.objects:
        if i.type == 'ARMATURE':
            if i.data.EDMArmatureExport:
                armatures.append(i)
    if len(armatures) > 1:
        exportErrorStr = "Use only one armature! Not writing. See readme"
        print(exportErrorStr)
        return None
    if len(armatures) == 0:
        exportErrorStr = "No armature found! Not writing. See readme"
        print(exportErrorStr)
        return None
    # for armature in armatures:
    armature = armatures[0]
    bones = armature.data.bones
    # create list of animated bones.
    actions = bpy.data.actions
    animatedbones = {}
    # print("Actions:")
    for action in actions:
        if not action.exportToEDM:
            continue
        # print(action.name)
        for fcu in action.fcurves:
            type, name, prop = parseAnimationPath(fcu)
            if type == "pose.bones":
                if bones[name].layers[0] == True:  # only layer 1 is exported
                    if name in animatedbones:
                        animatedbones[name].append(fcu)
                    else:
                        animatedbones[name] = [fcu]
    boneid = {}
    nodeindex = 0
    edmmodel = EDMModel()
    count = 0
    rootBone = 0
    for bone in bones:
        if bone.parent == None and bone.layers[0] == True:
            rootBone = bone
            count += 1
    if count > 1:
        exportErrorStr = "Use ONE bone as Root of the armature"
        print(exportErrorStr)
        return None
    # Transform from Blender Coords to DCS coords
    b = TransformNode(rootBone)  # rootBone is just a Dummy to create the node
    b.matrix = mathutils.Matrix.Rotation(-radians(90.0), 4, 'Z') @ mathutils.Matrix.Rotation(-radians(
        90.0), 4, 'Y') @  mathutils.Matrix.Identity(4)
    b.matrix = b.matrix @ armature.matrix_local
    b.parentid = nodeindex
    edmmodel.nodes.append(b)
    nodeindex += 1
    # Transformnodes start with rootBone
    if rootBone.name in animatedbones:
        b = ArgAnimationNode(rootBone)
    else:
        b = TransformNode(rootBone)
    b.parentid = nodeindex
    nodeindex += 1
    boneid[rootBone.name] = nodeindex
    edmmodel.nodes.append(b)
    # all Childbones:
    children = []
    getAllChildren(rootBone, children)
    count = 0
    for c in children:
        if c.layers[0] == False:  # skipping
            continue
        if c.name in animatedbones:
            if c.use_deform:
                b = AnimatedBoneNode(c)
            else:
                b = ArgAnimationNode(c)
        else:
            if c.use_deform:
                b = BoneNode(c)
            else:
                b = TransformNode(c)
        count += 1
        b.parentid = boneid[c.parent.name]
        edmmodel.nodes.append(b)
        nodeindex += 1
        boneid[c.name] = nodeindex
    # Object Children

    children = []
    getAllChildren(armature, children)
    for c in children:
        if c.type == 'EMPTY':
            type = c.EDMEmptyType
        if c.type == 'MESH':
            edmmodel.rootNode.updateBoundingBox(c)
            type = c.EDMRenderType
        if type == 'RenderNode':
            if not export_render:
                continue
            if hasMaterial(c) and meshIsOk(c, True):
                r = RenderNode(c)
                edmmodel.rootNode.materials.append(r.material)
            else:
                continue
        if type == 'FakeOmniLight':
            if not export_render:
                continue
            r = FakeOmniLightNode(c)
            edmmodel.rootNode.materials.append(r.material)
        if type == 'ShellNode':
            if not export_collision:
                continue
            r = ShellNode(c)
            edmmodel.rootNode.updateBoundingBox(c)
        if type == 'SegmentsNode':
            if not export_collision:
                continue
            r = SegmentsNode(c)
            edmmodel.rootNode.updateBoundingBox(c)
        if type == 'Connector':
            if not export_render:
                continue
            r = ConnectorNode(c)
            edmmodel.rootNode.updateBoundingBox(c)
        if type == 'Light':
            if not export_render:
                continue
            r = EDMLight(c)
            edmmodel.rootNode.updateBoundingBox(c)
        if type == 'RenderNode' or type == 'ShellNode' or type == 'SegmentsNode' or type == 'Connector' or type == 'FakeOmniLight' or type == 'Light':
            if c.parent_bone == "":
                writeWarning("Object '{}' is not parented".format(c.name))
            else:
                if c.parent_bone in armature.data.bones:
                    t = getOffsetTransform(
                        c, armature.data.bones[c.parent_bone], type == 'Connector' or type == 'Light')
                    r.parentData = boneid[c.parent_bone]
                    if t != None:
                        t.parentid = boneid[c.parent_bone]
                        edmmodel.nodes.append(t)
                        nodeindex += 1
                        boneid[c.name+"transform"] = nodeindex
                        r.parentData = nodeindex
                    if type == 'RenderNode':
                        edmmodel.RenderNodes.append(r)
                    if type == 'FakeOmniLight':
                        edmmodel.RenderNodes.append(r)
                    if type == 'ShellNode':
                        edmmodel.ShellNodes.append(r)
                    if type == 'SegmentsNode':
                        edmmodel.SegmentsNodes.append(r)
                    if type == 'Connector':
                        edmmodel.Connectors.append(r)
                    if type == 'Light':
                        edmmodel.LightNodes.append(r)
                else:
                    writeWarning("Parent for '{}' is not found".format(c.name))
        if type == 'SkinNode':
            if not export_render:
                continue
            if hasMaterial(c) and meshIsOk(c, True):
                r = SkinNode(c, boneid)
                edmmodel.rootNode.materials.append(r.material)
                edmmodel.SkinNodes.append(r)
                edmmodel.rootNode.updateBoundingBox(c)
        if type != 'Connector' and type != 'SkinNode':
            fcus, arguments = getVisibilityFCurves(c)
            if fcus:
                v = VisibilityNode(r.parentData)
                for i_fcu in range(len(fcus)):
                    v.addFCurve(arguments[i_fcu], fcus[i_fcu])
                    actionindex = update_actionindex(arguments[i_fcu], actionindex)

                edmmodel.nodes.append(v)
                nodeindex += 1
                boneid[c.name+"visibility"] = nodeindex
                r.parentData = nodeindex
        if type == 'SkinNode':
            fcus, arguments = getVisibilityFCurves(c)
            if fcus:
                print("Skinvisivbility")
                print(r.bones[0])
                print(edmmodel.nodes[r.bones[0]].name)
                v = VisibilityNode(edmmodel.nodes[r.bones[0]].parentid)
                v.name = c.name
                for i_fcu in range(len(fcus)):
                    v.addFCurve(arguments[i_fcu], fcus[i_fcu])
                    actionindex = update_actionindex(arguments[i_fcu], actionindex)
                # print(actionindex)
                edmmodel.nodes.append(v)
                nodeindex += 1
                boneid[c.name+"visibility"] = nodeindex
                edmmodel.nodes[r.bones[0]].parentid = nodeindex
    printnodes = True
    if printnodes:
        print("")
        print("Nodes: ")
        count = 0
        for n in edmmodel.nodes:
            print(str(count)+": " + n.name+" Parent: "+str(n.parentid))
            count += 1
        print("")
        print("Rendernodes:")
        for n in edmmodel.RenderNodes:
            print(str(count)+": " + n.name+"\ Parent: "+str(n.parentData))
            count += 1
        print("Skinnodes:")
        count = 0
        for n in edmmodel.SkinNodes:
            print(str(count)+": " + n.name)
            count += 1
        # print(boneid)
        print("")
        # print("Add Actions")

    for action in actions:
        if not action.exportToEDM:
            continue

        # print("Action: "+action.name)
        if action.EDMAutoRange:
            tMin, tMax = action.frame_range
        else:
            tMin = action.EDMStartFrame
            tMax = action.EDMEndFrame
        relative_keyframes = {"rot": {}, "loc":{},"scale":{}}
        if action.EDMRelativeTo is not None:
            relative_action = action.EDMRelativeTo
            relative_animatedbones = {}
            for fcu in relative_action.fcurves:
                type, name, prop = parseAnimationPath(fcu)
                if type == "pose.bones":
                    if bones[name].layers[0] == True:
                        if name in relative_animatedbones:
                            relative_animatedbones[name].append(fcu)
                        else:
                            relative_animatedbones[name] = [fcu]
            for n, l in relative_animatedbones.items():
                rotationfcurves = []
                translationfcurves = []
                scalefcurves = []
                for fcu in l:
                    type, name, prop = parseAnimationPath(fcu)
                    known = False
                    if prop == "rotation_quaternion":
                        known = True
                        rotationfcurves.append(fcu)
                    if prop == "location":
                        known = True
                        translationfcurves.append(fcu)
                    if prop == "scale":
                        known = True
                        scalefcurves.append(fcu)
                    if known == False:
                        writeWarning("unknown animationsargument "+prop)

                if len(rotationfcurves) != 0:
                    N = checkKeyframes(rotationfcurves)
                    if N != None:
                        animation_data = get_animation_data(rotationfcurves, mathutils.Quaternion, 0, 1)
                        key_frame = animation_data[0]["value"]
                        if not n in relative_keyframes["rot"]:
                            relative_keyframes["rot"][n]=[]
                        relative_keyframes["rot"][n].append(key_frame)
                if len(translationfcurves) != 0:
                    N = checkKeyframes(translationfcurves)
                    if N != None:
                        M = edmmodel.nodes[boneid[name]].Q1.to_matrix()
                        animation_data = get_animation_data(translationfcurves, mathutils.Vector,0, 1)
                        key_frame = animation_data[0]["value"]
                        if not n in relative_keyframes["loc"]:
                            relative_keyframes["loc"][n]=[]
                        relative_keyframes["loc"][n].append(M @ key_frame)
                if len(scalefcurves) != 0:
                    N = checkKeyframes(scalefcurves)
                    if N != None:
                        animation_data = get_animation_data(scalefcurves, mathutils.Vector, 0, 1)
                        key_frame = animation_data[0]["value"]
                        if not n in relative_keyframes["scale"]:
                            relative_keyframes["scale"][n]=[]
                        relative_keyframes["scale"][n].append(key_frame)
        else:
            relative_keyframes = {"rot": {}, "loc":{},"scale":{}}
        b = 2.0/(tMax-tMin)
        a = -tMin*b-1.0
        
        animatedbones = {}
        for fcu in action.fcurves:
            type, name, prop = parseAnimationPath(fcu)
            if type == "pose.bones":
                if bones[name].layers[0] == True:
                    if name in animatedbones:
                        animatedbones[name].append(fcu)
                    else:
                        animatedbones[name] = [fcu]
            else:
                if type != 'Visibility':
                    writeWarning(
                        "'{}' - Animation are not supported".format(type))
                    
        for n, l in animatedbones.items():
            rotationfcurves = []
            translationfcurves = []
            scalefcurves = []
            for fcu in l:
                type, name, prop = parseAnimationPath(fcu)
                known = False
                if prop == "rotation_quaternion":
                    known = True
                    rotationfcurves.append(fcu)
                if prop == "location":
                    known = True
                    translationfcurves.append(fcu)
                if prop == "scale":
                    known = True
                    scalefcurves.append(fcu)
                if known == False:
                    writeWarning("unknown animationsargument "+prop)
            

            if len(rotationfcurves) != 0:
                N = checkKeyframes(rotationfcurves)
                if N != None:
                    animation_data = get_animation_data(rotationfcurves, mathutils.Quaternion, a, b)
                    
                    M = mathutils.Quaternion([1.0,0.0,0.0,0.0]).to_matrix()
                    if n in relative_keyframes["rot"]:
                        for o in relative_keyframes["rot"][n]:
                            M = o.to_matrix()
                        M.invert()
                    data = []
                    for d in animation_data:
                        data.append(EDMAnimationData(d["frame"], (M @ d["value"].to_matrix()  ).to_quaternion()))
                    edmmodel.nodes[boneid[name]].rotationAnimations.append(
                        EDMAnimationSet(action.animationArgument, data, []))
                    actionindex = update_actionindex(action.animationArgument, actionindex)
                
            if len(translationfcurves) != 0:
                N = checkKeyframes(translationfcurves)
                if N != None:
                    M = edmmodel.nodes[boneid[name]].Q1.to_matrix()
                    animation_data = get_animation_data(translationfcurves, mathutils.Vector, a, b)
                    data = []
                    offset = mathutils.Vector()
                    if n in relative_keyframes["loc"]:
                        for o in relative_keyframes["loc"][n]:
                            offset = offset + o
                    for d in animation_data:
                        data.append(EDMAnimationData(d["frame"], (M @ d["value"])-offset))
                    edmmodel.nodes[boneid[name]].positionAnimations.append(
                        EDMAnimationSet(action.animationArgument, data, []))
                    actionindex = update_actionindex(action.animationArgument, actionindex)

            if len(scalefcurves) != 0:
                N = checkKeyframes(scalefcurves)
                if N != None:
                    animation_data = get_animation_data(scalefcurves, mathutils.Vector, a, b)
                    data = []
                    for d in animation_data:
                        data.append(EDMAnimationData(d["frame"], d["value"]))
                    data2 = []
                    data2.append(EDMAnimationData(
                        0, mathutils.Quaternion([1.0, 0.0, 0.0, 0.0])))
                    edmmodel.nodes[boneid[name]].scaleAnimations.append(
                        EDMAnimationSet(action.animationArgument, data2, data))
                    actionindex = update_actionindex(action.animationArgument, actionindex)
                    
    if armature.data.EDMAutoCalcBoxes:
        edmmodel.rootNode.UserMin = edmmodel.rootNode.BoundingMin
        edmmodel.rootNode.UserMax = edmmodel.rootNode.BoundingMax
    else:
        mat = mathutils.Matrix.Rotation(-radians(90.0), 3, 'Z') @ mathutils.Matrix.Rotation(-radians(
            90.0), 3, 'Y') @  mathutils.Matrix.Identity(3)
        edmmodel.rootNode.UserMin = mat@mathutils.Vector(
            armature.data.EDMUserBoxMin)
        edmmodel.rootNode.UserMax = mat@mathutils.Vector(
            armature.data.EDMUserBoxMax)
        edmmodel.rootNode.BoundingMin = mat@mathutils.Vector(
            armature.data.EDMBoundingBoxMin)
        edmmodel.rootNode.BoundingMax = mat@mathutils.Vector(
            armature.data.EDMBoundingBoxMax)

    edmmodel.rootNode.NAnimationArgs = actionindex+1
    return edmmodel


def prepareObjects():
    for c in bpy.data.objects:
        print(c.name)
        if c.type == 'MESH' and not c.EDMRenderType == 'SegmentsNode' and not c.EDMRenderType == 'None':
            if meshIsOk(c, False):
                me = c.data
                uv_layer = c.data.uv_layers[0].data
                for poly in me.polygons:
                    loop = range(poly.loop_start,
                                 poly.loop_start + poly.loop_total)
                    for loop_index in loop:
                        # ursprünglicher vertex
                        id = me.loops[loop_index].vertex_index
                        tangent = me.loops[loop_index].tangent
                        bitangent = me.loops[loop_index].bitangent
                        normal = me.loops[loop_index].normal
                        uv = mathutils.Vector(
                            [uv_layer[loop_index].uv[0], 1.0-uv_layer[loop_index].uv[1]])  # uv
                #me.calc_normals()
                me.calc_tangents(uvmap=c.data.uv_layers[0].name)
                me.free_tangents()

    bpy.context.view_layer.update()
    return True


def getEDMWarnings():
    return warningStrs


def getEDMError():
    return exportErrorStr
