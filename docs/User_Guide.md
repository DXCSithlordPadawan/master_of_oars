# User Guide: Commanding the Fleet

## Tactical Management
1.  **Command Radius:** Keep units within the blue "Command Pulse." Units outside this range become Autonomous.
2.  **Fatigue:** Sprinting (Red Bar) provides a speed boost but permanently lowers stamina for the encounter.
3.  **National Doctrines:**
    * **Rome:** Use the Corvus to initiate boarding quickly.
    * **Egypt:** Stay at range and use Ballistae.
    * **Carthage:** Use superior MP to flank and rake oars.

## Interface
* **Lower HUD:** Movement cards and equipment triggers.
* **Mini-Map:** Shows Signal Radius and Fog of War.

## Unity Scene Setup:

Attach VesselBridge and NavalInputManager to a persistent GameManager object.

Assign the selectionBox (a UI Image with a transparent color) to the NavalInputManager reference.

Ensure all ship prefabs have a Box Collider on the vesselLayer and a VesselController script.