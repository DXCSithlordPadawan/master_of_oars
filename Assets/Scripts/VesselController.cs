using UnityEngine;

public class VesselController : MonoBehaviour
{
    public int vesselID;
    public float stamina;
    public bool isAutonomous;
    
    [Header("Visual Components")]
    public Material oarMaterial;
    public GameObject commandPulseFX;

    public void UpdateState(Vector3 newPos, float heading, float currentStamina, bool autonomous)
    {
        // Smooth interpolation of authoritative data
        transform.position = Vector3.Lerp(transform.position, newPos, Time.deltaTime * 5f);
        transform.rotation = Quaternion.Euler(0, heading, 0);
        
        stamina = currentStamina;
        isAutonomous = autonomous;

        UpdateVisuals();
    }

    private void UpdateVisuals()
    {
        // Update Oar Shader frequency based on stamina
        float oarSpeed = stamina > 30 ? 1.0f : 0.4f;
        oarMaterial.SetFloat("_RowSpeed", oarSpeed);

        // Toggle Command Pulse warning
        if (commandPulseFX != null)
            commandPulseFX.SetActive(!isAutonomous);
    }
}