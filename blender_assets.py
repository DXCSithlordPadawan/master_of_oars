"""Blender asset generation script for Master of Oars / War Galley v1.0.

Run inside Blender 5.x via the Blender-MCP server or the Blender scripting panel.
Generates all game artifacts: vessels, weapons, fire proxy, environment, and
rigged character meshes. Exports each as FBX to Assets/Models/.

Historical reference for vessel proportions:
    Casson, L. — Ships and Seamanship in the Ancient World (1971).
"""
import bpy
import bmesh
import math


# ---------------------------------------------------------------------------
# S4A-01 — Scene setup
# ---------------------------------------------------------------------------

def reset_scene() -> None:
    """Remove all objects from scene and set metric units for Unity compatibility.

    Idempotent: safe to call multiple times at the start of any session.
    """
    try:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        scene = bpy.context.scene
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.length_unit = "CENTIMETERS"
        scene.unit_settings.scale_length = 0.01
        print("[+] Scene reset complete. Units: Metric / cm.")
    except Exception as e:
        print(f"[ERROR] reset_scene failed: {e}")


# ---------------------------------------------------------------------------
# S4A-02 — Vessel artifacts
# ---------------------------------------------------------------------------

def create_trireme_hull() -> None:
    """Trireme: standard Mediterranean war galley. ~37m x 6m beam.

    Historical reference: Casson (1971), Chapter 3.
    """
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        hull = bpy.context.active_object
        hull.name = "Trireme_Hull"
        hull.scale = (10, 2, 1.5)
        bpy.ops.object.transform_apply(scale=True)
        mod = hull.modifiers.new(name="Lattice", type="SIMPLE_DEFORM")
        mod.deform_method = "TAPER"
        mod.factor = -0.8

        # Ram (bronze beak at the bow)
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.5, radius2=0, depth=2, location=(11, 0, -0.5)
        )
        ram = bpy.context.active_object
        ram.name = "Trireme_Ram"
        ram.rotation_euler[1] = math.radians(90)

        print("[+] Trireme Hull Generated")
    except Exception as e:
        print(f"[ERROR] create_trireme_hull: {e}")


def create_quinquereme_hull() -> None:
    """Quinquereme: wider and longer than Trireme. Five oar banks. ~45m x 6m.

    Historical reference: Casson (1971), Chapter 5.
    """
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 40, 0))
        hull = bpy.context.active_object
        hull.name = "Quinquereme_Hull"
        hull.scale = (13, 3, 2.0)
        bpy.ops.object.transform_apply(scale=True)
        mod = hull.modifiers.new(name="Taper", type="SIMPLE_DEFORM")
        mod.deform_method = "TAPER"
        mod.factor = -0.6
        print("[+] Quinquereme Hull Generated")
    except Exception as e:
        print(f"[ERROR] create_quinquereme_hull: {e}")


def create_bireme_hull() -> None:
    """Bireme: smaller than Trireme, two oar banks. ~30m x 4m.

    Historical reference: Casson (1971), Chapter 3.
    """
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 80, 0))
        hull = bpy.context.active_object
        hull.name = "Bireme_Hull"
        hull.scale = (8, 2, 1.2)
        bpy.ops.object.transform_apply(scale=True)
        mod = hull.modifiers.new(name="Taper", type="SIMPLE_DEFORM")
        mod.deform_method = "TAPER"
        mod.factor = -0.9
        print("[+] Bireme Hull Generated")
    except Exception as e:
        print(f"[ERROR] create_bireme_hull: {e}")


def create_merchant_vessel_hull() -> None:
    """Merchant vessel: round-hulled, sail-driven. Wide beam, deep draft. ~20m x 8m.

    Historical reference: Casson (1971), Chapter 8.
    """
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 120, 0))
        hull = bpy.context.active_object
        hull.name = "MerchantVessel_Hull"
        hull.scale = (7, 4, 2.5)
        bpy.ops.object.transform_apply(scale=True)
        mod = hull.modifiers.new(name="SubSurf", type="SUBSURF")
        mod.levels = 2
        print("[+] Merchant Vessel Hull Generated")
    except Exception as e:
        print(f"[ERROR] create_merchant_vessel_hull: {e}")


def create_oar_banks(parent_name: str = "Trireme_Hull") -> None:
    """Add port and starboard oar bank placeholder meshes as children of the vessel.

    Named 'Oar_Bank_Port' and 'Oar_Bank_Starboard' for OarShader vertex targets.
    """
    try:
        parent = bpy.data.objects.get(parent_name)
        for side, offset_y in [("Port", 2.2), ("Starboard", -2.2)]:
            bpy.ops.mesh.primitive_plane_add(size=1, location=(0, offset_y, 0))
            bank = bpy.context.active_object
            bank.name = f"Oar_Bank_{side}"
            bank.scale = (9, 0.3, 0.1)
            bpy.ops.object.transform_apply(scale=True)
            if parent:
                bank.parent = parent
        print("[+] Oar Banks Generated")
    except Exception as e:
        print(f"[ERROR] create_oar_banks: {e}")


# ---------------------------------------------------------------------------
# S4A-03 — Weapons & fire artifacts
# ---------------------------------------------------------------------------

def create_corvus_bridge() -> None:
    """Corvus: Roman boarding bridge — hinged beam ~11m with a drop spike."""
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, 2))
        beam = bpy.context.active_object
        beam.name = "Corvus_Bridge"
        beam.scale = (0.8, 5.5, 0.3)
        bpy.ops.object.transform_apply(scale=True)

        bpy.ops.mesh.primitive_cone_add(
            radius1=0.2, radius2=0, depth=1.0, location=(15, 5.5, 1.5)
        )
        spike = bpy.context.active_object
        spike.name = "Corvus_Spike"
        spike.parent = beam
        print("[+] Corvus Bridge Generated")
    except Exception as e:
        print(f"[ERROR] create_corvus_bridge: {e}")


def create_ballista_frame() -> None:
    """Ballista: Egyptian/Greek torsion catapult. Frame + torsion arms."""
    try:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(30, 0, 0))
        frame = bpy.context.active_object
        frame.name = "Ballista_Frame"
        frame.scale = (1.5, 0.5, 1.0)
        bpy.ops.object.transform_apply(scale=True)

        for label, loc_x in [("L", 29), ("R", 31)]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(loc_x, 0, 1.2))
            arm = bpy.context.active_object
            arm.name = f"Ballista_Arm_{label}"
            arm.scale = (0.15, 0.15, 0.8)
            arm.parent = frame
            bpy.ops.object.transform_apply(scale=True)

        print("[+] Ballista Frame Generated")
    except Exception as e:
        print(f"[ERROR] create_ballista_frame: {e}")


def create_fire_emitter_proxy() -> None:
    """Fire emitter proxy: minimal plane mesh. Unity attaches a Particle System here."""
    try:
        bpy.ops.mesh.primitive_plane_add(size=0.5, location=(0, 0, 0))
        proxy = bpy.context.active_object
        proxy.name = "Fire_Emitter_Proxy"
        print("[+] Fire Emitter Proxy Generated")
    except Exception as e:
        print(f"[ERROR] create_fire_emitter_proxy: {e}")


# ---------------------------------------------------------------------------
# S4A-04 — Environment artifacts
# ---------------------------------------------------------------------------

def create_rock_variant(name: str, location: tuple, seed_x: float, seed_z: float) -> None:
    """Create a rock with deterministic IcoSphere distortion. Reproducible geometry."""
    try:
        bpy.ops.mesh.primitive_icosphere_add(subdivisions=3, radius=2, location=location)
        rock = bpy.context.active_object
        rock.name = name
        mesh = rock.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for v in bm.verts:
            v.co.x += math.sin(v.co.y * seed_x) * 0.4
            v.co.z += math.cos(v.co.x * seed_z) * 0.3
        bm.to_mesh(mesh)
        bm.free()
        print(f"[+] Rock Variant '{name}' Generated")
    except Exception as e:
        print(f"[ERROR] create_rock_variant '{name}': {e}")


def create_all_rock_variants() -> None:
    """Generate three distinct rock variants for obstacle variety."""
    create_rock_variant("Obstacle_Rock_A", (0, 15, 0),  seed_x=5.0, seed_z=3.0)
    create_rock_variant("Obstacle_Rock_B", (6, 15, 0),  seed_x=7.2, seed_z=2.1)
    create_rock_variant("Obstacle_Rock_C", (12, 15, 0), seed_x=3.8, seed_z=6.4)


def create_island_small() -> None:
    """Small navigable island: raised terrain mesh with coastal displacement."""
    try:
        bpy.ops.mesh.primitive_plane_add(size=20, location=(50, 50, 0))
        island = bpy.context.active_object
        island.name = "Island_Small"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=10)
        bpy.ops.object.mode_set(mode="OBJECT")
        tex = bpy.data.textures.new("IslandNoise", type="CLOUDS")
        tex.noise_scale = 2.0
        mod = island.modifiers.new(name="Displace", type="DISPLACE")
        mod.texture = tex
        mod.strength = 4.0
        print("[+] Small Island Generated")
    except Exception as e:
        print(f"[ERROR] create_island_small: {e}")


def create_reef_shallow() -> None:
    """Shallow reef: irregular plane just below sea level. Navigational hazard."""
    try:
        bpy.ops.mesh.primitive_plane_add(size=15, location=(70, 20, -0.3))
        reef = bpy.context.active_object
        reef.name = "Reef_Shallow"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=5)
        bpy.ops.object.mode_set(mode="OBJECT")
        mesh = reef.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for v in bm.verts:
            v.co.z += math.sin(v.co.x * 0.8) * 0.15
        bm.to_mesh(mesh)
        bm.free()
        print("[+] Shallow Reef Generated")
    except Exception as e:
        print(f"[ERROR] create_reef_shallow: {e}")


def create_sandbar_plane() -> None:
    """Sandbar: thin elevated plane, passable only to shallow-draft vessels."""
    try:
        bpy.ops.mesh.primitive_plane_add(size=12, location=(90, 30, 0.1))
        sandbar = bpy.context.active_object
        sandbar.name = "Sandbar_Plane"
        sandbar.scale = (1.0, 3.0, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        print("[+] Sandbar Plane Generated")
    except Exception as e:
        print(f"[ERROR] create_sandbar_plane: {e}")


def create_chain_boom() -> None:
    """Chain boom: harbour blockade — eight cylinder links across an entrance."""
    try:
        link_count = 8
        for i in range(link_count):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.3, depth=2.0, location=(i * 2.2, 100, 0)
            )
            link = bpy.context.active_object
            link.name = f"Chain_Boom_Link_{i:02d}"
            link.rotation_euler[2] = math.radians(90)
        print(f"[+] Chain Boom Generated ({link_count} links)")
    except Exception as e:
        print(f"[ERROR] create_chain_boom: {e}")


def create_terrain() -> None:
    """Generate Mediterranean seabed / island base terrain."""
    try:
        bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, -2))
        land = bpy.context.active_object
        land.name = "Mediterranean_Coast"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=20)
        bpy.ops.object.mode_set(mode="OBJECT")
        tex = bpy.data.textures.new("TerrainNoise", type="CLOUDS")
        mod = land.modifiers.new(name="Displace", type="DISPLACE")
        mod.texture = tex
        mod.strength = 3.0
        print("[+] Mediterranean Coast Terrain Generated")
    except Exception as e:
        print(f"[ERROR] create_terrain: {e}")


# ---------------------------------------------------------------------------
# S4A-05 — People artifacts with full Rigify character rigs
# ---------------------------------------------------------------------------

def _ensure_rigify_enabled() -> bool:
    """Enable the Rigify add-on if not already active. Returns True on success."""
    try:
        import addon_utils
        is_enabled, _ = addon_utils.check("rigify")
        if not is_enabled:
            bpy.ops.preferences.addon_enable(module="rigify")
            print("[+] Rigify add-on enabled")
        return True
    except Exception as e:
        print(f"[ERROR] Could not enable Rigify: {e}")
        return False


def _create_rigged_figure(
    name: str,
    location: tuple,
    height_scale: float,
    bulk_scale: float,
) -> None:
    """Create a Rigify metarig, generate the control rig, add a proxy body mesh,
    and parent with automatic weights.

    Args:
        name:         Base name for armature and mesh objects.
        location:     World-space (x, y, z) placement.
        height_scale: Vertical scale (1.0 ≈ 2m default Rigify height).
        bulk_scale:   Horizontal scale for body width.
    """
    if not _ensure_rigify_enabled():
        return
    try:
        # 1. Add human metarig
        bpy.ops.object.armature_human_metarig_add()
        metarig = bpy.context.active_object
        metarig.name = f"{name}_Metarig"
        metarig.location = location
        metarig.scale = (bulk_scale, bulk_scale, height_scale)
        bpy.ops.object.transform_apply(scale=True)

        # 2. Generate Rigify control rig from metarig
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.rigify_generate()
        bpy.ops.object.mode_set(mode="OBJECT")

        rig = bpy.context.active_object
        rig.name = f"{name}_Rig"

        # 3. Add low-poly proxy body mesh (capsule approximation)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.4 * bulk_scale,
            location=(location[0], location[1], location[2] + 0.9 * height_scale),
        )
        body = bpy.context.active_object
        body.name = f"{name}_Body"

        # 4. Parent mesh to rig with automatic weights
        bpy.ops.object.select_all(action="DESELECT")
        body.select_set(True)
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")

        print(f"[+] Rigged figure '{name}' Generated")
    except Exception as e:
        print(f"[ERROR] _create_rigged_figure '{name}': {e}")


def create_sailor_rig() -> None:
    """Sailor: standard crew member. Slim build, approx 1.75m tall."""
    _create_rigged_figure(
        name="Sailor",
        location=(100, 0, 0),
        height_scale=0.875,   # 0.875 × ~2m = ~1.75m
        bulk_scale=0.9,
    )


def create_hoplite_rig() -> None:
    """Hoplite: armoured soldier for boarding actions. Heavier build, approx 1.80m."""
    _create_rigged_figure(
        name="Hoplite",
        location=(110, 0, 0),
        height_scale=0.9,     # 0.9 × ~2m = ~1.80m
        bulk_scale=1.1,       # Broader — armour bulk
    )


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Material library — Principled BSDF, applied before export
# ---------------------------------------------------------------------------

def _make_material(
    name: str,
    base_color: tuple,
    metallic: float = 0.0,
    roughness: float = 0.5,
    specular: float = 0.5,
    emission: tuple = (0, 0, 0, 1),
    emission_strength: float = 0.0,
):
    """Create or replace a Principled BSDF material."""
    existing = bpy.data.materials.get(name)
    if existing:
        bpy.data.materials.remove(existing, do_unlink=True)
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value          = base_color
    bsdf.inputs["Metallic"].default_value            = metallic
    bsdf.inputs["Roughness"].default_value           = roughness
    bsdf.inputs["Specular IOR Level"].default_value  = specular
    bsdf.inputs["Emission Color"].default_value      = emission
    bsdf.inputs["Emission Strength"].default_value   = emission_strength
    out = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _assign(obj_name: str, mat) -> None:
    """Assign a material to a named mesh object, replacing all existing slots."""
    obj = bpy.data.objects.get(obj_name)
    if obj is None or obj.type != "MESH":
        print(f"[WARN] _assign: '{obj_name}' not found or not a mesh.")
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def apply_all_materials() -> None:
    """Create PBR materials and assign them to every game artifact."""
    # Vessels
    mat_hull    = _make_material("MAT_Hull",     (0.18, 0.11, 0.06, 1), roughness=0.85)
    mat_ram     = _make_material("MAT_Ram",      (0.55, 0.35, 0.05, 1), metallic=0.90, roughness=0.35)
    mat_oar     = _make_material("MAT_Oar",      (0.60, 0.40, 0.20, 1), roughness=0.90)
    for name in ["Trireme_Hull", "Quinquereme_Hull", "Bireme_Hull", "MerchantVessel_Hull"]:
        _assign(name, mat_hull)
    _assign("Trireme_Ram",        mat_ram)
    _assign("Oar_Bank_Port",      mat_oar)
    _assign("Oar_Bank_Starboard", mat_oar)

    # Weapons & fire
    _assign("Corvus_Bridge",    _make_material("MAT_Corvus",   (0.25, 0.15, 0.08, 1), roughness=0.88))
    _assign("Corvus_Spike",     _make_material("MAT_Spike",    (0.15, 0.14, 0.13, 1), metallic=0.95, roughness=0.50))
    _assign("Ballista_Frame",   _make_material("MAT_Ballista", (0.55, 0.42, 0.25, 1), roughness=0.80))
    mat_iron = _make_material("MAT_Iron", (0.20, 0.18, 0.16, 1), metallic=0.90, roughness=0.55)
    _assign("Ballista_Arm_L",   mat_iron)
    _assign("Ballista_Arm_R",   mat_iron)
    _assign("Fire_Emitter_Proxy", _make_material(
        "MAT_Fire", (1.0, 0.35, 0.02, 1), roughness=1.0,
        emission=(1.0, 0.35, 0.02, 1), emission_strength=5.0))

    # Environment
    mat_rock  = _make_material("MAT_Rock",  (0.22, 0.20, 0.18, 1), roughness=0.95)
    mat_chain = _make_material("MAT_Chain", (0.28, 0.14, 0.06, 1), metallic=0.85, roughness=0.75)
    for rock in ["Obstacle_Rock_A", "Obstacle_Rock_B", "Obstacle_Rock_C"]:
        _assign(rock, mat_rock)
    _assign("Island_Small",        _make_material("MAT_Island", (0.35, 0.40, 0.18, 1), roughness=0.90))
    _assign("Reef_Shallow",        _make_material("MAT_Reef",   (0.20, 0.55, 0.50, 1), roughness=0.70))
    _assign("Sandbar_Plane",       _make_material("MAT_Sand",   (0.76, 0.68, 0.45, 1), roughness=0.95))
    _assign("Mediterranean_Coast", _make_material("MAT_Coast",  (0.40, 0.32, 0.20, 1), roughness=0.92))
    for i in range(8):
        _assign(f"Chain_Boom_Link_{i:02d}", mat_chain)

    # Characters
    _assign("Sailor_Body",  _make_material("MAT_Sailor",  (0.72, 0.52, 0.38, 1), roughness=0.80))
    _assign("Hoplite_Body", _make_material("MAT_Hoplite", (0.65, 0.42, 0.10, 1), metallic=0.80, roughness=0.40))

    print("[+] All materials applied.")


# ---------------------------------------------------------------------------
# Master execution sequence (used by Blender-MCP and manual runs)
# ---------------------------------------------------------------------------

def generate_all_assets() -> None:
    """Run the full asset pipeline in dependency order."""
    reset_scene()

    # Vessels
    create_trireme_hull()
    create_oar_banks("Trireme_Hull")
    create_quinquereme_hull()
    create_bireme_hull()
    create_merchant_vessel_hull()

    # Weapons & fire
    create_corvus_bridge()
    create_ballista_frame()
    create_fire_emitter_proxy()

    # Environment
    create_all_rock_variants()
    create_island_small()
    create_reef_shallow()
    create_sandbar_plane()
    create_chain_boom()
    create_terrain()

    # People (requires Rigify)
    create_sailor_rig()
    create_hoplite_rig()

    # Apply PBR materials to everything
    apply_all_materials()

    print("[+] All assets generated with materials. Run Export_to_fbx.py to export FBX files.")


# When run directly inside Blender's scripting panel
if __name__ == "__main__":
    generate_all_assets()
