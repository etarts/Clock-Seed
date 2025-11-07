bl_info = {
    "name": "Random Seed Generator",
    "author": "Ed Tannenbaum and Claude",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Scene Properties > Random Seed Generator",
    "description": "Generates time-based random seeds for Geometry Nodes and other uses",
    "category": "System",
}

import bpy
from datetime import datetime
from bpy.app.handlers import persistent

# Store the last captured seed to prevent re-reading the clock
_last_captured_seed = None
_last_captured_time = None


def get_time_seed():
    """Calculate an integer seed based on current time"""
    now = datetime.now()
    # Combine time components into a single integer
    # Format: HHMMSSMMM (hour, minute, second, millisecond)
    seed_value = (now.hour * 10000000 + 
                  now.minute * 100000 + 
                  now.second * 1000 + 
                  now.microsecond // 1000)
    return seed_value, now


def get_stored_seed():
    """Get the last captured seed value - don't read clock again!"""
    global _last_captured_seed
    return _last_captured_seed if _last_captured_seed is not None else 0


@persistent
def clock_animation_pre_handler(scene):
    """Handler when animation playback starts - updates dynamic seed once"""
    seed_value, now = get_time_seed()
    
    print(f"=== SEED GENERATOR: Animation started ===")
    print(f"Generated seed: {seed_value}")
    
    # Update ALL scenes, not just the current one
    for sc in bpy.data.scenes:
        sc.clock_seed = seed_value
        sc.clock_hour = now.hour
        sc.clock_minute = now.minute
        sc.clock_second = now.second
        sc.clock_millisecond = now.microsecond // 1000
        sc.update_tag()
    
    print(f"Updated {len(bpy.data.scenes)} scene(s)")


@persistent
def clock_load_handler(dummy):
    """Handler that sets seeds when file loads"""
    seed_value, now = get_time_seed()
    
    print(f"=== SEED GENERATOR: File loaded ===")
    print(f"Generated initial seed: {seed_value}")
    
    for scene in bpy.data.scenes:
        # Set static seed (won't change during session)
        scene.clock_static_seed = seed_value
        
        # Also initialize dynamic seed
        scene.clock_seed = seed_value
        scene.clock_hour = now.hour
        scene.clock_minute = now.minute
        scene.clock_second = now.second
        scene.clock_millisecond = now.microsecond // 1000
        
    print(f"====================================")


@persistent
def clock_depsgraph_update_handler(scene, depsgraph):
    """Handler that ensures seeds are initialized"""
    # Check if seeds are at default (0) and initialize them
    if scene.clock_seed == 0 or scene.clock_static_seed == 0:
        seed_value, now = get_time_seed()
        
        if scene.clock_static_seed == 0:
            scene.clock_static_seed = seed_value
        
        if scene.clock_seed == 0:
            scene.clock_seed = seed_value
            scene.clock_hour = now.hour
            scene.clock_minute = now.minute
            scene.clock_second = now.second
            scene.clock_millisecond = now.microsecond // 1000


class SEED_OT_generate_static(bpy.types.Operator):
    """Generate a new static seed value"""
    bl_idname = "seed.generate_static"
    bl_label = "Generate New Seed"
    bl_description = "Generate a new static seed based on current system time"
    
    def execute(self, context):
        global _last_captured_seed, _last_captured_time
        
        # Capture time ONCE and store it globally
        seed_value, now = get_time_seed()
        _last_captured_seed = seed_value
        _last_captured_time = now
        
        print(f"=== SEED GENERATOR: Manual generation ===")
        print(f"Generated seed: {seed_value}")
        
        # Apply the STORED value to all scenes FIRST
        for scene in bpy.data.scenes:
            scene.clock_static_seed = _last_captured_seed
            scene.update_tag()
        
        # Mark geometry nodes objects for update
        for obj in bpy.data.objects:
            if obj.modifiers:
                for mod in obj.modifiers:
                    if mod.type == 'NODES':
                        obj.update_tag()
        
        # Force driver update
        current_frame = context.scene.frame_current
        context.scene.frame_set(current_frame)
        
        print(f"=========================================")
        
        return {'FINISHED'}


class SEED_PT_panel(bpy.types.Panel):
    """Panel for random seed generator"""
    bl_label = "Random Seed Generator"
    bl_idname = "SEED_PT_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        
        # Dynamic seed section
        box = layout.box()
        box.label(text="Dynamic Seed", icon='TIME')
        
        info = box.box()
        info.scale_y = 0.8
        col = info.column(align=True)
        col.label(text="• Updates each time you play (spacebar)")
        col.label(text="• Use as driver: clock_seed")
        
        layout.separator()
        
        # Static seed section
        box = layout.box()
        box.label(text="Static Seed", icon='DECORATE_LOCKED')
        
        box.operator("seed.generate_static", icon='FILE_REFRESH')
        
        info = box.box()
        info.scale_y = 0.8
        col = info.column(align=True)
        col.label(text="• Set when file loads")
        col.label(text="• Click button to generate new")
        col.label(text="• Use as driver: clock_static_seed")
        
        layout.separator()
        
        # Instructions
        info_box = layout.box()
        info_box.label(text="Setup Instructions:", icon='HELP')
        col = info_box.column(align=True)
        col.scale_y = 0.8
        col.label(text="1. Right-click property → Add Driver")
        col.label(text="2. Type: Sum Values")
        col.label(text="3. Variable: Single Property")
        col.label(text="4. ID: Scene")
        col.label(text="5. Path: clock_seed or clock_static_seed")


def register():
    bpy.utils.register_class(SEED_OT_generate_static)
    bpy.utils.register_class(SEED_PT_panel)
    
    # Add handlers
    if clock_animation_pre_handler not in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.append(clock_animation_pre_handler)
    
    if clock_load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(clock_load_handler)
    
    if clock_depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(clock_depsgraph_update_handler)
    
    # Add properties to Scene
    bpy.types.Scene.clock_static_seed = bpy.props.IntProperty(
        name="Static Seed",
        description="Static seed set on load",
        default=0,
        options={'ANIMATABLE'}
    )
    
    bpy.types.Scene.clock_seed = bpy.props.IntProperty(
        name="Dynamic Seed",
        description="Dynamic seed that updates on play",
        default=0,
        options={'ANIMATABLE'}
    )
    
    bpy.types.Scene.clock_hour = bpy.props.IntProperty(
        name="Hour",
        default=0,
        min=0,
        max=23,
        options={'ANIMATABLE'}
    )
    
    bpy.types.Scene.clock_minute = bpy.props.IntProperty(
        name="Minute",
        default=0,
        min=0,
        max=59,
        options={'ANIMATABLE'}
    )
    
    bpy.types.Scene.clock_second = bpy.props.IntProperty(
        name="Second",
        default=0,
        min=0,
        max=59,
        options={'ANIMATABLE'}
    )
    
    bpy.types.Scene.clock_millisecond = bpy.props.IntProperty(
        name="Millisecond",
        default=0,
        min=0,
        max=999,
        options={'ANIMATABLE'}
    )


def unregister():
    # Remove handlers
    if clock_animation_pre_handler in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.remove(clock_animation_pre_handler)
    
    if clock_load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(clock_load_handler)
    
    if clock_depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(clock_depsgraph_update_handler)
    
    # Remove properties
    del bpy.types.Scene.clock_static_seed
    del bpy.types.Scene.clock_seed
    del bpy.types.Scene.clock_hour
    del bpy.types.Scene.clock_minute
    del bpy.types.Scene.clock_second
    del bpy.types.Scene.clock_millisecond
    
    bpy.utils.unregister_class(SEED_PT_panel)
    bpy.utils.unregister_class(SEED_OT_generate_static)


if __name__ == "__main__":
    register()