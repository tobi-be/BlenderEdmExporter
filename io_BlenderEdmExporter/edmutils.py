import bpy


def getAllChildren(obj, list):
    for x in obj.children:
        list.append(x)
        getAllChildren(x, list)


def parseAnimationPath(fcu):
    path = fcu.data_path
    l = path.split("[")
    if len(l) > 1:
        type = l[0]
        l = l[1].split("]")
        name = l[0][1:len(l[0])-1]
        prop = l[1].split(".")[1]
        return type, name, prop
    else:
        if path == "hide_render":
            return "Visibility", "", "Visibility"
    return None, None, None


