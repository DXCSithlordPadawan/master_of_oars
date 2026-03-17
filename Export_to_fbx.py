"""FBX export script for Master of Oars / War Galley v1.0.

Run inside Blender 5.x after blender_assets.py has been executed.
Exports all named game artifacts to Assets/Models/ in Unity-compatible FBX format.

Unity axis convention used throughout:
    axis_forward = '-Z', axis_up = 'Y'  (Blender 5.x — primary_axis removed)
"""
import bpy
import os

# Adjust to your local Unity project path if running outside the repo
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
EXPORT_PATH: str = os.path.join(_REPO_ROOT, "Assets", "Models")

os.makedirs(EXPORT_PATH, exist_ok=True)

# ---------------------------------------------------------------------------
# Core export helpers
# ---------------------------------------------------------------------------

def _deselect_all() -> None:
    """Deselect all objects in the scene."""
    bpy.ops.object.select_all(action="DESELECT")


def export_vessel_fbx(object_name: str) -> None:
    """Export a single mesh object (no armature) to FBX."""
    _deselect_all()
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        print(f"[WARN] Object '{object_name}' not found. Skipping.")
        return

    obj.select_set(True)
    full_path = os.path.join(EXPORT_PATH, f"{object_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=full_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        bake_space_transform=True,
        object_types={"MESH", "EMPTY"},
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        axis_forward="-Z",
        axis_up="Y",
        path_mode="COPY",      # Embed material data into FBX
        embed_textures=True,
    )
    print(f"[+] Exported: {full_path}")


def export_rigged_fbx(armature_name: str) -> None:
    """Export a rigged character (armature + skinned mesh) to FBX for Unity.

    Uses bake_anim=False — animations are added separately in Unity.
    """
    _deselect_all()
    rig  = bpy.data.objects.get(f"{armature_name}_Rig")
    body = bpy.data.objects.get(f"{armature_name}_Body")

    if rig is None or body is None:
        print(f"[WARN] Rig or body not found for '{armature_name}'. Skipping.")
        return

    rig.select_set(True)
    body.select_set(True)
    full_path = os.path.join(EXPORT_PATH, f"{armature_name}_Rig.fbx")
    bpy.ops.export_scene.fbx(
        filepath=full_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        object_types={"MESH", "ARMATURE"},
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False,       # Animations added in Unity; do not bake
        axis_forward="-Z",
        axis_up="Y",
        path_mode="COPY",      # Embed material data into FBX
        embed_textures=True,
    )
    print(f"[+] Exported rig: {full_path}")


# ---------------------------------------------------------------------------
# Full export sequence
# ---------------------------------------------------------------------------

def export_all() -> None:
    """Export every named game artifact in dependency order."""

    # --- Vessels ---
    export_vessel_fbx("Trireme_Hull")
    export_vessel_fbx("Trireme_Ram")
    export_vessel_fbx("Quinquereme_Hull")
    export_vessel_fbx("Bireme_Hull")
    export_vessel_fbx("MerchantVessel_Hull")
    export_vessel_fbx("Oar_Bank_Port")
    export_vessel_fbx("Oar_Bank_Starboard")

    # --- Weapons & fire ---
    export_vessel_fbx("Corvus_Bridge")
    export_vessel_fbx("Ballista_Frame")
    export_vessel_fbx("Fire_Emitter_Proxy")

    # --- Environment ---
    export_vessel_fbx("Obstacle_Rock_A")
    export_vessel_fbx("Obstacle_Rock_B")
    export_vessel_fbx("Obstacle_Rock_C")
    export_vessel_fbx("Island_Small")
    export_vessel_fbx("Reef_Shallow")
    export_vessel_fbx("Sandbar_Plane")
    export_vessel_fbx("Mediterranean_Coast")
    # Chain boom links exported individually
    for i in range(8):
        export_vessel_fbx(f"Chain_Boom_Link_{i:02d}")

    # --- People (rigged) ---
    export_rigged_fbx("Sailor")
    export_rigged_fbx("Hoplite")

    print(f"\n[+] All FBX files written to: {EXPORT_PATH}")


if __name__ == "__main__":
    export_all()
