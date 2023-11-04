import bpy

def filter_callback(self, object):
    return True

class ACTION_PG_objectCollection(bpy.types.PropertyGroup):
    # name: StringProperty() -> Instantiated by default
    obj: bpy.props.PointerProperty(name="Action", type=bpy.types.Action)


class BlenderEDMOptions(bpy.types.PropertyGroup):
    bpy.types.Armature.EDMAutoCalcBoxes = bpy.props.BoolProperty(
        name="Use Calculated Bounding Boxes",
        default=True)
    bpy.types.Armature.EDMUserBoxMin = bpy.props.FloatVectorProperty(
        name="Min",
        default=(-10.0, -10.0, -10.0),
        # min=0.0,
        # max=1.0,
        size=3)
    bpy.types.Armature.EDMUserBoxMax = bpy.props.FloatVectorProperty(
        name="Max",
        default=(10.0, 10.0, 10.0),
        size=3)
    bpy.types.Armature.EDMBoundingBoxMin = bpy.props.FloatVectorProperty(
        name="Min",
        default=(-10.0, -10.0, -10.0),
        size=3)
    bpy.types.Armature.EDMBoundingBoxMax = bpy.props.FloatVectorProperty(
        name="Max",
        default=(10.0, 10.0, 10.0),
        size=3)
    bpy.types.Armature.EDMArmatureExport = bpy.props.BoolProperty(
        name="Export Armature",
        default=True)
    bpy.types.Object.EDMAlternativeName = bpy.props.StringProperty(
        name="Name",
        default="")
    bpy.types.Object.EDMRenderType = bpy.props.EnumProperty(
        items=[('RenderNode', 'RenderNode', 'none deformed mesh'),
               ('SkinNode', 'SkinNode', 'Bone-defomed mesh'),
               ('ShellNode', 'ShellNode', 'Collisionbox'),
               ('SegmentsNode', 'SegmentsNode', 'SegmentsNode'),
               ('None', 'None', 'Nothing')],
        name="RenderType",
        default='None')
    bpy.types.Object.EDMTwoSides = bpy.props.BoolProperty(
        name="Two sides",
        default=False)
    bpy.types.Object.EDMEmptyType = bpy.props.EnumProperty(
        items=[('Connector', 'Connector', 'Connector'),
               ('FakeOmniLight', 'FakeOmniLight', 'FakeOmniLight'),
               ('Light', 'Light', 'Light'),
               ('None', 'None', 'Nothing')],
        name="EmptyType",
        default='None')
    bpy.types.Material.EDMMaterialType = bpy.props.EnumProperty(
        items=[('Glass', 'Glass', 'Glass'),
               ('Solid', 'Solid', 'Solid'),
               ('transp_self_illu', 'transparent self-illuminated',
                'transparent self-illuminated'),
               ('self_illu', 'self-illuminated', 'self-illuminated'),
               ('additive_self_illu', 'additive_self-illuminated',
                'additive_self-illuminated'),
               ('bano', 'bano_material', 'bano_material'),
               ('forest', 'forest', 'forest'),
               ('Mirror', 'Mirror', 'Mirror')],
        name="MaterialType",
        default='Solid')
    bpy.types.Material.EDMBlending = bpy.props.EnumProperty(
        items=[('0', '0', '0'),
               ('1', '1', '1'),
               ('2', '2', '2'),
               ('3', '3', '3')],
        name="Blending",
        default='0')
    bpy.types.Material.EDMShadows = bpy.props.EnumProperty(
        items=[('0', '0', '0'),
               ('1', '1', '1'),
               ('2', '2', '2'),
               ('3', '3', '3')],
        name="Shadows",
        default='1')
    bpy.types.Object.FakeOmniLightTextureName = bpy.props.StringProperty(
        name="filename",
        default="texture_light")
    bpy.types.Object.FakeLightUV2 = bpy.props.FloatVectorProperty(
        name="UV2",
        default=(1, 1),
        min=0.0,
        size=2)
    bpy.types.Object.EDMLightColor = bpy.props.FloatVectorProperty(
        name="Color",
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        size=3)
    bpy.types.Object.EDMLightBrightness = bpy.props.FloatProperty(
        name="Brightness",
        default=(1.0),
        min=0.0)
    bpy.types.Object.EDMBrightnessArgument = bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)
    bpy.types.Object.EDMLightDistance = bpy.props.FloatProperty(
        name="Distance",
        default=(10.0),
        min=0.0)
    bpy.types.Object.EDMLightPhi = bpy.props.FloatProperty(
        name="Phi",
        default=(1.0),
        min=0.0)
    bpy.types.Object.EDMLightTheta = bpy.props.FloatProperty(
        name="Theta",
        default=(1.0),
        min=0.0)
    bpy.types.Object.EDMisSpot = bpy.props.BoolProperty(
        name="Spotlight",
        default=False)
    bpy.types.Object.FakeLightScale = bpy.props.FloatProperty(
        name="Scale",
        default=0.5,
        min=0.0,
        max=300.0)
    bpy.types.Object.FakeLightShift = bpy.props.FloatProperty(
        name="Shift to Cam",
        default=0.0,
        min=-50.0,
        max=50.0)
    bpy.types.Object.FakeLightP1 = bpy.props.FloatVectorProperty(
        name="Position Offset",
        default=(0.0, 0.0, 0.0),
        size=3)
    bpy.types.Object.FakeLightUV1 = bpy.props.FloatVectorProperty(
        name="UV1",
        default=(0.0, 0.0),
        min=0.0,
        size=2)
    bpy.types.Material.EDMBanoDistCoefs = bpy.props.FloatVectorProperty(
        name="Bano Distance Coefs",
        default=(60.0, 1000.0, 100.0),
        min=0,
        size=3)
    bpy.types.Material.EDMUseDiffuseMap = bpy.props.BoolProperty(
        name="Use diffuse map",
        default=True)
    bpy.types.Material.EDMUseDamageMap = bpy.props.BoolProperty(
        name="Use Damage map",
        default=False)
    bpy.types.Material.EDMUseDamageNormalMap = bpy.props.BoolProperty(
        name="Use Damage Normal map",
        default=False)
    bpy.types.Material.EDMSumBlend = bpy.props.BoolProperty(
        name="Sum Blending",
        default=True)
    bpy.types.Material.EDMUseAlpha = bpy.props.BoolProperty(
        name="Use alpha channel",
        default=False)
    bpy.types.Material.EDMDiffuseMapName = bpy.props.StringProperty(
        name="filename",
        default="texture")
    bpy.types.Material.EDMDamageMapName = bpy.props.StringProperty(
        name="filename",
        default="damage")
    bpy.types.Material.EDMDamageNormalMapName = bpy.props.StringProperty(
        name="filename",
        default="damage_normal")
    bpy.types.Material.EDMDiffuseValue = bpy.props.FloatProperty(
        name="Diffuse value",
        default=1.0,
        min=0.0,
        max=10.0)
    bpy.types.Material.EDMPhosphor = bpy.props.FloatProperty(
        name="Phosphor value",
        default=1.0,
        min=0.0,
        max=10.0)
    bpy.types.Material.EDMDiffuseShift = bpy.props.FloatVectorProperty(
        name="Diffuse shift",
        default=(0.0, 0.0),
        min=0.0,
        max=1.0,
        size=2)
    bpy.types.Material.EDMDiffuseShiftArgument = bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)
    bpy.types.Material.EDMDiffuseValueArgument = bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)
    bpy.types.Material.EDMIlluminationColor = bpy.props.FloatVectorProperty(
        name="Illumination Color",
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        size=3)
    bpy.types.Material.EDMReflectionValue = bpy.props.FloatProperty(
        name="Reflection value",
        default=0.0,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMmultiplyDiffuse = bpy.props.FloatProperty(
        name="multiply Diffuse",
        default=0.0,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMReflectionBlurring = bpy.props.FloatProperty(
        name="Reflection Blurring",
        default=0.2,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMUseDiffuseShift = bpy.props.BoolProperty(
        name="Use Diffuse Shift",
        default=False)
    bpy.types.Material.EDMUseSelfIllumination = bpy.props.BoolProperty(
        name="Use Selfillumination",
        default=False)
    bpy.types.Material.EDMSelfIlluminationArgument = bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)
    bpy.types.Object.EDMDamageArgument = bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)
    bpy.types.Material.EDMSelfIllumination = bpy.props.FloatProperty(
        name="Self Illumination Value",
        default=1,
        min=0.0,
        max=100.0)
    bpy.types.Material.EDMUseNormalMap = bpy.props.BoolProperty(
        name="Use normalmap",
        default=False)
    bpy.types.Material.EDMNormalMapName = bpy.props.StringProperty(
        name="filename",
        default="texture_normal")
    bpy.types.Material.EDMSelfIlluminationMapName = bpy.props.StringProperty(
        name="filename",
        default="texture_illumination")
    bpy.types.Material.EDMNormalMapValue = bpy.props.FloatProperty(
        name="Normal map value",
        default=0.0,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMUseSpecularMap = bpy.props.BoolProperty(
        name="Use specular map/Roughtmet",
        default=False)
    bpy.types.Material.EDMSpecularMapValue = bpy.props.FloatProperty(
        name="Specular map value",
        default=0.0,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMSpecularMapName = bpy.props.StringProperty(
        name="filename",
        default="texture_spec")
    bpy.types.Material.EDMSpecularFactor = bpy.props.FloatProperty(
        name="Specular factor",
        default=0.1,
        min=0.0,
        max=100.0)
    bpy.types.Material.EDMSpecularPower = bpy.props.FloatProperty(
        name="Specular power",
        default=0.07,
        min=0.0,
        max=100.0)
    # Action based
    bpy.types.Action.exportToEDM = bpy.props.BoolProperty(
        name="Export Action to EDM",
        default=False)
    bpy.types.Action.EDMAutoRange = bpy.props.BoolProperty(
        name="Autorange",
        default=True)
    bpy.types.Action.EDMStartFrame = bpy.props.IntProperty(
        name="Start",
        default=0)
    bpy.types.Action.EDMEndFrame = bpy.props.IntProperty(
        name="End",
        default=200)
    bpy.types.Action.EDMBakeStartFrame = bpy.props.IntProperty(
        name="Start",
        default=100)
    bpy.types.Action.EDMBakeEndFrame = bpy.props.IntProperty(
        name="End",
        default=200)
    bpy.types.Action.animationArgument = bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)
    bpy.types.Action.EDMRelativeTo = bpy.props.PointerProperty(
        name="Relative to",
        type=bpy.types.Action,
        poll=filter_callback
    )
