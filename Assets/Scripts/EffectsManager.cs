using UnityEngine;

public class EffectsManager : MonoBehaviour
{
    public ParticleSystem oarSplashes;
    public MeshRenderer wakeRenderer;
    private VesselController controller;

    void Start()
    {
        controller = GetComponent<VesselController>();
    }

    void Update()
    {
        // 1. Scale Wake Transparency by Speed
        float speedNormalized = controller.currentSpeed / 10f; // Assume 10 is max speed
        wakeRenderer.material.SetFloat("_Transparency", Mathf.Clamp01(speedNormalized));

        // 2. Adjust Oar Splash Emission
        var emission = oarSplashes.evolution;
        if (controller.stamina > 0 && controller.currentSpeed > 0.1f)
        {
            emission.enabled = true;
            // Higher speed = more violent splashes
            var main = oarSplashes.main;
            main.startSpeed = 2.0f * speedNormalized;
        }
        else
        {
            emission.enabled = false;
        }
    }
}