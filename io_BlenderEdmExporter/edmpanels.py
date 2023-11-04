import bpy


class EDMVIS_UL_items(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.obj
        split = layout.split(factor=0.3)
        split.label(text="Arg: %d" % (obj.animationArgument))
        split.prop(obj, "name", text="", emboss=False, translate=False)

    def invoke(self, context, event):
        pass


class ACTION_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "visanimation.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        obj = context.object
        idx = obj.visanimation_index

        try:
            item = obj.visanimation[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(obj.visanimation) - 1:
                item_next = obj.visanimation[idx+1].name
                obj.visanimation.move(idx, idx+1)
                obj.visanimation_index += 1
                info = 'Item "%s" moved to position %d' % (
                    item.name, obj.visanimation_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and idx >= 1:
                item_prev = obj.visanimation[idx-1].name
                obj.visanimation.move(idx, idx-1)
                obj.visanimation_index -= 1
                info = 'Item "%s" moved to position %d' % (
                    item.name, obj.visanimation_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (
                    obj.visanimation[idx].name)
                obj.visanimation_index -= 1
                obj.visanimation.remove(idx)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            if context.object:
                anim_data = obj.animation_data
                if anim_data is not None:
                    act = anim_data.action
                    if act:
                        item = obj.visanimation.add()
                        item.name = act.name
                        item.obj = act
                        self.report({'INFO'}, 'Added: "%s"' % (item.name))
                    else:
                        self.report(
                            {'INFO'}, "Nothing selected in the Viewport")
        return {"FINISHED"}


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
        # layout.label(text="My Select")

    def draw(self, context):
        showVisibility = False
        layout = self.layout
        box = layout.box()
        # print(context.object.type)
        if context.object.type == 'ARMATURE':
            box.prop(bpy.context.object.data, 'EDMArmatureExport')
            box.prop(bpy.context.object.data, 'EDMAutoCalcBoxes')
            if bpy.context.object.data.EDMAutoCalcBoxes == False:
                box2 = layout.box()
                box2.label(text="User Box:")
                row = box2.row(align=True)
                colleft = row.column(align=False)
                colleft.prop(bpy.context.object.data, 'EDMUserBoxMin')
                colright = row.column(align=False)
                colright.prop(bpy.context.object.data, 'EDMUserBoxMax')
                box3 = layout.box()
                box3.label(text="Bounding Box:")
                row2 = box3.row(align=True)
                colleft2 = row2.column(align=False)
                colleft2.prop(bpy.context.object.data, 'EDMBoundingBoxMin')
                colright2 = row2.column(align=False)
                colright2.prop(bpy.context.object.data, 'EDMBoundingBoxMax')

        if context.object.type == 'MESH':
            box.operator("object.edmautorigobject")
            box.prop(bpy.context.object, 'EDMAlternativeName')
            box.prop(bpy.context.object, 'EDMRenderType')
            box.prop(bpy.context.object, 'EDMTwoSides')
            type = bpy.context.object.EDMRenderType
            showVisibility = True
            if type == 'RenderNode' or type == 'SkinNode':
                materialBox = layout.box()
                if len(context.object.material_slots) > 0:
                    material = context.object.material_slots[0].material
                    materialBox.label(text="Material: "+material.name)
                    materialBox.prop(material, 'EDMMaterialType')
                    col = materialBox.column(align=True)
                    # Solid   ################################################
                    if material.EDMMaterialType == 'Solid':
                        diffuseBox = layout.box()
                        normalBox = layout.box()
                        specularBox = layout.box()
                        damageBox = layout.box()
                        illuminationBox = layout.box()
                        col.prop(material, 'EDMBlending')
                        col.prop(material, 'EDMShadows')
                        col = diffuseBox.column(align=True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material, 'EDMDiffuseShift')
                            col.prop(material, 'EDMDiffuseShiftArgument')
                        col = normalBox.column(align=True)
                        col.prop(material, 'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material, 'EDMNormalMapName')
                            col.prop(material, 'EDMNormalMapValue')
                        col = specularBox.column(align=True)
                        col.prop(material, 'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material, 'EDMSpecularMapName')
                            col.prop(material, 'EDMSpecularMapValue')
                        col = specularBox.column(align=True)
                        col.prop(material, 'EDMReflectionValue')
                        col.prop(material, 'EDMReflectionBlurring')
                        col.prop(material, 'EDMSpecularPower')
                        col.prop(material, 'EDMSpecularFactor')
                        col = damageBox.column(align=True)
                        col.prop(material, 'EDMUseDamageMap')
                        if material.EDMUseDamageMap:
                            col.prop(material, 'EDMDamageMapName')
                            col.prop(bpy.context.object, 'EDMDamageArgument')
                            col.prop(material, 'EDMUseDamageNormalMap')
                            if material.EDMUseDamageNormalMap:
                                col.prop(material, 'EDMDamageNormalMapName')
                        col = illuminationBox.column(align=True)
                        col.prop(material, 'EDMUseSelfIllumination')
                        if material.EDMUseSelfIllumination:
                            col.prop(material, 'EDMSelfIlluminationMapName')
                            col.prop(material, 'EDMSelfIllumination')
                            col.prop(material, 'EDMSelfIlluminationArgument')

                    # Glass    ###############################################
                    if material.EDMMaterialType == 'Glass':
                        diffuseBox = layout.box()
                        normalBox = layout.box()
                        specularBox = layout.box()
                        damageBox = layout.box()
                        col = diffuseBox.column(align=True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material, 'EDMDiffuseShift')
                            col.prop(material, 'EDMDiffuseShiftArgument')
                        col = normalBox.column(align=True)
                        col.prop(material, 'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material, 'EDMNormalMapName')
                            col.prop(material, 'EDMNormalMapValue')
                        col = specularBox.column(align=True)
                        col.prop(material, 'EDMReflectionValue')
                        col.prop(material, 'EDMReflectionBlurring')
                        col.prop(material, 'EDMSpecularPower')
                        col.prop(material, 'EDMSpecularFactor')
                        col = damageBox.column(align=True)
                        col.prop(material, 'EDMUseDamageMap')
                        if material.EDMUseDamageMap:
                            col.prop(material, 'EDMDamageMapName')
                            col.prop(bpy.context.object, 'EDMDamageArgument')
                            # col.prop(material,'EDMUseDamageNormalMap')
                            # if material.EDMUseDamageNormalMap:
                            #    col.prop(material,'EDMDamageNormalMapName')
                    # transparent self-illuminated  ###############################
                    if material.EDMMaterialType == 'transp_self_illu':
                        diffuseBox = layout.box()
                        illuminationBox = layout.box()
                        col.prop(material, 'EDMSumBlend')
                        col = diffuseBox.column(align=True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMDiffuseShift')
                        col.prop(material, 'EDMDiffuseShiftArgument')
                        col = illuminationBox.column(align=True)
                        col.prop(material, 'EDMSelfIllumination')
                        col.prop(material, 'EDMSelfIlluminationArgument')

                    # self-illuminated#########################################
                    if material.EDMMaterialType == 'self_illu':
                        diffuseBox = layout.box()
                        normalBox = layout.box()
                        specularBox = layout.box()
                        illuminationBox = layout.box()
                        col = diffuseBox.column(align=True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material, 'EDMDiffuseShift')
                            col.prop(material, 'EDMDiffuseShiftArgument')
                        col = normalBox.column(align=True)
                        col.prop(material, 'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material, 'EDMNormalMapName')
                            col.prop(material, 'EDMNormalMapValue')
                        col = specularBox.column(align=True)
                        col.prop(material, 'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material, 'EDMSpecularMapName')
                            col.prop(material, 'EDMSpecularMapValue')
                        col.prop(material, 'EDMReflectionValue')
                        col.prop(material, 'EDMReflectionBlurring')
                        col.prop(material, 'EDMSpecularPower')
                        col.prop(material, 'EDMSpecularFactor')
                        col = illuminationBox.column(align=True)
                        col.prop(material, 'EDMSelfIllumination')
                        col.prop(material, 'EDMSelfIlluminationArgument')
                        col.prop(material, 'EDMIlluminationColor')
                        col = illuminationBox.column(align=True)
                        col.prop(material, 'EDMmultiplyDiffuse')
                        col.prop(material, 'EDMPhosphor')

                    if material.EDMMaterialType == 'additive_self_illu':
                        diffuseBox = layout.box()
                        normalBox = layout.box()
                        specularBox = layout.box()
                        illuminationBox = layout.box()
                        col = diffuseBox.column(align=True)
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMUseDiffuseShift')
                        if material.EDMUseDiffuseShift:
                            col.prop(material, 'EDMDiffuseShift')
                            col.prop(material, 'EDMDiffuseShiftArgument')
                        col = normalBox.column(align=True)
                        col.prop(material, 'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material, 'EDMNormalMapName')
                            col.prop(material, 'EDMNormalMapValue')
                        col = specularBox.column(align=True)
                        col.prop(material, 'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material, 'EDMSpecularMapName')
                            col.prop(material, 'EDMSpecularMapValue')
                        col.prop(material, 'EDMReflectionValue')
                        col.prop(material, 'EDMSpecularPower')
                        col.prop(material, 'EDMSpecularFactor')
                        col = illuminationBox.column(align=True)
                        col.prop(material, 'EDMSelfIllumination')
                        col.prop(material, 'EDMSelfIlluminationArgument')
                        col.prop(material, 'EDMIlluminationColor')
                        col.prop(material, 'EDMmultiplyDiffuse')
                        col.prop(material, 'EDMPhosphor')
                    if material.EDMMaterialType == 'bano':
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMDiffuseValueArgument')
                        col.prop(material, 'EDMBanoDistCoefs')
                        col.prop(material, 'EDMDiffuseShift')
                        # col = materialBox.column(align = True)
                    if material.EDMMaterialType == 'forest':
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        # col = materialBox.column(align = True)
                    if material.EDMMaterialType == 'Mirror':
                        col.label(text="Diffuse colormap:")
                        col.prop(material, 'EDMDiffuseMapName')
                        col.prop(material, 'EDMDiffuseValue')
                        col.prop(material, 'EDMUseNormalMap')
                        if material.EDMUseNormalMap:
                            col.prop(material, 'EDMNormalMapName')
                            col.prop(material, 'EDMNormalMapValue')
                        col.prop(material, 'EDMUseSpecularMap')
                        if material.EDMUseSpecularMap:
                            col.prop(material, 'EDMSpecularMapName')
                            col.prop(material, 'EDMSpecularMapValue')
                        col.prop(material, 'EDMReflectionValue')
                        col.prop(material, 'EDMReflectionBlurring')
                        col.prop(material, 'EDMSpecularPower')
                        col.prop(material, 'EDMSpecularFactor')

                else:
                    materialBox.label(
                        text=context.object.name + " has no material")
        if context.object.type == 'EMPTY':
            box.prop(bpy.context.object, 'EDMEmptyType')
            if bpy.context.object.EDMEmptyType == 'FakeOmniLight':
                showVisibility = True
                box.prop(bpy.context.object, 'FakeLightP1')
                box.prop(bpy.context.object, 'FakeLightScale')
                box.label(text="FakeOmniLightTexture:")
                box.prop(bpy.context.object, 'FakeOmniLightTextureName')
                box.prop(bpy.context.object, 'FakeLightUV1')
                box.prop(bpy.context.object, 'FakeLightUV2')
                box.prop(bpy.context.object, 'FakeLightShift')
            if bpy.context.object.EDMEmptyType == 'Light':
                showVisibility = True
                box.prop(bpy.context.object, 'EDMLightColor')
                box.prop(bpy.context.object, 'EDMLightBrightness')
                box.prop(bpy.context.object, 'EDMBrightnessArgument')
                box.prop(bpy.context.object, 'EDMLightDistance')
                box.prop(bpy.context.object, 'EDMisSpot')
                if bpy.context.object.EDMisSpot:
                    box.prop(bpy.context.object, 'EDMLightPhi')
                    box.prop(bpy.context.object, 'EDMLightTheta')
        if showVisibility:
            VisActionsBox = layout.box()
            VisActionsBox.label(text="Visibility actions:")
            obj = bpy.context.object
            rows = 2
            row = VisActionsBox.row()
            row.template_list("EDMVIS_UL_items", "", obj,
                              "visanimation", obj, "visanimation_index", rows=rows)

            col = row.column(align=True)
            col.operator("visanimation.list_action",
                         icon='ADD', text="").action = 'ADD'
            col.operator("visanimation.list_action",
                         icon='REMOVE', text="").action = 'REMOVE'
            col.separator()
            col.operator("visanimation.list_action",
                         icon='TRIA_UP', text="").action = 'UP'
            col.operator("visanimation.list_action",
                         icon='TRIA_DOWN', text="").action = 'DOWN'


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
        # layout.label(text="My Select")

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        if context.object.animation_data.action is not None:
            col = box.column(align=True)
            col.label(text=context.object.animation_data.action.name)
            col.prop(context.object.animation_data.action, 'exportToEDM')
            col.prop(context.object.animation_data.action, 'animationArgument')
            col = box.column(align=True)
            col.prop(context.object.animation_data.action, 'EDMAutoRange')
            col.prop(context.object.animation_data.action, 'EDMRelativeTo')
            if not context.object.animation_data.action.EDMAutoRange:
                row = col.row(align=True)
                row.prop(context.object.animation_data.action, 'EDMStartFrame')
                row.prop(context.object.animation_data.action, 'EDMEndFrame')
            col = box.column(align=True)
            col.label(text="Bake Action")
            row = col.row(align=True)
            row.prop(context.object.animation_data.action, 'EDMBakeStartFrame')
            row.prop(context.object.animation_data.action, 'EDMBakeEndFrame')
            col.operator("action.edmbakeaction")
