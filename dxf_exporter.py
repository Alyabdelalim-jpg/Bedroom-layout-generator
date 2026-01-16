# dxf_exporter.py - UPDATED VERSION
import ezdxf
from ezdxf.enums import TextEntityAlignment
import tempfile
import os

def export_to_dxf(layout, filename=None):
    """Export complete professional layout to DXF"""
    
    try:
        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Setup professional layers
        layers = {
            'A-WALL-EXT': 8,      # External walls - Dark Grey
            'A-WALL-INT': 9,      # Internal walls - Light Grey
            'A-DOOR': 1,          # Doors - Red
            'A-WINDOW': 4,        # Windows - Cyan
            'A-FURNITURE': 3,     # Furniture - Green
            'A-FURN-BED': 30,     # Bed furniture - Dark green
            'A-FURN-STORAGE': 92, # Storage furniture - Brown
            'A-ELECTRICAL': 5,    # Electrical - Blue
            'A-LIGHTING': 40,     # Lighting - Orange
            'A-AC': 6,            # AC - Magenta
            'A-DIM': 2,           # Dimensions - Yellow
            'A-TEXT': 7,          # Text - White
            'A-ID': 1,            # IDs - Red
            'A-CENTERLINE': 1,    # Center lines - Red
            'A-HATCH': 9,         # Hatch - Grey
            'A-DOOR-SWING': 1,    # Door swing - Red
        }
        
        for layer_name, color in layers.items():
            doc.layers.new(name=layer_name, dxfattribs={'color': color})
        
        # Room dimensions
        ext_width = layout['room']['external_width']
        ext_depth = layout['room']['external_depth']
        ext_wall = layout['room']['external_wall_thickness']
        int_wall = layout['room']['internal_wall_thickness']
        int_width = layout['room']['internal_width']
        int_depth = layout['room']['internal_depth']
        
        # Draw external walls with thickness (GREY)
        # Top wall
        msp.add_lwpolyline([
            (0, ext_depth),
            (ext_width, ext_depth),
            (ext_width, ext_depth - ext_wall),
            (0, ext_depth - ext_wall),
            (0, ext_depth)
        ], dxfattribs={'layer': 'A-WALL-EXT', 'lineweight': 70})
        
        # Bottom wall
        msp.add_lwpolyline([
            (0, 0),
            (ext_width, 0),
            (ext_width, ext_wall),
            (0, ext_wall),
            (0, 0)
        ], dxfattribs={'layer': 'A-WALL-EXT', 'lineweight': 70})
        
        # Left wall
        msp.add_lwpolyline([
            (0, 0),
            (ext_wall, 0),
            (ext_wall, ext_depth),
            (0, ext_depth),
            (0, 0)
        ], dxfattribs={'layer': 'A-WALL-EXT', 'lineweight': 70})
        
        # Right wall
        msp.add_lwpolyline([
            (ext_width - ext_wall, 0),
            (ext_width, 0),
            (ext_width, ext_depth),
            (ext_width - ext_wall, ext_depth),
            (ext_width - ext_wall, 0)
        ], dxfattribs={'layer': 'A-WALL-EXT', 'lineweight': 70})
        
        # Hatch external walls (GREY)
        hatch_ext = msp.add_hatch(color=8, dxfattribs={'layer': 'A-HATCH'})
        hatch_ext.set_pattern_fill('SOLID')
        hatch_ext.paths.add_polyline_path([
            (0, ext_depth),
            (ext_width, ext_depth),
            (ext_width, ext_depth - ext_wall),
            (0, ext_depth - ext_wall)
        ], is_closed=True)
        
        # Draw internal wall (LIGHT GREY)
        walls = layout['walls']
        int_wall_data = walls['internal']
        msp.add_lwpolyline([
            (int_wall_data['x'], int_wall_data['y']),
            (int_wall_data['x'] + int_wall_data['width'], int_wall_data['y']),
            (int_wall_data['x'] + int_wall_data['width'], int_wall_data['y'] + int_wall_data['depth']),
            (int_wall_data['x'], int_wall_data['y'] + int_wall_data['depth']),
            (int_wall_data['x'], int_wall_data['y'])
        ], dxfattribs={'layer': 'A-WALL-INT', 'lineweight': 50})
        
        # Hatch internal wall (LIGHT GREY)
        hatch_int = msp.add_hatch(color=9, dxfattribs={'layer': 'A-HATCH'})
        hatch_int.set_pattern_fill('ANSI31', scale=5.0, angle=45)
        hatch_int.paths.add_polyline_path([
            (int_wall_data['x'], int_wall_data['y']),
            (int_wall_data['x'] + int_wall_data['width'], int_wall_data['y']),
            (int_wall_data['x'] + int_wall_data['width'], int_wall_data['y'] + int_wall_data['depth']),
            (int_wall_data['x'], int_wall_data['y'] + int_wall_data['depth'])
        ], is_closed=True)
        
        # Draw door with ID and swing arc
        door = layout['architectural']['door']
        
        # Door opening
        msp.add_line(
            (door['x'], ext_depth),
            (door['x'] + door['width'], ext_depth),
            dxfattribs={'layer': 'A-DOOR', 'lineweight': 50}
        )
        
        # Door swing arc (CLEAR AND VISIBLE)
        center = (door['x'], ext_depth)
        radius = door['swing_radius']
        msp.add_arc(
            center=center,
            radius=radius,
            start_angle=180,
            end_angle=270,
            dxfattribs={'layer': 'A-DOOR-SWING', 'lineweight': 35, 'linetype': 'DASHED'}
        )
        
        # Door leaf
        door_leaf_points = [
            (door['x'], ext_depth),
            (door['x'] + door['width'], ext_depth),
            (door['x'] + door['width'], ext_depth - 30),
            (door['x'], ext_depth - 30),
            (door['x'], ext_depth)
        ]
        msp.add_lwpolyline(door_leaf_points, dxfattribs={'layer': 'A-DOOR', 'lineweight': 40})
        
        # Door ID
        msp.add_text(
            door['id'],
            dxfattribs={
                'layer': 'A-ID',
                'height': 100,
                'style': 'Standard'
            }
        ).set_placement(
            (door['x'] + door['width']/2, ext_depth - 150),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Draw window with ID
        window = layout['architectural']['window']
        if window['wall'] in ['left', 'right']:
            # Vertical window
            msp.add_line(
                (window['x'], window['y']),
                (window['x'], window['y'] + window['depth']),
                dxfattribs={'layer': 'A-WINDOW', 'lineweight': 35, 'linetype': 'DASHED2'}
            )
        else:
            # Horizontal window
            msp.add_line(
                (window['x'], window['y']),
                (window['x'] + window['width'], window['y']),
                dxfattribs={'layer': 'A-WINDOW', 'lineweight': 35, 'linetype': 'DASHED2'}
            )
        
        # Window ID
        msp.add_text(
            window['id'],
            dxfattribs={
                'layer': 'A-ID',
                'height': 100,
                'style': 'Standard'
            }
        ).set_placement(
            (window['x'] + window['width']/2, window['y'] + window['depth']/2),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Draw furniture with IDs
        furniture = layout['furniture']
        
        for name, item in furniture.items():
            # Draw furniture
            points = [
                (item['x'], item['y']),
                (item['x'] + item['width'], item['y']),
                (item['x'] + item['width'], item['y'] + item['depth']),
                (item['x'], item['y'] + item['depth']),
                (item['x'], item['y'])
            ]
            
            layer = 'A-FURN-BED' if 'bed' in name else 'A-FURN-STORAGE' if name in ['wardrobe', 'tv_unit', 'dressing_table'] else 'A-FURNITURE'
            
            msp.add_lwpolyline(points, dxfattribs={'layer': layer, 'lineweight': 30})
            
            # Add ID
            center_x = item['x'] + item['width'] / 2
            center_y = item['y'] + item['depth'] / 2
            
            msp.add_text(
                item['id'],
                dxfattribs={
                    'layer': 'A-ID',
                    'height': 80,
                    'style': 'Standard'
                }
            ).set_placement(
                (center_x, center_y + 50),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
            
            # Add name
            readable_name = name.replace('_', ' ').title()
            msp.add_text(
                readable_name,
                dxfattribs={
                    'layer': 'A-TEXT',
                    'height': 120,
                    'style': 'Standard'
                }
            ).set_placement(
                (center_x, center_y),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
            
            # Add dimensions
            dim_text = f"{item['width']} x {item['depth']}"
            msp.add_text(
                dim_text,
                dxfattribs={
                    'layer': 'A-TEXT',
                    'height': 80,
                    'style': 'Standard'
                }
            ).set_placement(
                (center_x, center_y - 60),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        
        # Draw systems
        systems = layout['systems']
        
        # Electrical sockets
        for socket in systems['electrical']:
            # Simplified socket representation
            if socket['location'] == 'tv_wall':
                x = layout['furniture']['tv_unit']['x'] + layout['furniture']['tv_unit']['width'] / 2
                y = layout['furniture']['tv_unit']['y'] + 100
            elif socket['location'] == 'bedside_left' and 'bedside_table_left' in furniture:
                x = layout['furniture']['bedside_table_left']['x'] + 50
                y = layout['furniture']['bedside_table_left']['y'] + 100
            elif socket['location'] == 'bedside_right' and 'bedside_table_right' in furniture:
                x = layout['furniture']['bedside_table_right']['x'] + 50
                y = layout['furniture']['bedside_table_right']['y'] + 100
            elif socket['location'] == 'dressing_table' and 'dressing_table' in furniture:
                x = layout['furniture']['dressing_table']['x'] + 100
                y = layout['furniture']['dressing_table']['y'] + 50
            else:
                continue
            
            msp.add_circle((x, y), 25, dxfattribs={'layer': 'A-ELECTRICAL', 'lineweight': 20})
            msp.add_text(
                socket['id'],
                dxfattribs={
                    'layer': 'A-ID',
                    'height': 60,
                    'style': 'Standard'
                }
            ).set_placement(
                (x, y),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        
        # AC unit
        if systems['ac']:
            ac = systems['ac'][0]
            window = layout['architectural']['window']
            ac_x = window['x'] + window['width'] / 2
            ac_y = window['y'] + window['depth'] / 2
            
            # Adjust based on window wall
            if window['wall'] in ['top', 'bottom']:
                ac_y = window['y'] + 50
            else:
                ac_x = window['x'] + 50
            
            msp.add_lwpolyline([
                (ac_x - 100, ac_y - 25),
                (ac_x + 100, ac_y - 25),
                (ac_x + 100, ac_y + 25),
                (ac_x - 100, ac_y + 25),
                (ac_x - 100, ac_y - 25)
            ], dxfattribs={'layer': 'A-AC', 'lineweight': 40})
            
            msp.add_text(
                ac['id'],
                dxfattribs={
                    'layer': 'A-ID',
                    'height': 80,
                    'style': 'Standard'
                }
            ).set_placement(
                (ac_x, ac_y),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        
        # Add center line between bed and TV
        if 'bed' in furniture and 'tv_unit' in furniture:
            bed = layout['furniture']['bed']
            tv = layout['furniture']['tv_unit']
            bed_center_x = bed['x'] + bed['width'] / 2
            tv_center_x = tv['x'] + tv['width'] / 2
            center_x = (bed_center_x + tv_center_x) / 2
            
            msp.add_line(
                (center_x, bed['y'] + bed['depth']/2),
                (center_x, tv['y'] + tv['depth']/2),
                dxfattribs={'layer': 'A-CENTERLINE', 'lineweight': 15, 'linetype': 'CENTER'}
            )
        
        # Add dimensions
        # External dimensions
        msp.add_linear_dim(
            base=(0, -200),
            p1=(0, -200),
            p2=(ext_width, -200),
            dimstyle='EZDXF',
            dxfattribs={'layer': 'A-DIM'}
        ).set_text(f"{ext_width} mm")
        
        msp.add_linear_dim(
            base=(-200, 0),
            p1=(-200, 0),
            p2=(-200, ext_depth),
            dimstyle='EZDXF',
            dxfattribs={'layer': 'A-DIM', 'angle': 90}
        ).set_text(f"{ext_depth} mm")
        
        # Internal dimensions
        msp.add_linear_dim(
            base=(ext_wall, -300),
            p1=(ext_wall, -300),
            p2=(ext_wall + int_width, -300),
            dimstyle='EZDXF',
            dxfattribs={'layer': 'A-DIM'}
        ).set_text(f"{int_width} mm (Internal)")
        
        # Add title and project info
        metadata = layout['metadata']
        boq = layout['boq']
        
        title = f"PROFESSIONAL BEDROOM DESIGN - PROJECT {layout['room']['id']}\n"
        title += f"Internal: {int_width}x{int_depth}mm | TV: {metadata['tv_size']}\" | BOQ Total: ${boq['total_cost']}"
        
        msp.add_text(
            title,
            dxfattribs={
                'layer': 'A-TEXT',
                'height': 250,
                'style': 'Standard'
            }
        ).set_placement(
            (ext_width/2, -400),
            align=TextEntityAlignment.MIDDLE_CENTER
        )
        
        # Add AC info
        if systems['ac']:
            ac = systems['ac'][0]
            ac_info = f"AC SYSTEM:\n"
            ac_info += f"• Type: {ac['type'].title()}\n"
            ac_info += f"• Capacity: {ac['capacity_hp']} HP ({ac['capacity_btu']})"
            
            msp.add_text(
                ac_info,
                dxfattribs={
                    'layer': 'A-TEXT',
                    'height': 100,
                    'style': 'Standard'
                }
            ).set_placement(
                (ext_width/2, -550),
                align=TextEntityAlignment.MIDDLE_CENTER
            )
        
        # Save file
        if filename is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dxf')
            filename = temp_file.name
            temp_file.close()
        
        doc.saveas(filename)
        return filename
        
    except Exception as e:
        raise Exception(f"Professional DXF export failed: {str(e)}")