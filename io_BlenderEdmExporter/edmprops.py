import bpy


class BlenderEDMOptions(bpy.types.PropertyGroup):
    bpy.types.Object.EDMRenderType= bpy.props.EnumProperty(
        items = [('RenderNode', 'RenderNode', 'none deformed mesh'), 
                ('SkinNode', 'SkinNode', 'Bone-defomed mesh'),
                ('ShellNode', 'ShellNode', 'Collisionbox'),
                ('None', 'None','Nothing')],
        name = "RenderType",
        default='None')
    bpy.types.Object.EDMEmptyType= bpy.props.EnumProperty(
        items = [('Connector', 'Connector', 'Connector'),
                ('FakeOmniLight','FakeOmniLight','FakeOmniLight'),
                ('None', 'None','Nothing')],
        name = "EmptyType",
        default='None')        
    bpy.types.Material.EDMMaterialType= bpy.props.EnumProperty(
        items = [('Glass', 'Glass', 'Glass'), 
                ('Solid', 'Solid', 'Solid'),
                ('transp_self_illu','transparent self-illuminated',  'transparent self-illuminated'),
                ('self_illu', 'self-illuminated', 'self-illuminated'),
                ('bano', 'bano_material', 'bano_material')],
        name = "MaterialType",
        default='Solid')
    bpy.types.Object.FakeOmniLightTextureName=bpy.props.StringProperty(
        name="filename",
        default="texture_light")
    bpy.types.Object.FakeLightUV2=bpy.props.FloatVectorProperty(
        name="UV2",
        default=(1,1),
        min=0.0,
        size=2)
    bpy.types.Object.FakeLightScale=bpy.props.FloatProperty(
        name="Scale",
        default=0.5,
        min=0.0,
        max=300.0)
    bpy.types.Object.FakeLightShift=bpy.props.FloatProperty(
        name="Shift to Cam",
        default=0.0,
        min=-50.0,
        max=50.0)
    bpy.types.Object.FakeLightP1=bpy.props.FloatVectorProperty(
        name="Position Offset",
        default=(0.0,0.0,0.0),
        size=3)
    bpy.types.Object.FakeLightUV1=bpy.props.FloatVectorProperty(
        name="UV1",
        default=(0.0,0.0),
        min=0.0,
        size=2)
    bpy.types.Material.EDMUseDiffuseMap=bpy.props.BoolProperty(
        name="Use diffuse map",
        default = True)
    bpy.types.Material.EDMUseAlpha=bpy.props.BoolProperty(
        name="Use alpha channel",
        default = False)		
    bpy.types.Material.EDMDiffuseMapName=bpy.props.StringProperty(
        name="filename",
        default="texture")
    bpy.types.Material.EDMDiffuseValue=bpy.props.FloatProperty(
        name="Diffuse value",
        default=1.0,
        min=0.0,
        max=10.0)
    bpy.types.Material.EDMDiffuseShift=bpy.props.FloatProperty(
        name="Diffuse shift",
        default=0.0,
        min=0.0,
        max=1.0)    
    bpy.types.Material.EDMReflectionValue=bpy.props.FloatProperty(
        name="Reflection value",
        default=0.0,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMReflectionBlurring=bpy.props.FloatProperty(
        name="Reflection Blurring",
        default=0.2,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMSelfIllumination=bpy.props.FloatProperty(
        name="Self Illumination Value",
        default=1,
        min=0.0,
        max=10.0)
    bpy.types.Material.EDMUseNormalMap=bpy.props.BoolProperty(
        name="Use normalmap",
        default = False)
    bpy.types.Material.EDMNormalMapName=bpy.props.StringProperty(
        name="filename",
        default="texture_normal")
    bpy.types.Material.EDMNormalMapValue=bpy.props.FloatProperty(
        name="Normal map value",
        default=0.0,
        min=0.0,
        max=1.0)    
    bpy.types.Material.EDMUseSpecularMap=bpy.props.BoolProperty(
        name="Use specular map",
        default = False)        
    bpy.types.Material.EDMSpecularMapValue=bpy.props.FloatProperty(
        name="Specular map value",
        default=0.0,
        min=0.0,
        max=1.0)
    bpy.types.Material.EDMSpecularMapName=bpy.props.StringProperty(
        name="filename",
        default="texture_spec")
    bpy.types.Material.EDMSpecularFactor=bpy.props.FloatProperty(
        name="Specular factor",
        default=0.1,
        min=0.0,
        max=100.0)
    bpy.types.Material.EDMSpecularPower=bpy.props.FloatProperty(
        name="Specular power",
        default=0.07,
        min=0.0,
        max=100.0)    
    #Action based
    bpy.types.Action.exportToEDM= bpy.props.BoolProperty(
        name="Export Action to EDM",
        default = False)
    bpy.types.Action.animationArgument= bpy.props.IntProperty(
        name="Animation Argument",
        default=0,
        min=0)



