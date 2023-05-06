import bpy


class EDMMessageBox(bpy.types.Operator):
    bl_idname = "edmexporter.messagebox"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    message: bpy.props.StringProperty(
        name="message",
        description="Message text",
        default=''
    )

    # msgtype = bpy.props.StringProperty(
    #     name = "msgtype",
    #     description = "Message type",
    #     default = 'INFO'
    # )

    wrnlist: bpy.props.StringProperty(
        name="wrnlist",
        description="List of warning strings separated by |",
        default=""
    )

    def execute(self, context):
        #       self.report({self.msgtype}, self.message)
        return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.layout.label(text=self.message, icon='ERROR')
        if len(self.wrnlist):
            col = self.layout.column()
            for wrnStr in list(self.wrnlist.split('|')):
                col.label(text="­­­   {}".format(wrnStr))
        self.layout.label(text="")
