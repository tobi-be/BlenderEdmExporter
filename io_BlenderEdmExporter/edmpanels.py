import bpy

class EDMObjectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_select"
    bl_label = "EDM"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None)
        
    def draw_header(self, context):
        layout = self.layout
        #layout.label(text="My Select")
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        #print(context.object.type)
        if context.object.type=='ARMATURE':
            box.prop(bpy.context.object.data, 'EDMArmatureExport')
            box.prop(bpy.context.object.data, 'EDMAutoCalcBoxes')
            if bpy.context.object.data.EDMAutoCalcBoxes==False:
                box2=layout.box()
                box2.label(text="User Box:")
                row = box2.row(align = True)
                colleft=row.column(align=False)
                colleft.prop(bpy.context.object.data,'EDMUserBoxMin')
                colright=row.column(align=False)
                colright.prop(bpy.context.object.data,'EDMUserBoxMax')
                box3=layout.box()
                box3.label(text="Bounding Box:")
                row2 = box3.row(align = True)
                colleft2=row2.column(align=False)
                colleft2.prop(bpy.context.object.data,'EDMBoundingBoxMin')
                colright2=row2.column(align=False)
                colright2.prop(bpy.context.object.data,'EDMBoundingBoxMax')
        
        if context.object.type=='MESH':
            box.prop(bpy.context.object, 'EDMRenderType')
            box.prop(bpy.context.object,'EDMTwoSides')
            type=bpy.context.object.EDMRenderType
            if type=='RenderNode' or type=='SkinNode':
                materialBox=layout.box()
                if len(context.object.material_slots)>0:
                    material=context.object.material_slots[0].material
                    materialBox.label(text="Material: "+material.name)
                    materialBox.prop(material, 'EDMMaterialType')
                    col = materialBox.column(align = True)
                    #Solid   ################################################
                    if material.EDMMaterialType=='Solid':
                        diffuseBox=layout.box()
                        normalBox=layout.box()
                        specularBox=layout.box()
                        damageBox=layout.box()
                        illuminationBox=layout.box()
                        col.prop(material,'EDMBlending')
                        col.prop(material,'EDMShadows')
                        col = diffuseBox.column(align = True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material,'EDMDiffuseShift')
                            col.prop(material,'EDMDiffuseShiftArgument')
                        col = normalBox.column(align = True)
                        col.prop(material,'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material,'EDMNormalMapName')
                            col.prop(material,'EDMNormalMapValue')
                        col = specularBox.column(align = True)
                        col.prop(material,'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material,'EDMSpecularMapName')
                            col.prop(material,'EDMSpecularMapValue')
                        col = specularBox.column(align = True)
                        col.prop(material,'EDMReflectionValue')
                        col.prop(material,'EDMReflectionBlurring')
                        col.prop(material,'EDMSpecularPower')
                        col.prop(material,'EDMSpecularFactor')
                        col = damageBox.column(align = True)
                        col.prop(material,'EDMUseDamageMap')
                        if material.EDMUseDamageMap:
                            col.prop(material,'EDMDamageMapName')
                            col.prop(bpy.context.object,'EDMDamageArgument')
                            col.prop(material,'EDMUseDamageNormalMap')
                            if material.EDMUseDamageNormalMap:
                                col.prop(material,'EDMDamageNormalMapName')
                        col = illuminationBox.column(align = True)
                        col.prop(material,'EDMUseSelfIllumination')
                        if material.EDMUseSelfIllumination:
                            col.prop(material,'EDMSelfIlluminationMapName')
                            col.prop(material,'EDMSelfIllumination')
                            col.prop(material,'EDMSelfIlluminationArgument')

                    #Glass    ###############################################    
                    if material.EDMMaterialType=='Glass':
                        diffuseBox=layout.box()
                        specularBox=layout.box()
                        damageBox=layout.box()
                        col = diffuseBox.column(align = True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material,'EDMDiffuseShift')
                            col.prop(material,'EDMDiffuseShiftArgument')
                        col = specularBox.column(align = True)
                        col.prop(material,'EDMReflectionValue')
                        col.prop(material,'EDMReflectionBlurring')
                        col.prop(material,'EDMSpecularPower')
                        col.prop(material,'EDMSpecularFactor')
                        col = damageBox.column(align = True)
                        col.prop(material,'EDMUseDamageMap')
                        if material.EDMUseDamageMap:
                            col.prop(material,'EDMDamageMapName')
                            col.prop(bpy.context.object,'EDMDamageArgument')
                            #col.prop(material,'EDMUseDamageNormalMap')
                            #if material.EDMUseDamageNormalMap:
                            #    col.prop(material,'EDMDamageNormalMapName')
                    #transparent self-illuminated  ###############################
                    if material.EDMMaterialType=='transp_self_illu':
                        diffuseBox=layout.box()
                        illuminationBox=layout.box()
                        col.prop(material,'EDMSumBlend')
                        col = diffuseBox.column(align = True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMDiffuseShift')
                        col.prop(material,'EDMDiffuseShiftArgument')
                        col = illuminationBox.column(align = True)
                        col.prop(material,'EDMSelfIllumination')
                        col.prop(material,'EDMSelfIlluminationArgument')

                    # self-illuminated#########################################            
                    if material.EDMMaterialType=='self_illu':
                        diffuseBox=layout.box()
                        normalBox=layout.box()
                        specularBox=layout.box()
                        illuminationBox=layout.box()
                        col = diffuseBox.column(align = True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material,'EDMDiffuseShift')
                            col.prop(material,'EDMDiffuseShiftArgument')
                        col = normalBox.column(align = True)
                        col.prop(material,'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material,'EDMNormalMapName')
                            col.prop(material,'EDMNormalMapValue')
                        col = specularBox.column(align = True)
                        col.prop(material,'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material,'EDMSpecularMapName')
                            col.prop(material,'EDMSpecularMapValue')   
                        col.prop(material,'EDMReflectionValue')
                        col.prop(material,'EDMReflectionBlurring')
                        col.prop(material,'EDMSpecularPower')
                        col.prop(material,'EDMSpecularFactor')
                        col = illuminationBox.column(align = True)
                        col.prop(material,'EDMSelfIllumination')
                        col.prop(material,'EDMSelfIlluminationArgument')
                        col.prop(material,'EDMIlluminationColor')
                        col = illuminationBox.column(align = True)
                        col.prop(material,'EDMmultiplyDiffuse')
                        col.prop(material,'EDMPhosphor')

                    if material.EDMMaterialType=='additive_self_illu':
                        diffuseBox=layout.box()
                        normalBox=layout.box()
                        specularBox=layout.box()
                        illuminationBox=layout.box()
                        col = diffuseBox.column(align = True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material,'EDMDiffuseShift')
                            col.prop(material,'EDMDiffuseShiftArgument')
                        col = normalBox.column(align = True)
                        col.prop(material,'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material,'EDMNormalMapName')
                            col.prop(material,'EDMNormalMapValue')
                        col = specularBox.column(align = True)
                        col.prop(material,'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material,'EDMSpecularMapName')
                            col.prop(material,'EDMSpecularMapValue')
                        col.prop(material,'EDMReflectionValue')
                        col.prop(material,'EDMSpecularPower')
                        col.prop(material,'EDMSpecularFactor')
                        col = illuminationBox.column(align = True)
                        col.prop(material,'EDMSelfIllumination')
                        col.prop(material,'EDMSelfIlluminationArgument')
                        col.prop(material,'EDMIlluminationColor')
                        col.prop(material,'EDMmultiplyDiffuse')
                        col.prop(material,'EDMPhosphor')
                    if material.EDMMaterialType=='bano':
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMBanoDistCoefs')
                        col.prop(material,'EDMDiffuseShift')
                        #col = materialBox.column(align = True)
                    if material.EDMMaterialType=='forest':
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        #col = materialBox.column(align = True)
                    if material.EDMMaterialType=='Mirror':
                        col.label(text="Diffuse colormap:")
                        col.prop(material,'EDMDiffuseMapName')
                        col.prop(material,'EDMDiffuseValue')
                        col.prop(material,'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material,'EDMNormalMapName')
                            col.prop(material,'EDMNormalMapValue')
                        col.prop(material,'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material,'EDMSpecularMapName')
                            col.prop(material,'EDMSpecularMapValue')   
                        col.prop(material,'EDMReflectionValue')
                        col.prop(material,'EDMReflectionBlurring')
                        col.prop(material,'EDMSpecularPower')  
                        col.prop(material,'EDMSpecularFactor')    
                    
                     
                else:
                    materialBox.label(text=context.object.name +" has no material")
        if context.object.type=='EMPTY':
            box.prop(bpy.context.object, 'EDMEmptyType')
            if bpy.context.object.EDMEmptyType=='FakeOmniLight':
                box.prop(bpy.context.object,'FakeLightP1')
                box.prop(bpy.context.object,'FakeLightScale')
                box.label(text="FakeOmniLightTexture:")
                box.prop(bpy.context.object,'FakeOmniLightTextureName')
                box.prop(bpy.context.object,'FakeLightUV1')
                box.prop(bpy.context.object,'FakeLightUV2')
                box.prop(bpy.context.object,'FakeLightShift')
            if bpy.context.object.EDMEmptyType=='Light':
                box.prop(bpy.context.object,'EDMLightColor')
                box.prop(bpy.context.object,'EDMLightBrightness')
                box.prop(bpy.context.object,'EDMLightDistance')
                box.prop(bpy.context.object,'EDMisSpot')
                if bpy.context.object.EDMisSpot:
                    box.prop(bpy.context.object,'EDMLightPhi')
                    box.prop(bpy.context.object,'EDMLightTheta')    
                
                
            
class ActionOptionPanel(bpy.types.Panel):
    bl_idname = "ACTION_PT_Option"
    bl_label = "EDM"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_context = "action"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        if context.object.animation_data is None:
            return False			
        if context.object.animation_data.action is None:
            return False		
        return True
        
    def draw_header(self, context):
        layout = self.layout
        #layout.label(text="My Select")
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        if context.object.animation_data.action is not None:
            col = box.column(align = True)
            col.label(text=context.object.animation_data.action.name)
            col.prop(context.object.animation_data.action, 'exportToEDM')
            col.prop(context.object.animation_data.action, 'animationArgument')
            col = box.column(align = True)
            col.prop(context.object.animation_data.action, 'EDMAutoRange')
            if not context.object.animation_data.action.EDMAutoRange:
                row = col.row(align=True)
                row.prop(context.object.animation_data.action, 'EDMStartFrame')
                row.prop(context.object.animation_data.action, 'EDMEndFrame')
            col = box.column(align = True)
            col.label(text="Bake Action")
            row = col.row(align=True)
            row.prop(context.object.animation_data.action, 'EDMBakeStartFrame')
            row.prop(context.object.animation_data.action, 'EDMBakeEndFrame')
            col.operator("action.edmbakeaction")


