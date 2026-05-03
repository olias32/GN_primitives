import bpy

bl_info = {
    "name": "GN Primitives Pack",
    "author": "Gemini & User",
    "version": (1, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Add > Mesh > GN Primitives",
    "description": "Adds procedural Geometry Node primitives to the Mesh menu",
    "category": "Add Mesh",
}

# --- NODE GROUP GENERATORS ---

def create_gn_plane_tree():
    group = bpy.data.node_groups.new("GN Plane", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    for axis in ['X', 'Y']:
        s = group.interface.new_socket(f"Size {axis}", in_out='INPUT', socket_type='NodeSocketFloat')
        s.default_value, s.min_value = 2.0, 0.0
    for axis in ['X', 'Y']:
        v = group.interface.new_socket(f"Vertices {axis}", in_out='INPUT', socket_type='NodeSocketInt')
        v.default_value, v.min_value = 4, 2
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, grid, gn_out = nodes.new('NodeGroupInput'), nodes.new('GeometryNodeMeshGrid'), nodes.new('NodeGroupOutput')
    group.links.new(gn_in.outputs[1], grid.inputs[0]); group.links.new(gn_in.outputs[2], grid.inputs[1])
    group.links.new(gn_in.outputs[3], grid.inputs[2]); group.links.new(gn_in.outputs[4], grid.inputs[3])
    group.links.new(grid.outputs[0], gn_out.inputs[0])
    return group

def create_gn_cube_tree():
    group = bpy.data.node_groups.new("GN Cube", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    for axis in ['X', 'Y', 'Z']:
        s = group.interface.new_socket(f"Size {axis}", in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value, s.min_value = 2.0, 0.0
    for axis in ['X', 'Y', 'Z']:
        v = group.interface.new_socket(f"Vertices {axis}", in_out='INPUT', socket_type='NodeSocketInt'); v.default_value, v.min_value = 4, 2
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, comb, cube, gn_out = nodes.new('NodeGroupInput'), nodes.new('ShaderNodeCombineXYZ'), nodes.new('GeometryNodeMeshCube'), nodes.new('NodeGroupOutput')
    for i in range(3): group.links.new(gn_in.outputs[i+1], comb.inputs[i])
    group.links.new(comb.outputs[0], cube.inputs[0])
    for i in range(3): group.links.new(gn_in.outputs[i+4], cube.inputs[i+1])
    group.links.new(cube.outputs[0], gn_out.inputs[0])
    return group

def create_gn_cylinder_tree():
    group = bpy.data.node_groups.new("GN Cylinder", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    r = group.interface.new_socket("Radius", in_out='INPUT', socket_type='NodeSocketFloat'); r.default_value, r.min_value = 1.0, 0.0
    h = group.interface.new_socket("Height", in_out='INPUT', socket_type='NodeSocketFloat'); h.default_value, h.min_value = 2.0, 0.0
    s = group.interface.new_socket("Side segments", in_out='INPUT', socket_type='NodeSocketInt'); s.default_value, s.min_value = 32, 3
    hs = group.interface.new_socket("Height segments", in_out='INPUT', socket_type='NodeSocketInt'); hs.default_value, hs.min_value = 1, 1
    cs = group.interface.new_socket("Cap segments", in_out='INPUT', socket_type='NodeSocketInt'); cs.default_value, cs.min_value = 1, 1
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, cyl, gn_out = nodes.new('NodeGroupInput'), nodes.new('GeometryNodeMeshCylinder'), nodes.new('NodeGroupOutput')
    group.links.new(gn_in.outputs["Side segments"], cyl.inputs["Vertices"])
    group.links.new(gn_in.outputs["Height segments"], cyl.inputs["Side Segments"])
    group.links.new(gn_in.outputs["Cap segments"], cyl.inputs["Fill Segments"])
    group.links.new(gn_in.outputs["Radius"], cyl.inputs["Radius"])
    group.links.new(gn_in.outputs["Height"], cyl.inputs["Depth"])
    group.links.new(cyl.outputs[0], gn_out.inputs[0])
    return group

def create_gn_cone_tree():
    group = bpy.data.node_groups.new("GN Cone", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    rt = group.interface.new_socket("Radius top", in_out='INPUT', socket_type='NodeSocketFloat'); rt.default_value, rt.min_value = 0.0, 0.0
    rb = group.interface.new_socket("Radius bottom", in_out='INPUT', socket_type='NodeSocketFloat'); rb.default_value, rb.min_value = 1.0, 0.0
    s = group.interface.new_socket("Side segments", in_out='INPUT', socket_type='NodeSocketInt'); s.default_value, s.min_value = 32, 3
    hs = group.interface.new_socket("Height segments", in_out='INPUT', socket_type='NodeSocketInt'); hs.default_value, hs.min_value = 1, 1
    cs = group.interface.new_socket("Cap segments", in_out='INPUT', socket_type='NodeSocketInt'); cs.default_value, cs.min_value = 1, 1
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, cone, gn_out = nodes.new('NodeGroupInput'), nodes.new('GeometryNodeMeshCone'), nodes.new('NodeGroupOutput')
    group.links.new(gn_in.outputs["Side segments"], cone.inputs["Vertices"])
    group.links.new(gn_in.outputs["Height segments"], cone.inputs["Side Segments"])
    group.links.new(gn_in.outputs["Cap segments"], cone.inputs["Fill Segments"])
    group.links.new(gn_in.outputs["Radius top"], cone.inputs["Radius Top"])
    group.links.new(gn_in.outputs["Radius bottom"], cone.inputs["Radius Bottom"])
    group.links.new(cone.outputs[0], gn_out.inputs[0])
    return group

def create_gn_uv_sphere_tree():
    group = bpy.data.node_groups.new("GN UV Sphere", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    r = group.interface.new_socket("Radius", in_out='INPUT', socket_type='NodeSocketFloat'); r.default_value, r.min_value = 1.0, 0.0
    s = group.interface.new_socket("Side segments", in_out='INPUT', socket_type='NodeSocketInt'); s.default_value, s.min_value = 32, 3
    h = group.interface.new_socket("Height segments", in_out='INPUT', socket_type='NodeSocketInt'); h.default_value, h.min_value = 16, 2
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, uv, gn_out = nodes.new('NodeGroupInput'), nodes.new('GeometryNodeMeshUVSphere'), nodes.new('NodeGroupOutput')
    group.links.new(gn_in.outputs["Radius"], uv.inputs["Radius"])
    group.links.new(gn_in.outputs["Side segments"], uv.inputs["Segments"])
    group.links.new(gn_in.outputs["Height segments"], uv.inputs["Rings"])
    group.links.new(uv.outputs[0], gn_out.inputs[0])
    return group

def create_gn_ico_sphere_tree():
    group = bpy.data.node_groups.new("GN Ico Sphere", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    r = group.interface.new_socket("Radius", in_out='INPUT', socket_type='NodeSocketFloat'); r.default_value, r.min_value = 1.0, 0.0
    s = group.interface.new_socket("Subdivisions", in_out='INPUT', socket_type='NodeSocketInt'); s.default_value, s.min_value = 1, 1
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, ico, gn_out = nodes.new('NodeGroupInput'), nodes.new('GeometryNodeMeshIcoSphere'), nodes.new('NodeGroupOutput')
    group.links.new(gn_in.outputs["Radius"], ico.inputs["Radius"])
    group.links.new(gn_in.outputs["Subdivisions"], ico.inputs["Subdivisions"])
    group.links.new(ico.outputs[0], gn_out.inputs[0])
    return group

# --- OPERATOR ---

class MESH_OT_add_gn_primitive_v2(bpy.types.Operator):
    bl_idname = "mesh.add_gn_primitive_v2"
    bl_label = "Add GN Primitive"
    bl_options = {'REGISTER', 'UNDO'}
    type: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        tooltips = {
            'PLANE': "Add a procedural Plane",
            'CUBE': "Add a procedural Cube",
            'CYLINDER': "Add a procedural Cylinder",
            'CONE': "Add a procedural Cone",
            'UV_SPHERE': "Add a procedural UV Sphere",
            'ICO_SPHERE': "Add a procedural Ico Sphere"
        }
        return tooltips.get(properties.type, "Add a GN Primitive")

    def execute(self, context):
        lookup = {
            'PLANE': ("GN Plane", create_gn_plane_tree),
            'CUBE': ("GN Cube", create_gn_cube_tree),
            'CYLINDER': ("GN Cylinder", create_gn_cylinder_tree),
            'CONE': ("GN Cone", create_gn_cone_tree),
            'UV_SPHERE': ("GN UV Sphere", create_gn_uv_sphere_tree),
            'ICO_SPHERE': ("GN Ico Sphere", create_gn_ico_sphere_tree)
        }
        
        if self.type not in lookup:
            return {'CANCELLED'}
            
        name, func = lookup[self.type]
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)
        
        mod = obj.modifiers.new(name="GeometryNodes", type='NODES')
        # This double-check prevents data-block name collisions
        node_group = bpy.data.node_groups.get(name)
        if not node_group:
            node_group = func()
        mod.node_group = node_group
        
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}

# --- MENU ---

class VIEW3D_MT_gn_primitives_v2(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_gn_primitives_v2"
    bl_label = "GN Primitives"

    def draw(self, context):
        layout = self.layout
        
        # Defining items to loop through to make the code cleaner and safer
        items = [
            ("GN Plane", 'PLANE', 'MESH_GRID'),
            ("GN Cube", 'CUBE', 'MESH_CUBE'),
            ("GN Cylinder", 'CYLINDER', 'MESH_CYLINDER'),
            ("GN Cone", 'CONE', 'MESH_CONE'),
            ("GN UV Sphere", 'UV_SPHERE', 'SPHERE'),
            ("GN Ico Sphere", 'ICO_SPHERE', 'MESH_ICOSPHERE'), # Updated icon name
        ]

        for text, op_type, icon_name in items:
            try:
                layout.operator("mesh.add_gn_primitive_v2", text=text, icon=icon_name).type = op_type
            except:
                # If an icon or type fails, draw it with a default icon so the menu doesn't break
                layout.operator("mesh.add_gn_primitive_v2", text=text, icon='DOT').type = op_type

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_gn_primitives_v2", icon='GEOMETRY_NODES')



# --- REGISTRATION ---

classes = (
    MESH_OT_add_gn_primitive_v2,
    VIEW3D_MT_gn_primitives_v2,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()