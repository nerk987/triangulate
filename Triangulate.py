### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Triangulate",
    "author": "Ian Huish (nerk)",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Triangulate",
    "description": "Animates Empties based on camera triangulation",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"}

import bpy
from mathutils import Vector
from mathutils import geometry
import math
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty    


def Get2DFromTrack(track, clip, clipob, frame):
    # print("track: ", track)
    # print("clip: ", clip)
    # print("clipob: ", clipob)
    
    D = bpy.data
    trackptr = D.movieclips[clip].tracking.objects[clipob].tracks[track]
    markerAtFrame = trackptr.markers.find_frame(frame)
    if markerAtFrame == None:
        return None
    return list(markerAtFrame.co.xy)
    
def GetRayFromTrack(track, clip, clipob, frame, scene):
    D = bpy.data
    coord2D = Get2DFromTrack(track, clip, clipob, frame)
    if coord2D == None:
        return None
    camera = D.objects[clip]
    frame = camera.data.view_frame(scene=scene)
    rayend = Vector((frame[2][0]+coord2D[0]*(frame[0][0]- frame[2][0]), frame[2][1]+coord2D[1]*(frame[0][1]- frame[2][1]), frame[0][2]))
    rayend = camera.matrix_world.normalized()@rayend
    return [camera.location, rayend]

def ReadTracks(scene, MaxError):

    D = bpy.data
    tracks = {}
    TotalError = 0
    ErrorCount = 0.000001
#
# Make a list of empties in the scene. This will be used to filter useful tracks
# 
    Empties = []
    # print("Empty List")
    for emptyOb in D.objects:
        if emptyOb.type=="EMPTY":
            Empties.append(emptyOb.name)
   
#
# Make a list of track objects, with a list of associated clips
#
    for clip in D.movieclips:
        for clipob in clip.tracking.objects:
            for track in clipob.tracks:
                if track.name in Empties:
                    trackname = track.name
                    if trackname in tracks:
                        tracks[trackname].append([clip.name, clipob.name])
                    else:
                        tracks[trackname] = [[clip.name, clipob.name]]
    # print("tracks:")
    # print(tracks)
#
# for each frame, triangulate the tracks, and add keyframes to the empties
#
    for cf in range(scene.frame_start, scene.frame_end+1):
        # print (cf)
        for trackname, cliplist in tracks.items():
#            print("Frame: ", cf, " Track: ", trackname)
            ray = []
            for clip in cliplist:
                newRay = GetRayFromTrack(trackname, clip[0], clip[1], cf, scene)
#                print(newRay)
                if newRay != None:
                    ray.append(newRay)
            if len(ray) > 1:
                result = geometry.intersect_line_line(ray[0][0], ray[0][1], ray[1][0], ray[1][1])
                error = result[0]-result[1]
                errorval = math.sqrt(error[0]**2 + error[1]**2+error[2]**2)
#                print("Error: ", errorval)
                EmptyObj = D.objects[trackname]
                EmptyObj['Error'] = errorval
                EmptyObj.keyframe_insert(data_path='["Error"]', frame=(cf))
                if errorval < MaxError:
                    # print("Adding kf: ", trackname, cf)
                    EmptyLocation = 0.5*(result[0]+result[1])
                    EmptyObj.location = EmptyLocation
                    EmptyObj.keyframe_insert(data_path='location', frame=(cf))
                    TotalError += errorval
                    ErrorCount += 1
                    # print(TotalError)
                else:
                    # print("Deleting kf: ", trackname, cf)
                    EmptyObj.keyframe_delete(data_path='location', frame=(cf))
    Average = TotalError / ErrorCount
    # print("Average: ", Average)
    return Average
                    
            

class MESH_OT_triangulate(bpy.types.Operator):
    bl_idname = "animation.triangulate"
    bl_label = "Triangulate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'REGISTER', 'UNDO'}
    MaxError : FloatProperty(name="Max Error", description="Max Error", default=1.0, min=0, soft_max=100)
    AvError : FloatProperty(name="Average Error", description="Average Error", default=0.0, min=0)


    def execute(self, context):
        scene = context.scene
        self.AvError = ReadTracks(scene, self.MaxError)
        return {'FINISHED'}
        
    def draw(self,context):
        layout = self.layout
        layout.prop(self, 'MaxError')
        layout.prop(self, 'AvError')

class VIEW_3D_PT_triangulate(bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_triagulate"
    bl_label = "Triangulate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Triangulate"

    def draw(self,context):
        layout = self.layout
        layout.operator('animation.triangulate', text="Triangulate", icon='FILE_REFRESH' )
        
def menu_func_triangulate(self, context):
    self.layout.operator(MESH_OT_triangulate.bl_idname, text="Triangulate", icon='RNDCURVE')

classes = (
    MESH_OT_triangulate,
    VIEW_3D_PT_triangulate,
)

    
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.VIEW3D_MT_object.append(menu_func_triangulate)

def unregister():
    bpy.types.VIEW3D_MT_paint_weight.remove(menu_func_triangulate)
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

