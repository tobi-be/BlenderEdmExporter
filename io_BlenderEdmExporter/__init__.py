bl_info = {
    "name": "EDM-Exporter",
    "blender": (2, 82, 0),
    "category": "Import-Export",
	"author": "Tobias Berkefeld"
}

import bpy
from .edmexporter import*
from .edmpanels import*
from .edmprops import*
from .edmmessagebox import*
from bpy_extras.io_utils import ExportHelper

if "bpy" in locals():
    import importlib
    if "edmexporter" in locals():
        importlib.reload(edmexporter)
    if "edmpanels" in locals():
        importlib.reload(edmpanels)
    if "edmprops" in locals():
        importlib.reload(edmprops)

#operators
class ExportEDMFile(bpy.types.Operator,ExportHelper):
    bl_idname = "exportedm.edm"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Export EDM"         # Display name in the interface.
    bl_options = {'UNDO'}  # Enable undo for the operator.
    filename_ext = ".edm"

    filter_glob: bpy.props.StringProperty(
        default="*.edm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    def execute(self, context):
        #logfile = open("D:/edm/logfile.txt", "w")
        #logfile.write("Log EDM-Export")
        if not len(bpy.context.selected_objects) ==0:
            bpy.ops.object.mode_set(mode='OBJECT')
        prepareObjects()
        edmmodel=createEDMModel()
        resultVal={'CANCELLED'}
        if edmmodel!=None:
            edmmodel.write( self.filepath )
            warningStrs = getEDMWarnings()
            if len(warningStrs):
                bpy.ops.edmexporter.messagebox('INVOKE_DEFAULT', message="Export finished with next warnings:", wrnlist='|'.join(warningStrs))
            print("Finished")
            resultVal={'FINISHED'}
            self.report({'INFO'},"Export to EDM finished.")
        else:
            msg = "Export to EDM failed"
            exportErrorStr = getEDMError()
            if (len(exportErrorStr)):
                msg = msg + ": "+exportErrorStr
            self.report({'ERROR'}, msg)
        #logfile.close()
        return resultVal

def menu_function_export(self, context):
    self.layout.operator(ExportEDMFile.bl_idname,
        text="Export EDM (.edm)")


def register():
    bpy.utils.register_class(BlenderEDMOptions)
    bpy.utils.register_class(ExportEDMFile)
    bpy.types.TOPBAR_MT_file_export.append(menu_function_export)
    bpy.utils.register_class(EDMObjectPanel)
    bpy.utils.register_class(ActionOptionPanel)
    bpy.utils.register_class(EDMMessageBox)

def unregister():
    bpy.utils.unregister_class(ActionOptionPanel)
    bpy.utils.unregister_class(EDMObjectPanel)
    bpy.utils.unregister_class(BlenderEDMOptions)
    bpy.utils.unregister_class(ExportEDMFile)
    bpy.utils.unregister_class(EDMMessageBox)



# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
