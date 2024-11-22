from maya import cmds
from maya import mel
from Qt import QtCore, QtGui, QtWidgets
import os
from VertexAnimationTexture import spliceimage
from importlib import reload
reload(spliceimage)


def unsign_vector(vec):
    """
    Rescale input list from -1..1 to 0..1
    Args:
        vec: List of 3 float values (x, y, z)
    Returns:
        List of rescaled values in the range [0, 1]
    """
    return [(v + 1) / 2 for v in vec]


def rgbfrompos(xyz, scale=1):
    """ Convert position to RGB values scaled between 0-1 """
    rgb = unsign_vector([i / scale for i in xyz])  # Normalize and rescale [x,y,z]
    if max(rgb) > 1 or min(rgb) < 0:
        cmds.confirmDialog(t="Warning", m="Out of range, please up the scale")
        quit()
    return rgb


class VertsToTexture(dict):

    def verticesfromobject(self, selectedobj):
        vertices = []
        position = []
        normal = []

        if selectedobj:
            vertices = cmds.ls(f"{selectedobj}.vtx[*]", flatten=True)
            for vertex in vertices:
                position.append(cmds.pointPosition(vertex, local=True))
                tempnorm = cmds.polyNormalPerVertex(vertex, query=True, xyz=True)
                normal.append([tempnorm[0], tempnorm[1], tempnorm[2]])

        return vertices, position, normal



    def arrangeuvmap(self, vertices, mesh):

        gapx = 1 / (len(vertices))  # offset between uv coordinated
        x = 0  # count offset for uv
        ImageWidth = (len(vertices))


        # create or set to existing uv map.
        if "vertmap" in cmds.polyUVSet(mesh, query=True, allUVSets=True):
            cmds.polyUVSet(currentUVSet=True, uvSet='vertmap')
        else:
            cmds.polyUVSet(create=True, uvSet='vertmap')
            cmds.polyUVSet(currentUVSet=True, uvSet='vertmap')
        cmds.polyForceUV(cp=True, u=True)

        for vertex in vertices:
            cmds.select(vertex)
            cmds.ConvertSelectionToUVs()
            cmds.polyEditUV(relative=False, uValue=(gapx * x) + (gapx / 2), vValue=1)
            x += 1

        cmds.select(mesh)
        return ImageWidth

    def getMeshInfo(self, step=1, split=False):
        selectedObj = cmds.ls(type="transform", selection=True)

        #checks to make sure mesh is actually a mesh
        if not selectedObj:
            return None
        try:
            child = cmds.listRelatives(selectedObj, children=True, fullPath=True)[0]
            if not (cmds.objectType(child)) == "mesh":
                return None
        except:
            return None

        meshdata = self.verticesfromobject(selectedObj[0])


        start = cmds.playbackOptions(q=True, min=True)
        stop = cmds.playbackOptions(q=True, max=True)

        imagey = int((stop - start) / step)
        imagex = len(meshdata[0])

        if split:
            imagey *= 2
            imagex /= 2
        return selectedObj[0], len(meshdata[0]), int(imagey), int(imagex), int(start), int(stop)





    def main(self, selectedObj, start=0, stop=30, step=1, scale=30, dirpath='', split=False, bit=False):

        playlength = int((stop - start) / step)

        print("Setting Mesh")

        if selectedObj:
            cmds.currentTime(0, edit=True)

            print("Getting Mesh Data")
            self.firstframe_meshdata = self.verticesfromobject(selectedObj)

            print("Baking UV Info")
            ImageWidth = self.arrangeuvmap(vertices=self.firstframe_meshdata[0], mesh=selectedObj)

            print("Starting Image Creation")
            self.createPosImage(playlength, ImageWidth, bit)
            self.createNorImage(playlength, ImageWidth)

            mainpath = f"{dirpath}/SM_{selectedObj}_frame0"
            mel.eval('FBXExportSmoothingGroups -v true')
            mel.eval('FBXExportTangents -v true')
            mel.eval('FBXExport -f "{0}" -s'.format(mainpath))

            #
            imgline = 0

            for i in range(0, stop + 1 - start, step):
                cmds.currentTime(i + start, edit=True)

                meshdata = self.verticesfromobject(selectedObj)

                self.setPosColourinImage(meshdata[1], scale, imgline)
                self.setNorColourinImage(meshdata[2], imgline)

                print(f"{imgline} row of {playlength} processed")
                imgline += 1

            self.output(dirpath, selectedObj, split)

    def output(self, dirPath, object, split):
        dirPath = dirPath.replace("/", '\\')
        posdir = os.path.join(dirPath, f"T_{object}_position_VAT.png")
        nordir = os.path.join(dirPath, f"T_{object}_normal_VAT.png")
        self.posimg.save(posdir, quality=100)
        self.norimg.save(nordir, quality=100)
        print("Exported!")
        if split:
            spliceimage.process_image(posdir)
            spliceimage.process_image(nordir)

    def createNorImage(self, playlength, ImageWidth):
        self.norimg = QtGui.QImage(ImageWidth, playlength, QtGui.QImage.Format_RGB888)
        self.norimg.fill(0)

    def createPosImage(self, playlength, ImageWidth, bit):
        if bit:
            self.posimg = QtGui.QImage(ImageWidth, playlength, QtGui.QImage.Format_RGBX64)
        else:
            self.posimg = QtGui.QImage(ImageWidth, playlength, QtGui.QImage.Format_RGB888)
        self.posimg.fill(0.5)

    def setNorColourinImage(self, normals, time=0):
        rgb = list()

        for xyz in normals:
            rgb.append(unsign_vector(xyz))

        for v in range(len(rgb)):
            self.norimg.setPixelColor(v, time, QtGui.QColor.fromRgbF(*rgb[v]))  # Y, X, RGB

    def setPosColourinImage(self, position, scale, time=0):

        # substract first frame values from current positions to only get offset values.
        OffsetPositions = [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in
                           zip(position, self.firstframe_meshdata[1])]

        rgb = list()
        for xyz in OffsetPositions:
            rgb.append(rgbfrompos(xyz, scale))

        for v in range(len(rgb)):
            self.posimg.setPixelColor(v, time, QtGui.QColor.fromRgbF(*rgb[v]))  # Y, X, RGB




