import bpy
import math

bl_info = {
    "name": "GN Primitives Pack",
    "author": "olias32",
    "version": (1, 2),
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
    group_name = "GN Cylinder"
    
    # Check if the node group already exists, clear it if so
    if group_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
    group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    
    # ==========================================
    # 1. CREATE GROUP INPUT/OUTPUT INTERFACES
    # ==========================================
    group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    
    # Changed to a single "Radius" input
    r = group.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
    r.default_value, r.min_value = 1.0, 0.0
    
    h = group.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    h.default_value, h.min_value = 2.0, 0.0
    
    s = group.interface.new_socket(name="Side segments", in_out='INPUT', socket_type='NodeSocketInt')
    s.default_value, s.min_value = 32, 3
    
    hs = group.interface.new_socket(name="Height segments", in_out='INPUT', socket_type='NodeSocketInt')
    hs.default_value, hs.min_value = 1, 1
    
    cs = group.interface.new_socket(name="Cap segments", in_out='INPUT', socket_type='NodeSocketInt')
    cs.default_value, cs.min_value = 0, 0
    
    group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # ==========================================
    # 2. CREATE NODES
    # ==========================================
    nodes = group.nodes
    
    gn_in = nodes.new('NodeGroupInput')
    gn_out = nodes.new('NodeGroupOutput')
    
    # Compare Node (Greater Than 0)
    compare = nodes.new('FunctionNodeCompare')
    compare.data_type = 'INT'
    compare.operation = 'GREATER_THAN'
    compare.inputs['B'].default_value = 0 
    
    # Math Node (Maximum)
    math_max = nodes.new('ShaderNodeMath')
    math_max.operation = 'MAXIMUM'
    math_max.inputs[1].default_value = 1.0  
    
    # Top Cone (N-Gon)
    cone_ngon = nodes.new('GeometryNodeMeshCone')
    cone_ngon.fill_type = 'NGON'
    cone_ngon.inputs["Fill Segments"].default_value = 1 # Safely locked at 1
    
    # Bottom Cone (Triangles)
    cone_tri = nodes.new('GeometryNodeMeshCone')
    cone_tri.fill_type = 'TRIANGLE_FAN' 
    
    # Switch Node
    switch = nodes.new('GeometryNodeSwitch')
    switch.input_type = 'GEOMETRY'
    
    # ==========================================
    # 3. LINK THE NODES
    # ==========================================
    links = group.links
    
    # Link common inputs to BOTH cones
    for cone in [cone_tri, cone_ngon]:
        links.new(gn_in.outputs["Side segments"], cone.inputs["Vertices"])
        links.new(gn_in.outputs["Height segments"], cone.inputs["Side Segments"])
        
        # Connect the single Radius input to BOTH top and bottom sockets
        links.new(gn_in.outputs["Radius"], cone.inputs["Radius Top"])
        links.new(gn_in.outputs["Radius"], cone.inputs["Radius Bottom"])
        
        links.new(gn_in.outputs["Height"], cone.inputs["Depth"])
        
    # Cap Segments Logic Routing
    links.new(gn_in.outputs["Cap segments"], compare.inputs['A']) 
    links.new(gn_in.outputs["Cap segments"], math_max.inputs[0]) 
    
    # Maximum output goes to Triangle Fill Segments
    links.new(math_max.outputs[0], cone_tri.inputs["Fill Segments"])
    
    # Switch Logic Connections
    links.new(compare.outputs["Result"], switch.inputs["Switch"])
    links.new(cone_ngon.outputs["Mesh"], switch.inputs["False"])
    links.new(cone_tri.outputs["Mesh"], switch.inputs["True"])
    
    # Final Output
    links.new(switch.outputs["Output"], gn_out.inputs["Geometry"])
    
    # ==========================================
    # 4. BASIC NODE ARRANGEMENT (Cosmetic)
    # ==========================================
    gn_in.location = (-600, 0)
    compare.location = (-200, 300)
    math_max.location = (-200, -100)
    cone_ngon.location = (0, 200)
    cone_tri.location = (0, -200)
    switch.location = (300, 100)
    gn_out.location = (500, 100)
    
    return group

def create_gn_torus_tree():
    group = bpy.data.node_groups.new("GN Torus", 'GeometryNodeTree')
    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    rm = group.interface.new_socket("Major Radius", in_out='INPUT', socket_type='NodeSocketFloat'); rm.default_value = 2
    rn = group.interface.new_socket("Minor Radius", in_out='INPUT', socket_type='NodeSocketFloat'); rn.default_value = 0.5
    sm = group.interface.new_socket("Major Segments", in_out='INPUT', socket_type='NodeSocketInt'); sm.default_value = 32
    sn = group.interface.new_socket("Minor Segments", in_out='INPUT', socket_type='NodeSocketInt'); sn.default_value = 16
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nodes = group.nodes
    nodes.clear()
    gn_in, c1, c2, ctm, gn_out = nodes.new('NodeGroupInput'), nodes.new('GeometryNodeCurvePrimitiveCircle'), nodes.new('GeometryNodeCurvePrimitiveCircle'), nodes.new('GeometryNodeCurveToMesh'), nodes.new('NodeGroupOutput')
    group.links.new(gn_in.outputs["Major Radius"], c1.inputs["Radius"])
    group.links.new(gn_in.outputs["Major Segments"], c1.inputs["Resolution"])
    group.links.new(gn_in.outputs["Minor Radius"], c2.inputs["Radius"])
    group.links.new(gn_in.outputs["Minor Segments"], c2.inputs["Resolution"])
    group.links.new(c1.outputs[0], ctm.inputs[0])
    group.links.new(c2.outputs[0], ctm.inputs[1])
    group.links.new(ctm.outputs[0], gn_out.inputs[0])
    return group

def create_gn_tube_tree():
    group_name = "GN Tube"
    
    if group_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
    tree = bpy.data.node_groups.new(name=group_name, type='GeometryNodeTree')
    
    # ==========================================
    # 1. GROUP INPUT/OUTPUT INTERFACES
    # ==========================================
    tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    
    sock = tree.interface.new_socket(name="Outer radius", in_out='INPUT', socket_type='NodeSocketFloat')
    sock.default_value, sock.min_value = 2.0, 0.0
    
    sock = tree.interface.new_socket(name="Inner radius", in_out='INPUT', socket_type='NodeSocketFloat')
    sock.default_value, sock.min_value = 1.0, 0.0
    
    sock = tree.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    sock.default_value, sock.min_value = 2.0, 0.0
    
    sock = tree.interface.new_socket(name="Side segments", in_out='INPUT', socket_type='NodeSocketInt')
    sock.default_value, sock.min_value = 32, 3
    
    sock = tree.interface.new_socket(name="Height segments", in_out='INPUT', socket_type='NodeSocketInt')
    sock.default_value, sock.min_value = 1, 1
    
    sock = tree.interface.new_socket(name="Cap segments", in_out='INPUT', socket_type='NodeSocketInt')
    sock.default_value, sock.min_value = 1, 1
    
    tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # ==========================================
    # 2. CREATE NODES
    # ==========================================
    nodes = tree.nodes
    
    group_in = nodes.new('NodeGroupInput')
    group_out = nodes.new('NodeGroupOutput')
    
    math_max = nodes.new('ShaderNodeMath')
    math_max.operation = 'MAXIMUM'
    
    math_min = nodes.new('ShaderNodeMath')
    math_min.operation = 'MINIMUM'
    
    comb_xyz_1 = nodes.new('ShaderNodeCombineXYZ')
    comb_xyz_2 = nodes.new('ShaderNodeCombineXYZ')
    comb_xyz_3 = nodes.new('ShaderNodeCombineXYZ')
    comb_xyz_4 = nodes.new('ShaderNodeCombineXYZ')
    
    sub_1 = nodes.new('ShaderNodeMath')
    sub_1.operation = 'SUBTRACT'
    sub_1.inputs[1].default_value = 1.0
    sub_1.label = "Subtract"
    
    sub_2 = nodes.new('ShaderNodeMath')
    sub_2.operation = 'SUBTRACT'
    sub_2.inputs[1].default_value = 1.0
    sub_2.label = "Subtract"
    
    line_1 = nodes.new('GeometryNodeCurvePrimitiveLine')
    line_2 = nodes.new('GeometryNodeCurvePrimitiveLine')
    line_3 = nodes.new('GeometryNodeCurvePrimitiveLine')
    line_4 = nodes.new('GeometryNodeCurvePrimitiveLine')
    
    subdiv_1 = nodes.new('GeometryNodeSubdivideCurve')
    subdiv_2 = nodes.new('GeometryNodeSubdivideCurve')
    subdiv_3 = nodes.new('GeometryNodeSubdivideCurve')
    subdiv_4 = nodes.new('GeometryNodeSubdivideCurve')
    
    join_geom = nodes.new('GeometryNodeJoinGeometry')
    
    trans_geom = nodes.new('GeometryNodeTransform')
    trans_geom.inputs['Rotation'].default_value = (math.radians(90), 0.0, 0.0)
    
    circle = nodes.new('GeometryNodeCurvePrimitiveCircle')
    # THE FIX: A microscopic radius allows Blender to calculate outward math.
    circle.inputs['Radius'].default_value = 0.001 
    
    rev_curve = nodes.new('GeometryNodeReverseCurve')
    
    curve_to_mesh = nodes.new('GeometryNodeCurveToMesh')
    shade_smooth = nodes.new('GeometryNodeSetShadeSmooth')
    
    # ==========================================
    # 3. LINK THE NODES
    # ==========================================
    links = tree.links
    
    links.new(group_in.outputs['Outer radius'], math_max.inputs[0])
    links.new(group_in.outputs['Inner radius'], math_max.inputs[1])
    links.new(group_in.outputs['Outer radius'], math_min.inputs[0])
    links.new(group_in.outputs['Inner radius'], math_min.inputs[1])
    
    links.new(math_max.outputs[0], comb_xyz_1.inputs['X'])
    links.new(group_in.outputs['Height'], comb_xyz_1.inputs['Z'])
    links.new(math_max.outputs[0], comb_xyz_2.inputs['X']) 
    links.new(math_min.outputs[0], comb_xyz_3.inputs['X']) 
    links.new(math_min.outputs[0], comb_xyz_4.inputs['X'])
    links.new(group_in.outputs['Height'], comb_xyz_4.inputs['Z'])
    
    links.new(group_in.outputs['Height segments'], sub_1.inputs[0])
    links.new(group_in.outputs['Cap segments'], sub_2.inputs[0])
    
    links.new(comb_xyz_1.outputs[0], line_1.inputs['Start'])
    links.new(comb_xyz_2.outputs[0], line_1.inputs['End'])
    links.new(comb_xyz_2.outputs[0], line_2.inputs['Start'])
    links.new(comb_xyz_3.outputs[0], line_2.inputs['End'])
    links.new(comb_xyz_3.outputs[0], line_3.inputs['Start'])
    links.new(comb_xyz_4.outputs[0], line_3.inputs['End'])
    links.new(comb_xyz_4.outputs[0], line_4.inputs['Start'])
    links.new(comb_xyz_1.outputs[0], line_4.inputs['End'])
    
    links.new(line_1.outputs['Curve'], subdiv_1.inputs['Curve'])
    links.new(sub_1.outputs[0], subdiv_1.inputs['Cuts'])
    links.new(line_2.outputs['Curve'], subdiv_2.inputs['Curve'])
    links.new(sub_2.outputs[0], subdiv_2.inputs['Cuts'])
    links.new(line_3.outputs['Curve'], subdiv_3.inputs['Curve'])
    links.new(sub_1.outputs[0], subdiv_3.inputs['Cuts'])
    links.new(line_4.outputs['Curve'], subdiv_4.inputs['Curve'])
    links.new(sub_2.outputs[0], subdiv_4.inputs['Cuts'])
    
    links.new(subdiv_1.outputs['Curve'], join_geom.inputs['Geometry'])
    links.new(subdiv_2.outputs['Curve'], join_geom.inputs['Geometry'])
    links.new(subdiv_3.outputs['Curve'], join_geom.inputs['Geometry'])
    links.new(subdiv_4.outputs['Curve'], join_geom.inputs['Geometry'])
    
    links.new(group_in.outputs['Side segments'], circle.inputs['Resolution'])
    links.new(circle.outputs['Curve'], rev_curve.inputs['Curve'])
    links.new(join_geom.outputs['Geometry'], trans_geom.inputs['Geometry'])
    
    links.new(rev_curve.outputs['Curve'], curve_to_mesh.inputs['Curve'])
    links.new(trans_geom.outputs['Geometry'], curve_to_mesh.inputs['Profile Curve'])
    
    links.new(curve_to_mesh.outputs['Mesh'], shade_smooth.inputs['Geometry'])
    links.new(shade_smooth.outputs['Geometry'], group_out.inputs['Geometry'])

    # ==========================================
    # 4. BASIC NODE ARRANGEMENT (Cosmetic)
    # ==========================================
    group_in.location = (-800, 0)
    math_max.location = (-600, 100)
    math_min.location = (-600, -100)
    sub_1.location = (-600, -300)
    sub_2.location = (-600, -450)
    comb_xyz_1.location = (-400, 300)
    comb_xyz_2.location = (-400, 150)
    comb_xyz_3.location = (-400, 0)
    comb_xyz_4.location = (-400, -150)
    line_1.location = (-200, 300)
    line_2.location = (-200, 150)
    line_3.location = (-200, 0)
    line_4.location = (-200, -150)
    subdiv_1.location = (0, 300)
    subdiv_2.location = (0, 150)
    subdiv_3.location = (0, 0)
    subdiv_4.location = (0, -150)
    join_geom.location = (200, 150)
    trans_geom.location = (400, 0)
    circle.location = (200, 400)
    rev_curve.location = (400, 400)
    curve_to_mesh.location = (600, 300)
    shade_smooth.location = (800, 300)
    group_out.location = (1000, 300)

    return tree
    
def create_gn_cone_tree():
    group_name = "GN Cone"
    
    # Check if the node group already exists, clear it if so
    if group_name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[group_name])
        
    group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    
    # ==========================================
    # 1. CREATE GROUP INPUT/OUTPUT INTERFACES
    # ==========================================
    group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    
    rt = group.interface.new_socket(name="Radius top", in_out='INPUT', socket_type='NodeSocketFloat')
    rt.default_value, rt.min_value = 0.0, 0.0
    
    rb = group.interface.new_socket(name="Radius bottom", in_out='INPUT', socket_type='NodeSocketFloat')
    rb.default_value, rb.min_value = 1.0, 0.0
    
    h = group.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    h.default_value, h.min_value = 2.0, 0.0
    
    s = group.interface.new_socket(name="Side segments", in_out='INPUT', socket_type='NodeSocketInt')
    s.default_value, s.min_value = 32, 3
    
    hs = group.interface.new_socket(name="Height segments", in_out='INPUT', socket_type='NodeSocketInt')
    hs.default_value, hs.min_value = 1, 1
    
    cs = group.interface.new_socket(name="Cap segments", in_out='INPUT', socket_type='NodeSocketInt')
    cs.default_value, cs.min_value = 0, 0
    
    group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    
    # ==========================================
    # 2. CREATE NODES
    # ==========================================
    nodes = group.nodes
    
    gn_in = nodes.new('NodeGroupInput')
    gn_out = nodes.new('NodeGroupOutput')
    
    # Compare Node (Greater Than 0)
    compare = nodes.new('FunctionNodeCompare')
    compare.data_type = 'INT'
    compare.operation = 'GREATER_THAN'
    compare.inputs['B'].default_value = 0 
    
    # Math Node (Maximum)
    math_max = nodes.new('ShaderNodeMath')
    math_max.operation = 'MAXIMUM'
    math_max.inputs[1].default_value = 1.0  
    
    # Top Cone (N-Gon)
    cone_ngon = nodes.new('GeometryNodeMeshCone')
    cone_ngon.fill_type = 'NGON'
    cone_ngon.inputs["Fill Segments"].default_value = 1 # Safely locked at 1
    
    # Bottom Cone (Triangles)
    cone_tri = nodes.new('GeometryNodeMeshCone')
    cone_tri.fill_type = 'TRIANGLE_FAN' 
    
    # Switch Node
    switch = nodes.new('GeometryNodeSwitch')
    switch.input_type = 'GEOMETRY'
    
    # ==========================================
    # 3. LINK THE NODES
    # ==========================================
    links = group.links
    
    # Link common inputs to BOTH cones
    for cone in [cone_tri, cone_ngon]:
        links.new(gn_in.outputs["Side segments"], cone.inputs["Vertices"])
        links.new(gn_in.outputs["Height segments"], cone.inputs["Side Segments"])
        links.new(gn_in.outputs["Radius top"], cone.inputs["Radius Top"])
        links.new(gn_in.outputs["Radius bottom"], cone.inputs["Radius Bottom"])
        links.new(gn_in.outputs["Height"], cone.inputs["Depth"])
        
    # Cap Segments Logic Routing
    links.new(gn_in.outputs["Cap segments"], compare.inputs['A']) 
    links.new(gn_in.outputs["Cap segments"], math_max.inputs[0]) 
    
    # Maximum output goes to Triangle Fill Segments
    links.new(math_max.outputs[0], cone_tri.inputs["Fill Segments"])
    
    # Switch Logic Connections
    links.new(compare.outputs["Result"], switch.inputs["Switch"])
    links.new(cone_ngon.outputs["Mesh"], switch.inputs["False"])
    links.new(cone_tri.outputs["Mesh"], switch.inputs["True"])
    
    # Final Output
    links.new(switch.outputs["Output"], gn_out.inputs["Geometry"])
    
    # ==========================================
    # 4. BASIC NODE ARRANGEMENT (Cosmetic)
    # ==========================================
    gn_in.location = (-600, 0)
    compare.location = (-200, 300)
    math_max.location = (-200, -100)
    cone_ngon.location = (0, 200)
    cone_tri.location = (0, -200)
    switch.location = (300, 100)
    gn_out.location = (500, 100)
    
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

    def execute(self, context):
        lookup = {
            'PLANE': ("GN Plane", create_gn_plane_tree),
            'CUBE': ("GN Cube", create_gn_cube_tree),
            'CYLINDER': ("GN Cylinder", create_gn_cylinder_tree),
            'CONE': ("GN Cone", create_gn_cone_tree),
            'UV_SPHERE': ("GN UV Sphere", create_gn_uv_sphere_tree),
            'ICO_SPHERE': ("GN Ico Sphere", create_gn_ico_sphere_tree),
            'TORUS': ("GN Torus", create_gn_torus_tree),
            'TUBE': ("GN Tube", create_gn_tube_tree)
        }
        
        name, func = lookup[self.type]
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(obj)
        
        mod = obj.modifiers.new(name="GeometryNodes", type='NODES')
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
        items = [
            ("GN Plane", 'PLANE', 'MESH_GRID'),
            ("GN Cube", 'CUBE', 'MESH_CUBE'),
            ("GN Cylinder", 'CYLINDER', 'MESH_CYLINDER'),
            ("GN Cone", 'CONE', 'MESH_CONE'),
            ("GN UV Sphere", 'UV_SPHERE', 'SPHERE'),
            ("GN Ico Sphere", 'ICO_SPHERE', 'MESH_ICOSPHERE'),
            ("GN Torus", 'TORUS', 'MESH_TORUS'),
            ("GN Tube", 'TUBE', 'MESH_CYLINDER'),
        ]
        for text, op_type, icon_name in items:
            layout.operator("mesh.add_gn_primitive_v2", text=text, icon=icon_name).type = op_type

def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_gn_primitives_v2", icon='GEOMETRY_NODES')

classes = (MESH_OT_add_gn_primitive_v2, VIEW3D_MT_gn_primitives_v2)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_mesh_add.prepend(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    for cls in reversed(classes): bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
