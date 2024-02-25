from .edmautorig import *
from .edmutils import *
from .edmbakeaction import *
from .edmmessagebox import *
from .edmprops import *
from .edmpanels import *
from .edmexporter import *
from bpy_extras.io_utils import ExportHelper
import bpy
from bpy.props import BoolProperty

bl_info = {
    "name": "EDM-Exporter",
    "blender": (2, 82, 0),
    "category": "Import-Export",
    "author": "Tobsen",
    "version": (1, 0, 12),
}


if "bpy" in locals():
    import importlib
    if "edmexporter" in locals():
        importlib.reload(edmexporter)
    if "edmpanels" in locals():
        importlib.reload(edmpanels)
    if "edmprops" in locals():
        importlib.reload(edmprops)
    if "edmmessagebox" in locals():
        importlib.reload(edmmessagebox)
    if "edmbakeaction" in locals():
        importlib.reload(edmbakeaction)
    if "edmbakeaction" in locals():
        importlib.reload(edmautorig)
    if "edmutils" in locals():
        importlib.reload(edmutils)

# operators


class ExportEDMFile(bpy.types.Operator, ExportHelper):
    # Unique identifier for buttons and menu items to reference.
    bl_idname = "exportedm.edm"
    bl_label = "Export EDM"         # Display name in the interface.
    # bl_options = {}
    filename_ext = ".edm"

    filter_glob: bpy.props.StringProperty(
        default="*.edm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    skip_collision: BoolProperty(
        name="Skip collision",
        description="Export without Collision objects",
        default=False,
    )

    skip_render: BoolProperty(
        name="Skip Render",
        description="Export without Render objects",
        default=False,
    )

    def execute(self, context):
        # logfile = open("D:/edm/logfile.txt", "w")
        # logfile.write("Log EDM-Export")
        if not len(bpy.context.selected_objects) == 0:
            bpy.ops.object.mode_set(mode='OBJECT')
        #prepareObjects()
        edmmodel = createEDMModel(not self.skip_render, not self.skip_collision)
        resultVal = {'CANCELLED'}
        if edmmodel != None:
            edmmodel.write(self.filepath)
            warningStrs = getEDMWarnings()
            if len(warningStrs):
                bpy.ops.edmexporter.messagebox(
                    'INVOKE_DEFAULT', message="Export finished with next warnings:", wrnlist='|'.join(warningStrs))
            print("Finished")
            resultVal = {'FINISHED'}
            self.report({'INFO'}, "Export to EDM finished.")
        else:
            msg = "Export to EDM failed"
            exportErrorStr = getEDMError()
            if (len(exportErrorStr)):
                bpy.ops.edmexporter.messagebox(
                    'INVOKE_DEFAULT', message=msg + ": " + exportErrorStr)
        # logfile.close()
        return resultVal


def menu_function_export(self, context):
    self.layout.operator(ExportEDMFile.bl_idname,
                         text="Export EDM (.edm)")


def register():
    bpy.utils.register_class(ACTION_OT_actions)
    bpy.utils.register_class(EDMVIS_UL_items)
    bpy.utils.register_class(ACTION_PG_objectCollection)

    bpy.utils.register_class(BlenderEDMOptions)
    bpy.utils.register_class(ExportEDMFile)
    bpy.types.TOPBAR_MT_file_export.append(menu_function_export)
    bpy.utils.register_class(EDMObjectPanel)
    bpy.utils.register_class(ActionOptionPanel)
    bpy.utils.register_class(EDMMessageBox)
    bpy.utils.register_class(EDMBakeAction)
    bpy.utils.register_class(EDMAutoRigObject)

    bpy.types.Object.visanimation = bpy.props.CollectionProperty(
        type=ACTION_PG_objectCollection)
    bpy.types.Object.visanimation_index = bpy.props.IntProperty()


def unregister():
    bpy.utils.unregister_class(EDMAutoRigObject)
    bpy.utils.unregister_class(EDMBakeAction)
    bpy.utils.unregister_class(ActionOptionPanel)
    bpy.utils.unregister_class(EDMObjectPanel)
    bpy.utils.unregister_class(BlenderEDMOptions)
    bpy.utils.unregister_class(ExportEDMFile)
    bpy.utils.unregister_class(EDMMessageBox)

    bpy.utils.unregister_class(ACTION_OT_actions)
    bpy.utils.unregister_class(EDMVIS_UL_items)
    bpy.utils.unregister_class(ACTION_PG_objectCollection)

    del bpy.types.Object.visanimation
    del bpy.types.Object.visanimation_index


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
