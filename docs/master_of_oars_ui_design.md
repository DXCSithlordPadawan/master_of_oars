# UI Design Document & Style Guide: War Galley v1.0

## 1. Visual Language
The interface follows a **"Greco-Roman Command"** aesthetic. UI components should feel like physical artifacts placed upon a tactical map.

## 2. HUD Specification
### 2.1 The Compass (Top Right)
- **Wind Indicator:** A rotating "Anemos" dial showing direction and speed.
- **Season Display:** Text indicator (e.g., "WINTER - MP REDUCED").

### 2.2 Selection Info (Bottom Left)
- **Primary:** Ship Class and Name.
- **Secondary:** Hull Integrity (Vertical Bar) and Crew Stamina (Horizontal Bar).
- **Tertiary:** Equipped specialists (e.g., "Keleustes Active").

## 3. Diegetic UI Elements
- **Command Pulse:** A circular shader expanding from the Flagship. 
- **Selection Box:** A transparent Athenian Bronze `#CD7F32` rectangle.
- **Threat Indicators:** Red chevrons appearing at the screen edge for off-screen enemies.

## 4. Components & States
| Component | Normal State | Hover State | Active/Selected |
| :--- | :--- | :--- | :--- |
| **Action Button** | Deep Ionian BG | Bronze Border | Gold Glow |
| **Unit Icon** | 80% Opacity | 100% Opacity | Highlight Outline |

## 5. Web Admin Interface
- **Layout:** Dark Mode (Slate `#0F172A`).
- **Telemetry:** Real-time line charts for Logic Engine latency.
- **Log View:** Monospace font with Syntax Highlighting for HMAC success/failure.