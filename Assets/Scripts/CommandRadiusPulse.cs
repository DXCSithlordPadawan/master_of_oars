using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class CommandRadiusPulse : MonoBehaviour
{
    public int segments = 50;
    public float radius = 15f;
    private LineRenderer line;

    void Start() {
        line = GetComponent<LineRenderer>();
        line.positionCount = segments + 1;
        line.useWorldSpace = false;
        CreatePoints();
    }

    void CreatePoints() {
        float angle = 20f;
        for (int i = 0; i <= segments; i++) {
            float x = Mathf.Sin(Mathf.Deg2Rad * angle) * radius;
            float z = Mathf.Cos(Mathf.Deg2Rad * angle) * radius;
            line.SetPosition(i, new Vector3(x, 0, z));
            angle += (360f / segments);
        }
    }
}