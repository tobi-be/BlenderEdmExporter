**BLENDER EDM EXPORTER**
========================

I have used much of the knowledge provided by NickD. ( https://ndevenish.github.io/Blender_ioEDM/ )He made the difficult start decrypting the EDM files and thus laid the foundation and understanding for developing such addons. Also madwax (https://github.com/madwax/Blender_ioEDM ) who continued the work and kept NickD’s addon running with the DCS updates. I decided to begin from scratch for an exporter for blender 2.8 because things have changed in blender and I wanted to take a slightly different approach to some things. (use of armature) 

Releases:

https://github.com/tobi-be/BlenderEdmExporter/releases

Install:
--------

- Download io_BlenderEdmExporter.zip from asserts of the latest release. 
- Blender: Go to Edit->Preferences->Add-Ons, press install and choose downloaded zip file 
- Activate the add-on

What should work:
------------------

- Mesh export 
- Collision boxes
- Bone deformed animations
- A selection of material types including diffuse, normal and specular maps. roughmet textures can be added later
- FakeOmniLights
- Connectors
- Argument based animations of Visibility, Rotation, Location, Scale and bone deformation
- Lights  

what doesn‘ t work:
------------------

- Import EDM models
- LOD Nodes
- Visibility Nodes on Skin Nodes
- Export of modifiers
- Export of IK chains. Bones which are animated within an IK Chain has to be keyframed additionally by visual rotation or visual location

known issues
------------
- Sometimes UV-Maps aren't exported correctly. This happens more often if you have just left edit mode and export afterwards. Exporting again solves the problem 

General Rules:
==============

Export script could be buggy please report bugs
-----------------------------------------------

Always use an armature
----------------------

Use always an armature even if you don't want to animate anything. This addon uses an armature as the root of the edm model. In the highest hierarchical level must and may only be one bone. This bone then can have children with children of children as you like. Consider this bone as root of the whole edm model. Every (rigid) object you want to be rendered in DCS has to be parented to the armature relative to one bone. The only exception is a bone deformed mesh, which has to be parented to the armature also, but of cause not relative to only one bone. (See SkinNode)
The reason for the need of an armature goes back to the way of animations in blender:
In Blender an armature offers the possibility to handle animations, which contains several bones in one action in the Action Editor. Each bone can be a parent for one or more objects. If you animate the objects directly instead, only one body could be animated in one action. Therefore it was decided that geometric animations (rotation and translation) are only considered and exported using bones. So do not animate objects directly! Always use an Armature. For simplicity in programming, an armature is also required for models without animations

Use quaternions always
----------------------

Other rotation representations are not supported

Read the System Console
-----------------------

Window→Toggle System Console. You should get hints there if somethings goes wrong 

Bone Layers
-----------

Every bone which should be used in the EDM model has to be on bone layer 1. Bones on other bone layers are not exported. This allows you to use IK-bones or pole bones on other layers. Make sure every model-relevant bone is on layer 1. 

First steps to create a simple model:
=====================================

- Create an armature
- Create a mesh object
- Parent mesh object relative to one bone oft the armature
In object mode: select mesh object first, add armature to selection, go to pose mode, click on 	the bone you wish, press (strg+p) choose “Bone Relative”
- assign a material to the mesh object. (this is just a dummy right now but it has to be done)
- check UV-Map (a mesh object has to have a UV-Map)
- Select mesh object. In Object Properties should be a EDM-Panel choose RenderNode as rendertype. 
- Adjust the material settings in the EDM-Panel for this mesh. (See Materials)
- export: File->export->Export .EDM to export the model 

Supported Features
==================

Materials
---------

As a first approach, the EDM panel offers material properties that are present in the existing EDM files. The settings are independent of the Blender materials and have no influence on the appearance in Blender. Also, the Blender internal material properties have no influence on the exported EDM model. First you have to select a general material type. The type names should be almost self-explanatory. The most commonly used material type should be Solid (def_material in  EDM files). I have not spent much time with the different types and their appearance. Therefore I would not write much here, just a short description of the application and wish every user a lot of fun while experimenting.
Each material has a diffuse color map. The name of the texture to be used must be entered in the filename field. In general, textures are always entered without file names. If you want to use "texture.png" there must be "texture" there. Using Normalmaps and specular maps is optional. If you want to use _roughmet textures you have to enable a specular map. (See: https://forums.eagle.ru/showthread.php?t=193596 )

RenderNode
----------

A RenderNode is a non deformable mesh object. Like chassis, wheels, planes, etc. RenderNodes can be animated (rotation and translation) by animating the bone to which it is parented. You have to assign a material to the mesh object. (this is just a dummy right now but it has to be done)

ShellNode
---------

A ShellNode are the collision boxes in EDM files mesh object. ShellNodes have to be parented to a bone and can be animated (rotation and translation) by animating its bone. 

SkinNode
--------
A SkinNode is a bone deformed Mesh used for infantry, pilots, driver or cows. 
Workflow to create a SkinNode would be: 
- Create the mesh and choose SkinNode at EDM-Panel, setup material parameters and UV-map
- Apply tranformation of the mesh object.
- Prepare the armature. In Blender every bone has the property „Deform“ in Bone Properties. If you want to use a SkinNode you should disable this option on every bone which should not deform the mesh. 
- Parent the mesh to the armature with automatic weights and correct weight painting.  

SkinNodes in DCS uses up to 4 bone weights per vertex. In Blender you have to limit the number of weights to 4 to get a proper export. This can be done in weight paint mode at weights→limit total. You have to assign a material to the mesh object. (this is just a dummy right now but it has to be done)
There might be some problems with exporting Skinnodes. I would be happy about every  description of problems.

Connectors
----------

To place a connector in the EDM model you have to place an empty-object in Blender. The name of the connector will be the name of the empty Object. In the EDM-Panel in Object Properties you have to choose Connector at EmptyType.

FakeOmniLight
-------------

To place a FakeOmniLight in the edm model, you have to place an empty-object in Blender and choose FakeOmniLight in the EDM-Panel. Position offset is an offset relative to the position of the empty. Scale is the size of the fake light, UV1 and UV2 are the uv-coords (left bottom and right top) in the texture defined by filename. Shift to cam moves the fake light on an axis pointing from the position of the fake light and the viewer. 

Animation
---------

The way to animate the model is to animate the armature of the model. Every thing which is supposed to show up in DCS has to be parented to the armature. 
The general concept is to use actions of the armature to define argument based animations. Open the Dopesheet Editor and switch to Action Editor. Create a new action in pose mode of the armature  by clicking on new action in Action Editor. You can select a bone and insert keyframes by hitting I. Please use only Rotation and Location. Scale is not supported yet. Use only full sets of rotations or locations in the meaning of keyframing all 4 quaternion properties or all 3 location coordinates. If you use Location and Rotation make sure to insert keyframes for both at the start and at the end of the action. The start and the end of the action is defined by the first and the last keyframes respectively. 
The Action Editor contains an additional panel. This is a bit hidden on the right side of the window. When you expand it you will find the Export to EDM option and the animation argument. You should make every action a fake user. Otherwise the action could be deleted when saving and loading

VisibilityNode
--------------

A VisibilityNode is the way to let an object appear oder disappear with an argument. This is the only thing which has to be animated on an object directly. Select the Object which should get a VisibilityNode in Object Mode.  Open dopesheet editor and switch to Action Editor. Create a new Action. Setup Export to EDM and argument. In Object Properties at Visibility there is a property named „Show in Renders“.  Move mouse over it, change the value as you need and press „I“ to insert a keyframe. Change frame and the value and repeat. To export the VisibilityNode the action has to kept in the animaton data of the object. The animation data of the object is independent of the animation data of the armature. 
