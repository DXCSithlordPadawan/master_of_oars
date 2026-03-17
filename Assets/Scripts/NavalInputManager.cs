using UnityEngine;
using System.Collections.Generic;

public class NavalInputManager : MonoBehaviour
{
    public RectTransform selectionBox;
    public LayerMask vesselLayer;
    private Vector2 startPos;
    private List<VesselController> selectedVessels = new List<VesselController>();
    private VesselBridge bridge;

    void Start()
    {
        bridge = GetComponent<VesselBridge>();
    }

    void Update()
    {
        // 1. Selection Logic (Left Mouse)
        if (Input.GetMouseButtonDown(0))
        {
            startPos = Input.mousePosition;
            ClearSelection();
        }

        if (Input.GetMouseButton(0))
        {
            UpdateSelectionBox(Input.mousePosition);
        }

        if (Input.GetMouseButtonUp(0))
        {
            ReleaseSelectionBox();
        }

        // 2. Command Logic (Right Mouse)
        if (Input.GetMouseButtonDown(1) && selectedVessels.Count > 0)
        {
            IssueMoveCommand();
        }
    }

    void UpdateSelectionBox(Vector2 curPos)
    {
        if (!selectionBox.gameObject.activeInHierarchy)
            selectionBox.gameObject.SetActive(true);

        float width = curPos.x - startPos.x;
        float height = curPos.y - startPos.y;

        selectionBox.sizeDelta = new Vector2(Mathf.Abs(width), Mathf.Abs(height));
        selectionBox.anchoredPosition = startPos + new Vector2(width / 2, height / 2);
    }

    void ReleaseSelectionBox()
    {
        selectionBox.gameObject.SetActive(false);

        Vector2 min = selectionBox.anchoredPosition - (selectionBox.sizeDelta / 2);
        Vector2 max = selectionBox.anchoredPosition + (selectionBox.sizeDelta / 2);

        foreach (var vessel in FindObjectsOfType<VesselController>())
        {
            Vector3 screenPos = Camera.main.WorldToScreenPoint(vessel.transform.position);
            if (screenPos.x > min.x && screenPos.x < max.x && screenPos.y > min.y && screenPos.y < max.y)
            {
                selectedVessels.Add(vessel);
                // Visual feedback: Highlight vessel
                vessel.GetComponent<Outline>()?.setEnabled(true);
            }
        }
    }

    void IssueMoveCommand()
    {
        Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
        if (Physics.Raycast(ray, out RaycastHit hit))
        {
            List<object> commands = new List<object>();

            foreach (var v in selectedVessels)
            {
                // Create command for the Python backend
                var cmd = new {
                    id = v.vesselID,
                    vector = new float[] { hit.point.x, hit.point.z },
                    mp_used = Vector3.Distance(v.transform.position, hit.point)
                };
                commands.Add(cmd);
            }

            // Send to Authoritative Server
            bridge.SendAction("PLAYER_ACTION", new { commands = commands }, "AUTO_GEN_SIGNATURE");
        }
    }

    void ClearSelection()
    {
        foreach (var v in selectedVessels)
        {
            v.GetComponent<Outline>()?.setEnabled(false);
        }
        selectedVessels.Clear();
    }
}