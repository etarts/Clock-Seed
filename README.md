# Clock-Seed
Create clock based seeds for Blender

A Blender addon that generates time-based random seeds for use with Geometry Nodes and other procedural systems.

## What It Does

This addon provides two types of random seeds that can be used as drivers in Geometry Nodes (particularly useful for Random Value nodes):

- **Dynamic Seed**: Generates a new random seed each time you play the animation (spacebar)
- **Static Seed**: Generates a seed once when you open Blender, stays constant throughout your session

## Why Use This?

When working with procedural content in Geometry Nodes, you often want:
- Different random variations each time you work on your project
- Consistent results while you're tweaking parameters
- Easy way to get fresh randomization without manually changing seed values

This addon solves that problem by automatically providing time-based seeds that update when you want them to.

## Installation

1. Download the `.py` file
2. In Blender, go to Edit → Preferences → Add-ons
3. Click "Install" and select the downloaded file
4. Enable "Random Seed Generator" in the add-ons list

## Usage

### Setting Up a Driver

1. In Geometry Nodes (or any property), right-click on the Seed value → **Add Driver**
2. Open the Drivers Editor (or Graph Editor → switch to Drivers mode)
3. Configure the driver:
   - **Type**: Sum Values
   - **Variable Type**: Single Property
   - **ID**: Scene
   - **Path**: `clock_seed` (for dynamic) or `clock_static_seed` (for static)

### Using Dynamic Seed

- Press **spacebar** to play animation
- Each time you start playback, the seed updates with a new value
- Perfect for getting fresh randomization while keeping results consistent during iteration

### Using Static Seed

- Set automatically when you open your Blender file
- Click **"Generate New Seed"** button in Scene Properties to manually refresh
- Different each time you open Blender, but stays constant during your work session
- Great for procedural assets that should be unique per file but stable while editing

## Finding the Controls

Look for **"Random Seed Generator"** in the Scene Properties panel (the icon that looks like a scene/camera).

## Tips

- Use **Dynamic Seed** for variations you want to refresh frequently (testing different looks)
- Use **Static Seed** for variations you want to stay consistent (final assets)
- Both seeds work correctly with appended node groups from other blend files
- The seeds are based on system time (format: HHMMSSMMM), so they're always unique

## Technical Details

- Seeds are integer values in the format HHMMSSMMM (Hour, Minute, Second, Millisecond)
- Updates all scenes simultaneously (works with Scene.001, etc. from appending)
- Uses Blender's animation handlers for automatic updates
- No performance impact - only updates when needed

## Compatibility

- Blender 3.0 and above
- Works with Geometry Nodes, shader nodes, and any property that accepts drivers



---

Created for the Blender community. Free to use and share!