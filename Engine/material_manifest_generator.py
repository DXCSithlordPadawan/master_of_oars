import os

def generate_unity_material_manifest(model_name, material_links):
    """
    Generates a YAML manifest to link FBX internal IDs to Unity Materials.
    """
    manifest_content = f"""fileFormatVersion: 2
guid: {os.urandom(16).hex()}
ModelImporter:
  externalObjects:
"""
    for mesh_name, mat_name in material_links.items():
        manifest_content += f"""    - first:
        type: UnityEngine:Material
        assembly: UnityEngine.CoreModule
        name: {mesh_name}
      second: {{fileID: 2100000, guid: {mat_name}_GUID, type: 2}}
"""
    
    manifest_content += "  userData: \n  assetBundleName: \n  assetBundleVariant: "
    
    with open(f"{model_name}.fbx.meta", "w") as f:
        f.write(manifest_content)
    print(f"[+] Created Material Manifest for {model_name}")

# Example usage for a Trireme
links = {
    "Hull_Mesh": "Aged_Oak_PBR",
    "Ram_Mesh": "Oxidized_Bronze_PBR",
    "Oar_Mesh": "Light_Ash_PBR"
}

generate_unity_material_manifest("Trireme_Hull", links)