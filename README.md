# Mannequin Medium Humanoid IK

**A Blender add-on for creating humanoid skeletons and setting up arm and leg IK.**

Create a base skeleton from scratch or import a compatible `Mannequin_Medium.fbx`, then add Inverse Kinematics (IK) controls for both arms and legs. The add-on validates the expected bone names and parent relationships before configuring the rig.

| At a glance | Details |
| --- | --- |
| Add-on version | 1.1.0 |
| Minimum Blender version | 4.0.0, as declared by the script |
| Category | Rigging |
| Interface | 3D Viewport → Sidebar → **Humanoid IK** |
| Script filename | `mannequin_humanoid_ik.py` |

---

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Workflows](#workflows)
- [IK controls](#ik-controls)
- [Animation and game engine export](#animation-and-game-engine-export)
- [Troubleshooting](#troubleshooting)

## Features

- **Skeleton generation** — Create a humanoid armature at the world origin using a scalable T-pose proportion template.
- **FBX import** — Import a compatible rig and validate its bone hierarchy.
- **Optional IK setup** — Configure four two-bone IK chains: left arm, right arm, left leg, and right leg.
- **Target and pole controls** — Position the wrists and ankles, and control elbow and knee bending direction.
- **Pole angle adjustment** — Apply a shared angle to the add-on's IK constraints.
- **Non-deforming controllers** — Keep the generated IK controls separate from the deform bones used for export.

## Requirements

- **Blender 4.0.0 or higher**, according to the add-on metadata. Compatibility with every later release has not been verified here.
- Save the script as **`mannequin_humanoid_ik.py`** for installation.
- For the FBX workflow, provide a file containing exactly one armature that matches the expected Mannequin Medium bone names and hierarchy.

> **Scope:** This add-on creates or imports an armature and configures IK. It does not generate a character mesh, automatically skin a mesh, or export files.

## Installation

1. Download or save the script as `mannequin_humanoid_ik.py`.
2. Open Blender and go to **Edit → Preferences → Add-ons**.
3. Use the add-on installation option to select the script. The original workflow uses **Install… → Install Add-on**; the label and location can vary by Blender version.
4. Find **Rigging: Mannequin Medium Humanoid IK** in the add-on list.
5. Enable the checkbox next to the add-on.

## Quick start

1. Move the pointer over the **3D Viewport**.
2. Press **N** to open the Sidebar.
3. Select the **Humanoid IK** tab.
4. Set the desired height and enable **Create IK controls**.
5. Click **Create skeleton from scratch**.
6. Select the armature, enter **Pose Mode**, and move the IK target bones.

> **Interface language:** The supplied script uses Portuguese labels for most settings and buttons. This README uses English descriptions, with the exact script labels shown below.

## Workflows

### 1. Create a skeleton from scratch

Use this workflow to build a base armature without an FBX file.

| Setting or action | Script label | Purpose |
| --- | --- | --- |
| Height (m) | `Altura (m)` | Scale the skeleton template; default: **1.8**. |
| Create IK controls | `Criar controles IK` | Generate IK controls during creation; disabled by default. |
| Create skeleton from scratch | `Criar ossos do zero` | Create the armature at the world origin. |

1. Set **Height (m)** to suit your character.
2. Enable **Create IK controls** if you want IK immediately.
3. Click **Create skeleton from scratch**.
4. Adjust the base skeleton to fit your character before skinning and animating.

> **Proportions:** The generated skeleton uses a modeling template. Its coordinates are not measurements taken from the original FBX, and its final height is approximate.

### 2. Import an FBX

Use this workflow when you already have a compatible Mannequin Medium rig.

1. In **Mannequin FBX**, use the file selector to locate `Mannequin_Medium.fbx`.
2. Enable **Create IK controls** if you want IK added during import.
3. Click **Import bones from FBX** (`Importar ossos do FBX`).

The add-on imports the FBX, identifies a matching armature, and checks its bone names and parent relationships. If requested, it then creates the IK controls.

> **Import behavior:** The script uses Blender's FBX importer without filtering the file to armatures only. Other objects contained in the FBX may also be imported.

### 3. Add or rebuild IK on an existing armature

1. Select a compatible armature and make it the active object.
2. Enable **Create IK controls** to reveal **Pole distance** (`Distância dos poles`) in the panel.
3. Set the desired pole distance. The default is **0.65**, used as a multiplier of the limb's reach.
4. Click **Add IK to selected armature** (`Adicionar IK ao armature selecionado`).

The armature must match the expected bone names and hierarchy. The checkbox controls automatic IK creation during generation or import; the separate **Add IK** button can be used independently.

> **Rebuilding controls:** Running **Add IK** again replaces the add-on's named target and pole bones and recreates its constraints. Set up and adjust the rig before animating those controllers.

### 4. Adjust elbow or knee twisting

If a limb bends in an unexpected direction:

1. Select the armature.
2. Adjust **IK Angle** (`Ângulo IK`).
3. Click **Apply pole target angle** (`Aplicar ângulo dos pole targets`).
4. Check the result in **Pose Mode** and repeat as needed.

The panel applies the same angle to all four IK chains. Individual adjustments can be made directly in each bone's IK constraint.

## IK controls

The add-on creates eight controller bones, parented to `root` and marked as non-deforming.

| Limb | Target bone | Pole bone |
| --- | --- | --- |
| Left arm | `IK_arm_target.l` | `IK_arm_pole.l` |
| Right arm | `IK_arm_target.r` | `IK_arm_pole.r` |
| Left leg | `IK_leg_target.l` | `IK_leg_pole.l` |
| Right leg | `IK_leg_target.r` | `IK_leg_pole.r` |

- **Targets:** Move these bones to position the wrists or ankles.
- **Poles:** Move these bones to guide the elbow or knee bending direction.

Each IK chain uses two bones with stretching disabled. The wrist and foot receive a **Mannequin IK orientation** Copy Rotation constraint, initially set to **0.0 influence**. Increase its influence manually if those bones should follow the target's rotation.

## Animation and game engine export

### Animate in Blender

Select the armature and switch to **Pose Mode**. Use **Ctrl + Tab** to access the mode switch menu, then choose Pose Mode.

Animate the target and pole bones to pose the limbs. Mesh binding and weight painting remain separate steps in your character workflow.

### Prepare animations for Unity or Unreal

IK controllers are utility bones used inside Blender. The game engine needs the resulting motion on the exported skeleton.

1. Ensure the animation is baked onto the deform skeleton, either before export or through the exporter's animation baking options.
2. Configure the export to include the character mesh and armature as needed.
3. Enable **Only Deform Bones** to exclude the add-on's non-deforming IK controllers.
4. Verify the exported hierarchy and animation in your target engine.

> **Engine setup:** The add-on does not configure Unity's Humanoid Avatar or Unreal's retargeting system. Complete and validate the engine's skeleton mapping after import.

## Troubleshooting

| Issue | What to check |
| --- | --- |
| The panel is missing | Confirm the add-on is enabled, open the 3D Viewport Sidebar with **N**, and select **Humanoid IK**. |
| The Add IK button is disabled | Make an armature the active object. |
| Pole distance is hidden | Enable **Create IK controls** to display the setting. |
| FBX import reports an incompatible rig | Check that exactly one imported armature has all expected bone names and the required parent relationships. |
| An elbow or knee twists | Adjust **IK Angle**, apply it, and inspect the pole placement in Pose Mode. |
| Rotating a target does not rotate the wrist or foot | Adjust the **Mannequin IK orientation** constraint; its influence starts at **0.0**. |

---

**Create the skeleton. Configure IK. Animate the character.**
