
# Maya - Vertex Animation Texture Baker

A Maya tool to bake animations from Maya into a texture to use in Game Engines.




## FAQ

#### Installation
Intall script files to Maya Scripts folder
```
*\Documents\maya\2023\scripts\VertexAnimationTexture\VertexAnimationGUI.py
*\Documents\maya\2023\scripts\VertexAnimationTexture\VertexAnimationCapture.py
*\Documents\maya\2023\scripts\VertexAnimationTexture\spliceimage.py
*\Documents\maya\2023\scripts\VertexAnimationTexture\__init__.py
```
Add Maya button to shelf
```
from VertexAnimationTexture import VertexAnimationGUI
from importlib import reload
reload(VertexAnimationGUI)


start = VertexAnimationGUI.VATUI()
start.show()
```
Install Qt.py wrapper to Maya Scripts 

[Git Repo - QT.py](https://github.com/mottosso/Qt.py)

```
*\Documents\maya\2023\scripts\Qt.py
```
Run button on shelf to open Vertex Animation Texture GUI

###Using the premade UE materials
- Add the VAT folder inside of the content folder in your Unreal Project
- Make an instance of the MM_demo_MayaToUnreal_VAT material and import your texture maps.
- Make sure textures have SRGB turned off!!!
- Ensure scale setting is the same as used to bake in Maya.
- Make any changes you need.

#### How to use?
- Select a mesh
- Adjust playrange on timeline for time to bake
- Press update
- Choose a output directory
- Press Start

#### Limitations
- Doesn't support hard edges - ensure all edges is shaded soft/smooth. Bevel or disconnect edges if you really need hard edges.
- Meshes above 4096 vertices are at risk of breaking and might require manual tweaking of UVs - You might be able to mitigate this be ordering the vertices in Maya
- Vertex position is based off local transforms, ensure that mesh has frozen transforms and any animations aren't directly parented to the mesh pivot. E.g Transform constraints and order heirarchy. use a full weight joint as a buffer since skinning is fine. If the mesh channel box changes values then it probably won't work.
- Joint-based animations may need the mesh to be manually exported from frame 0 via duplicating then exporting if frame 0 is not rig rest pose.

### How it works
- New UV map is created which puts all the vertices in order to line up with pixel location.
- Vertex Positions are baked in local space from the mesh pivot
- All vertex positions are relative offsets to frame 0 on the timeline
- Mesh is exported from frame 0
- Normals are baked from local space. So a normal facing up would be 0,1,0
- XYZ bakes to RGB are in Maya's coordinate space. Y-up, right-handed
- Position XYZ is baked to RGB via equation: ((XYZ/scale)+1)/2=RGB
- Scale is needed to remap position range from; e.g -89...89 to -1..1 with a scale of 89. Scale needs to be identitical 
- Normal XYZ is baked to RGB via equation: ((XYZ+1)/2)=RGB
- To use in Game Engine, you need to reverse the equation to plug into WPO
- Make sure textures are sampled linear (no SRGB)
- Pan the texture map vertically with shader to 'play' the animation in Engine.









## Demo

[Video Demo](https://youtu.be/kuKEY0qqS6Q)


## Check me out on:
[Linkedin](https://www.linkedin.com/in/charlesvonkalm/)
[ArtStation](https://www.artstation.com/charlesvonkalm)
