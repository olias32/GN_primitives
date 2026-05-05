<h1>Non destructive primitives for Blender</h1>

<img width="1788" height="727" alt="_ (Unsaved) - Blender 5 0 0_b83W" src="https://github.com/user-attachments/assets/d8417f2e-a5b8-4b42-81f7-ad6a27d02402" />
<br />

# GN Primitives Pack

If you miss the non-destructive primitives workflow in 3D Studio Max, you can now use GN Primitives to replicate it in Blender. 

This add-on creates Geometry Nodes objects that rely on the built-in Blender Mesh Primitives, but it allows you to change the base properties—like size, radius, and the number of segments—even after the creation step.

## Installation & Usage
1. In Blender, go to **Edit > Preferences > Add-ons**, click **Install**, and select the downloaded `.zip` file.
2. Check the box next to **Add Mesh: GN Primitives Pack** to enable it.
3. The new primitives will show up in your 3D Viewport under the **Add > Mesh > GN Primitives** menu.

## Customization
If you need to change the default values for properties like radius or size, you can open the `__init__.py` script and manually modify the `default_value` and `min_value` settings within the socket declarations.
