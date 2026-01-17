# bedroom_engine.py - COMPLETE REWRITE WITH CONSTRAINT SOLVER
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import uuid
from typing import Tuple, Optional

try:
    import plotly.graph_objects as go
except Exception:
    # Plotly is optional; Streamlit app will fall back if not installed.
    go = None

class BedroomEngine:
    def __init__(self, 
                 width=3900, 
                 depth=3600, 
                 height=3000,
                 door_from_wall=200,
                 door_width=900,
                 door_wall='top',
                 door_hinge='left',
                 door_swing='inward',
                 door_open_angle_deg=0,
                 window_wall='right',
                 window_width=1800,
                 window_sill=300,
                 internal_wall_gap=200,
                 bed_wall_preference='auto',
                 bed_type='queen',
                 wardrobe_mode='auto',
                 wardrobe_width=1800,
                 tv_unit_width=1200,
                 dressing_table_width=1200,
                 bedside_table_count=2,
                 bedside_table_width=500,
                 bedside_table_depth=400,
                 headboard_width=1600,
                 headboard_height=1000,
                 include_banquet=True,
                 banquet_width=1400,
                 banquet_depth=500,
                 ac_type='split',
                 lighting_type='recessed',
                 include_electrical=True,
                 include_lighting=True,
                 include_ac=True):
        
        # Generate unique ID for this room
        self.room_id = str(uuid.uuid4())[:8]
        
        # Room dimensions (INTERNAL dimensions provided by user)
        self.internal_width = width
        self.internal_depth = depth
        self.height = height
        
        # Wall thicknesses
        self.external_wall_thickness = 250
        self.internal_wall_thickness = 120
        
        # Calculate external dimensions
        self.external_width = width + 2 * self.external_wall_thickness
        self.external_depth = depth + 2 * self.external_wall_thickness
        
        # Door settings
        self.door_from_wall = door_from_wall
        self.door_width = door_width
        self.door_wall = door_wall
        self.door_hinge = door_hinge
        self.door_swing = door_swing
        self.door_open_angle_deg = door_open_angle_deg
        self.door_height = 2200
        
        # Window settings
        self.window_wall = window_wall
        self.window_width = window_width
        self.window_sill = window_sill
        self.window_height = 2200
        
        # Internal wall
        self.internal_wall_gap = internal_wall_gap
        self.internal_wall_depth = 600

        # Bed wall preference: 'auto' or one of ['top','bottom','left','right']
        self.bed_wall_preference = (bed_wall_preference or 'auto').lower().strip()
        
        # Furniture configuration
        self.bedside_table_count = min(bedside_table_count, 2)
        self.include_banquet = include_banquet
        # Wardrobe mode: free / enclosed / walkin_l / walkin_u / auto
        self.wardrobe_mode = wardrobe_mode
        
        # Systems
        self.ac_type = ac_type
        self.lighting_type = lighting_type
        self.include_electrical = include_electrical
        self.include_lighting = include_lighting
        self.include_ac = include_ac
        
        # Furniture dimensions based on bed type
        bed_sizes = {
            'single': {'width': 1200, 'depth': 1900},
            'double': {'width': 1400, 'depth': 1900},
            'queen': {'width': 1600, 'depth': 2000},
            'king': {'width': 1800, 'depth': 2000}
        }
        
        bed_size = bed_sizes[bed_type]
        
        # Store furniture specs
        self.bed_width = bed_size['width']
        self.bed_depth = bed_size['depth']
        self.wardrobe_width = wardrobe_width
        self.tv_unit_width = tv_unit_width
        self.dressing_table_width = dressing_table_width
        self.bedside_table_width = bedside_table_width
        self.bedside_table_depth = bedside_table_depth
        self.headboard_width = headboard_width
        self.headboard_height = headboard_height
        self.banquet_width = banquet_width
        self.banquet_depth = banquet_depth
        
        # Furniture with unique IDs
        self.furniture_specs = {
            'bed': {'id': f'FUR-{self.room_id}-001', 'width': bed_size['width'], 'depth': bed_size['depth'], 'height': 500, 'material': 'Upholstered', 'unit_cost': 1500},
            'headboard': {'id': f'FUR-{self.room_id}-002', 'width': headboard_width, 'depth': 50, 'height': headboard_height, 'material': 'Fabric', 'unit_cost': 300},
            'wardrobe': {'id': f'FUR-{self.room_id}-003', 'width': wardrobe_width, 'depth': 600, 'height': 2200, 'material': 'Engineered Wood', 'unit_cost': 800},
            'tv_unit': {'id': f'FUR-{self.room_id}-004', 'width': tv_unit_width, 'depth': 400, 'height': 500, 'material': 'MDF', 'unit_cost': 400},
            'dressing_table': {'id': f'FUR-{self.room_id}-005', 'width': dressing_table_width, 'depth': 450, 'height': 800, 'material': 'Engineered Wood', 'unit_cost': 350},
            'dressing_chair': {'id': f'FUR-{self.room_id}-006', 'width': 600, 'depth': 500, 'height': 450, 'material': 'Fabric', 'unit_cost': 250},
            'bedside_table_left': {'id': f'FUR-{self.room_id}-007', 'width': bedside_table_width, 'depth': bedside_table_depth, 'height': 600, 'material': 'Wood', 'unit_cost': 150},
            'bedside_table_right': {'id': f'FUR-{self.room_id}-008', 'width': bedside_table_width, 'depth': bedside_table_depth, 'height': 600, 'material': 'Wood', 'unit_cost': 150},
        }
        
        if include_banquet:
            self.furniture_specs['banquet'] = {'id': f'FUR-{self.room_id}-009', 'width': banquet_width, 'depth': banquet_depth, 'height': 400, 'material': 'Upholstered', 'unit_cost': 200}
        
        # Calculate optimal TV size
        self.tv_size = self.calculate_tv_size()
        
        # Clearance requirements
        self.clearances = {
            'bed_sides': 600,
            'bed_foot': 900,
            'wardrobe_doors': 900,
            'door_swing': 450,
            'circulation': 900,
            'window_clearance': 500,
            'furniture_gap': 100,
            'bedside_table_gap': 50,
            'tv_viewing_distance': self.tv_size * 25,
            'min_wall_clearance': 50,
            'wardrobe_niche_clearance': 200,  # 200mm clearance from openings
        }
        
        # Track placed furniture for collision detection
        self.placed_furniture = []
    
    def calculate_tv_size(self):
        """Calculate optimal TV size based on room dimensions"""
        room_area = (self.internal_width * self.internal_depth) / 1000000
        
        if room_area < 12:
            return 32
        elif room_area < 15:
            return 43
        elif room_area < 20:
            return 55
        else:
            return 65
    
    def calculate_ac_capacity(self):
        """Calculate AC capacity based on room area/10"""
        room_area_m2 = (self.internal_width * self.internal_depth) / 1000000
        hp_needed = room_area_m2 / 10
        
        standard_hp = [1.5, 2.25, 3, 4, 5]
        
        for hp in standard_hp:
            if hp >= hp_needed:
                return hp
        
        return 5
    
    def get_wall_info(self, wall_name):
        """Get wall information including available length and position"""
        ext_wall = self.external_wall_thickness
        
        walls = {
            'top': {
                'name': 'top',
                'start': (ext_wall, self.external_depth - ext_wall),
                'end': (ext_wall + self.internal_width, self.external_depth - ext_wall),
                'length': self.internal_width,
                'direction': 'horizontal'
            },
            'bottom': {
                'name': 'bottom',
                'start': (ext_wall, ext_wall),
                'end': (ext_wall + self.internal_width, ext_wall),
                'length': self.internal_width,
                'direction': 'horizontal'
            },
            'left': {
                'name': 'left',
                'start': (ext_wall, ext_wall),
                'end': (ext_wall, ext_wall + self.internal_depth),
                'length': self.internal_depth,
                'direction': 'vertical'
            },
            'right': {
                'name': 'right',
                'start': (ext_wall + self.internal_width, ext_wall),
                'end': (ext_wall + self.internal_width, ext_wall + self.internal_depth),
                'length': self.internal_depth,
                'direction': 'vertical'
            }
        }
        
        return walls.get(wall_name)

    # -----------------------------
    # HARD CONSTRAINT HELPERS
    # -----------------------------
    def _inner_bounds(self):
        """Inner usable rectangle (inside the inner face of external walls).
        Returns (xmin, ymin, xmax, ymax) in mm.
        """
        ext = self.external_wall_thickness
        return (ext, ext, ext + self.internal_width, ext + self.internal_depth)

    @staticmethod
    def _rects_intersect(r1, r2):
        x1, y1, w1, d1 = r1
        x2, y2, w2, d2 = r2
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + d1 <= y2 or y2 + d2 <= y1)

    @staticmethod
    def _expand_rect(r, pad):
        x, y, w, d = r
        return (x - pad, y - pad, w + 2 * pad, d + 2 * pad)

    def _rect_inside_inner(self, x, y, w, d, pad=0):
        xmin, ymin, xmax, ymax = self._inner_bounds()
        return (x >= xmin + pad and y >= ymin + pad and (x + w) <= xmax - pad and (y + d) <= ymax - pad)

    def _build_opening_keepouts(self, door, window):
        """Build conservative HARD keep-out rectangles for door + window.

        Door keep-out = swing bbox + approach rectangle (inside room).
        Window keep-out = 300mm strip inside room along window span (tall items use 600mm).
        """
        ext = self.external_wall_thickness
        xmin, ymin, xmax, ymax = self._inner_bounds()

        keepouts = []

        # Door keepouts (see constraints spec: approach=600, swing radius=door width)
        approach = 600
        swing_pad = 50

        if door['wall'] in ('top', 'bottom'):
            x0 = door['x']
            x1 = door['x'] + self.door_width
            if door['wall'] == 'top':
                y_wall = ext + self.internal_depth
                keepouts.append((x0, y_wall - approach, x1 - x0, approach))
                hinge_x = x0 if door['hinge'] == 'left' else x1
                sx0 = hinge_x if door['hinge'] == 'left' else hinge_x - self.door_width
                keepouts.append((sx0, y_wall - self.door_width, self.door_width, self.door_width))
            else:
                y_wall = ext
                keepouts.append((x0, y_wall, x1 - x0, approach))
                hinge_x = x0 if door['hinge'] == 'left' else x1
                sx0 = hinge_x if door['hinge'] == 'left' else hinge_x - self.door_width
                keepouts.append((sx0, y_wall, self.door_width, self.door_width))

        else:
            y0 = door['y']
            y1 = door['y'] + self.door_width
            if door['wall'] == 'right':
                x_wall = ext + self.internal_width
                keepouts.append((x_wall - approach, y0, approach, y1 - y0))
                hinge_y = y0 if door['hinge'] == 'left' else y1
                sy0 = hinge_y if door['hinge'] == 'left' else hinge_y - self.door_width
                keepouts.append((x_wall - self.door_width, sy0, self.door_width, self.door_width))
            else:
                x_wall = ext
                keepouts.append((x_wall, y0, approach, y1 - y0))
                hinge_y = y0 if door['hinge'] == 'left' else y1
                sy0 = hinge_y if door['hinge'] == 'left' else hinge_y - self.door_width
                keepouts.append((x_wall, sy0, self.door_width, self.door_width))

        # Window keepout (base 300mm)
        win_depth = 300
        if window['wall'] in ('top', 'bottom'):
            wx0 = window['x']
            wx1 = window['x'] + self.window_width
            if window['wall'] == 'top':
                y_wall = ext + self.internal_depth
                keepouts.append((wx0, y_wall - win_depth, wx1 - wx0, win_depth))
            else:
                y_wall = ext
                keepouts.append((wx0, y_wall, wx1 - wx0, win_depth))
        else:
            wy0 = window['y']
            wy1 = window['y'] + self.window_width
            if window['wall'] == 'right':
                x_wall = ext + self.internal_width
                keepouts.append((x_wall - win_depth, wy0, win_depth, wy1 - wy0))
            else:
                x_wall = ext
                keepouts.append((x_wall, wy0, win_depth, wy1 - wy0))

        # Clip to inner bounds and pad door swing
        clipped = []
        for r in keepouts:
            rr = self._expand_rect(r, swing_pad) if r in keepouts[:2] else r  # only pad door rects
            x, y, w, d = rr
            cx0 = max(xmin, x)
            cy0 = max(ymin, y)
            cx1 = min(xmax, x + w)
            cy1 = min(ymax, y + d)
            if cx1 > cx0 and cy1 > cy0:
                clipped.append((cx0, cy0, cx1 - cx0, cy1 - cy0))
        return clipped

    def _collides_keepouts(self, x, y, w, d, item_height=0, clearance=0):
        """Check intersection with door/window keepouts.

        For tall items (height > 1500mm), window strip depth increases to 600mm.
        """
        rect = (x, y, w, d)
        rect = self._expand_rect(rect, clearance) if clearance else rect

        for k in getattr(self, '_keepouts', []):
            # If this keepout corresponds to a window strip, optionally deepen for tall items.
            kk = k
            if item_height and item_height > 1500:
                # Heuristic: if keepout is a shallow 300mm strip along a window wall, deepen to 600.
                xk, yk, wk, dk = k
                if dk <= 350:
                    # Decide direction to deepen based on proximity to each boundary
                    xmin, ymin, xmax, ymax = self._inner_bounds()
                    # if strip touches top boundary (y+dk == ymax) deepen upward (towards ymin) by increasing dk and shifting y
                    if abs((yk + dk) - ymax) < 2:
                        kk = (xk, max(ymin, yk - 300), wk, dk + 300)
                    # touches bottom
                    elif abs(yk - ymin) < 2:
                        kk = (xk, yk, wk, dk + 300)
                    # touches right
                    elif abs((xk + wk) - xmax) < 2:
                        kk = (max(xmin, xk - 300), yk, wk + 300, dk)
                    # touches left
                    elif abs(xk - xmin) < 2:
                        kk = (xk, yk, wk + 300, dk)

            if self._rects_intersect(rect, kk):
                return True
        return False

    def _can_place_rect(self, x, y, w, d, item_height=0, clearance=0):
        """Hard check: inside inner bounds, no collision with furniture, no collision with keepouts."""
        if not self._rect_inside_inner(x, y, w, d, pad=0):
            return False
        if self._collides_keepouts(x, y, w, d, item_height=item_height, clearance=clearance):
            return False
        if self.check_collision(x, y, w, d, clearance=clearance):
            return False
        return True

    def _slide_along_wall_to_fit(self, wall_name, along, into, *, item_height=0, clearance=0, preferred_offset=None):
        """Try to place a wall-attached item by sliding it along the wall until it passes hard constraints.

        Returns (x,y,w,d,offset_used) or None.
        """
        wall = self.get_wall_info(wall_name)
        if not wall:
            return None

        # Determine feasible offset range along wall
        max_off = max(0, wall['length'] - along)

        # Build forbidden intervals from openings (buffered)
        intervals = self._opening_intervals_on_wall(wall_name)

        def ok_offset(off):
            # Does [off, off+along] overlap any forbidden interval?
            for a,b in intervals:
                if not (off + along <= a or off >= b):
                    return False
            return 0 <= off <= max_off

        # Candidate offsets: start with preferred, then expand outwards in steps
        step = 50
        start = 0 if preferred_offset is None else float(preferred_offset)
        start = max(0, min(max_off, start))

        tried=set()
        def try_off(off):
            off = max(0, min(max_off, off))
            if off in tried:
                return None
            tried.add(off)
            if not ok_offset(off):
                return None
            x,y,w,d = self.place_item_on_wall(wall_name, along, into, offset_from_start=off, center=False)
            if self._can_place_rect(x,y,w,d,item_height=item_height,clearance=clearance):
                return (x,y,w,d,off)
            return None

        # 1) preferred
        cand = try_off(start)
        if cand:
            return cand

        # 2) scan alternating left/right
        for k in range(1, int(max_off/step)+2):
            for off in (start - k*step, start + k*step):
                cand = try_off(off)
                if cand:
                    return cand

        # 3) full coarse scan (rare fallback)
        for off in range(0, int(max_off)+1, step):
            cand = try_off(off)
            if cand:
                return cand

        return None
    

    def check_collision(self, x, y, width, depth, clearance=0):
        """Check if a placement collides with already placed furniture.

        Uses conservative AABB checks with symmetric clearance.
        """
        cand = (x, y, width, depth)
        cand = self._expand_rect(cand, clearance) if clearance else cand

        for placed in self.placed_furniture:
            px, py, pw, pd = placed['x'], placed['y'], placed['width'], placed['depth']
            pr = (px, py, pw, pd)
            pr = self._expand_rect(pr, clearance) if clearance else pr
            if self._rects_intersect(cand, pr):
                return True

        return False
    
    def is_wall_available(self, wall_name, required_length, check_openings=True):
        """Check if wall has enough space and no openings"""
        wall = self.get_wall_info(wall_name)
        
        if wall['length'] < required_length:
            return False
        
        if check_openings:
            # Check if door is on this wall
            if self.door_wall == wall_name:
                return False
            
            # Check if window is on this wall
            if self.window_wall == wall_name:
                return False
        
        return True
    
    def place_on_wall(self, wall_name, width, depth, offset_from_start=None, center=False):
        """Place an axis-aligned rectangle on a wall.

        Conventions:
        - `width` is the dimension ALONG the wall.
        - `depth` is the dimension PERPENDICULAR into the room.

        This avoids the classic vertical-wall swap bug that caused wardrobes to overlap beds/doors.
        """
        wall = self.get_wall_info(wall_name)

        if wall['direction'] == 'horizontal':
            # Along wall is X
            if center:
                x = wall['start'][0] + (wall['length'] - width) / 2
            elif offset_from_start is not None:
                x = wall['start'][0] + offset_from_start
            else:
                x = wall['start'][0]

            # Perpendicular is Y
            if wall_name == 'top':
                y = wall['start'][1] - depth
            else:  # bottom
                y = wall['start'][1]

        else:
            # Along wall is Y
            if center:
                y = wall['start'][1] + (wall['length'] - width) / 2
            elif offset_from_start is not None:
                y = wall['start'][1] + offset_from_start
            else:
                y = wall['start'][1]

            # Perpendicular is X
            if wall_name == 'right':
                x = wall['start'][0] - depth
            else:  # left
                x = wall['start'][0]

        return x, y

    def place_item_on_wall(
        self,
        wall_name: str,
        along: float,
        into: float,
        offset_from_start: Optional[float] = None,
        center: bool = False,
    ) -> Tuple[float, float, float, float]:
        """Place an item on a wall and return axis-aligned rect (x,y,width,depth).

        - along: dimension ALONG the wall.
        - into:  dimension PERPENDICULAR into the room.

        Important: Layout rectangles are always axis-aligned in global XY, so for
        vertical walls we must SWAP the stored (width, depth) to (into, along).
        """
        x, y = self.place_on_wall(
            wall_name,
            width=along,
            depth=into,
            offset_from_start=offset_from_start,
            center=center,
        )

        wall = self.get_wall_info(wall_name)
        if wall["direction"] == "horizontal":
            return x, y, along, into
        return x, y, into, along
    
    def find_best_bed_wall(self):
        """
        Find the best wall for bed placement using topology rules:
        1. Avoid window wall
        2. Avoid door wall
        3. Prefer longer wall
        4. Must fit bed + bedside tables if needed
        """
        # If user forces a wall, respect it as long as it isn't the window wall
        # and has enough length to host the bed group.
        forced = self.bed_wall_preference
        if forced in ['top', 'bottom', 'left', 'right'] and forced != self.window_wall:
            wall = self.get_wall_info(forced)
            # Calculate required width for bed setup
            required_width = self.bed_width
            if self.bedside_table_count > 0:
                required_width += self.bedside_table_width * self.bedside_table_count + 100
            if wall['length'] >= required_width:
                return forced

        candidate_walls = []
        
        # Calculate required width for bed setup
        required_width = self.bed_width
        if self.bedside_table_count > 0:
            required_width += self.bedside_table_width * self.bedside_table_count + 100
        
        for wall_name in ['top', 'bottom', 'left', 'right']:
            # Skip walls with openings
            if wall_name == self.door_wall or wall_name == self.window_wall:
                continue
            
            wall = self.get_wall_info(wall_name)
            
            # Check if bed fits
            if wall['length'] >= required_width:
                # Prefer longer walls
                score = wall['length']
                candidate_walls.append((wall_name, score))
        
        if not candidate_walls:
            raise Exception("No suitable wall for bed placement")
        
        # Sort by score (prefer longer walls)
        candidate_walls.sort(key=lambda x: x[1], reverse=True)
        
        return candidate_walls[0][0]

    def _opening_intervals_on_wall(self, wall_name):
        """Return list of forbidden intervals (start,end) along a wall due to openings + buffer.
        Units: mm along the wall axis measured from wall start.
        """
        buf = self.clearances.get('wardrobe_niche_clearance', 200)
        intervals=[]

        # Door interval
        if self.door_wall == wall_name:
            a = max(0, self.door_from_wall - buf)
            b = self.door_from_wall + self.door_width + buf
            intervals.append((a,b))

        # Corner keep-out when the door is on an adjacent wall close to the corner.
        # This prevents wardrobe niches/enclosures from colliding with door zones.
        # We keep it conservative and lightweight (CAD-like behavior > perfect geometry).
        corner_limit = 1200  # mm from corner along the door wall considered "near corner"
        corner_keepout = buf + 600  # buf + wardrobe depth

        # Door on LEFT wall near BOTTOM corner -> keep-out on BOTTOM wall near LEFT corner
        if self.door_wall == 'left' and self.door_from_wall < corner_limit and wall_name == 'bottom':
            intervals.append((0, corner_keepout))
        # Door on LEFT wall near TOP corner -> keep-out on TOP wall near LEFT corner
        if self.door_wall == 'left' and (self.internal_depth - (self.door_from_wall + self.door_width)) < corner_limit and wall_name == 'top':
            intervals.append((0, corner_keepout))
        # Door on RIGHT wall near BOTTOM corner -> keep-out on BOTTOM wall near RIGHT corner
        if self.door_wall == 'right' and self.door_from_wall < corner_limit and wall_name == 'bottom':
            intervals.append((max(0, self.internal_width - corner_keepout), self.internal_width))
        # Door on RIGHT wall near TOP corner -> keep-out on TOP wall near RIGHT corner
        if self.door_wall == 'right' and (self.internal_depth - (self.door_from_wall + self.door_width)) < corner_limit and wall_name == 'top':
            intervals.append((max(0, self.internal_width - corner_keepout), self.internal_width))
        # Door on BOTTOM wall near LEFT corner -> keep-out on LEFT wall near BOTTOM corner
        if self.door_wall == 'bottom' and self.door_from_wall < corner_limit and wall_name == 'left':
            intervals.append((0, corner_keepout))
        # Door on BOTTOM wall near RIGHT corner -> keep-out on RIGHT wall near BOTTOM corner
        if self.door_wall == 'bottom' and (self.internal_width - (self.door_from_wall + self.door_width)) < corner_limit and wall_name == 'right':
            intervals.append((0, corner_keepout))
        # Door on TOP wall near LEFT corner -> keep-out on LEFT wall near TOP corner
        if self.door_wall == 'top' and self.door_from_wall < corner_limit and wall_name == 'left':
            intervals.append((max(0, self.internal_depth - corner_keepout), self.internal_depth))
        # Door on TOP wall near RIGHT corner -> keep-out on RIGHT wall near TOP corner
        if self.door_wall == 'top' and (self.internal_width - (self.door_from_wall + self.door_width)) < corner_limit and wall_name == 'right':
            intervals.append((max(0, self.internal_depth - corner_keepout), self.internal_depth))

        # Window interval (treat as keep-clear too if ever used)
        if self.window_wall == wall_name:
            # centered window
            wall = self.get_wall_info(wall_name)
            win_start = (wall['length'] - self.window_width)/2
            a = max(0, win_start - buf)
            b = win_start + self.window_width + buf
            intervals.append((a,b))

        # Merge overlaps
        if not intervals:
            return []
        intervals.sort()
        merged=[intervals[0]]
        for a,b in intervals[1:]:
            la,lb=merged[-1]
            if a<=lb:
                merged[-1]=(la,max(lb,b))
            else:
                merged.append((a,b))
        return merged

    def _largest_free_segment(self, wall_name, required_length):
        """Pick a placement segment along wall that avoids openings; returns offset_from_start or None.
        Strategy: choose the largest free segment that can host required_length, and center within it.
        """
        wall=self.get_wall_info(wall_name)
        intervals=self._opening_intervals_on_wall(wall_name)
        # Compute free segments
        free=[]
        cur=0
        for a,b in intervals:
            if a-cur>0:
                free.append((cur,a))
            cur=max(cur,b)
        if wall['length']-cur>0:
            free.append((cur,wall['length']))

        # Filter by size
        candidates=[seg for seg in free if (seg[1]-seg[0])>=required_length]
        if not candidates:
            return None
        # Largest then earliest
        candidates.sort(key=lambda s:(s[1]-s[0],-s[0]), reverse=True)
        a,b=candidates[0]
        return a + (b-a-required_length)/2

    def _rect_distance(self, r1, r2):
        """Axis-aligned min distance between rectangles (0 if intersect).
        Each rect: (x,y,w,d).
        """
        x1,y1,w1,d1=r1
        x2,y2,w2,d2=r2
        dx=max(x2-(x1+w1), x1-(x2+w2), 0)
        dy=max(y2-(y1+d1), y1-(y2+d2), 0)
        return (dx**2+dy**2)**0.5

    def _recommended_tv_center_z(self) -> float:
        """Simple mounting rule-of-thumb.

        TV center close to seated eye level (~1050mm), adjusted slightly with viewing distance.
        Clamped to a conservative range so it never floats near the ceiling.
        """
        vd = float(self.clearances.get('tv_viewing_distance', 2000))
        # Baseline: 1050mm at ~2m; add 25mm per extra 500mm viewing distance
        center = 1050.0 + 25.0 * max(0.0, (vd - 2000.0) / 500.0)
        return float(max(950.0, min(1200.0, center)))

    def resolve_wardrobe_mode(self):
        """Resolve wardrobe mode from user choice and room size thresholds.

        Modes: 'free', 'enclosed', 'walkin_l', 'walkin_u', 'auto'.
        Auto rules (user confirmed):
          - U-shape if both dimensions >= 5200mm
          - L-shape if max dimension >= 4500mm
          - Else enclosed straight
        """
        mode = (self.wardrobe_mode or 'auto').lower().strip()
        if mode in ('free', 'enclosed', 'walkin_l', 'walkin_u'):
            return mode
        w, d = self.internal_width, self.internal_depth
        if w >= 5200 and d >= 5200:
            return 'walkin_u'
        if max(w, d) >= 4500:
            return 'walkin_l'
        return 'enclosed'

    def _walkin_aisle_depth(self, prefer=900, tight=750):
        """Return aisle depth for walk-in closets.

        Default 900mm. If room is tight (bed+group cannot fit), use 750mm.
        """
        # Heuristic: if clear depth after bed and tv zone is too small, drop to tight.
        # We keep it simple: if min(internal_width, internal_depth) < 3600, consider tight.
        if min(self.internal_width, self.internal_depth) < 3600:
            return tight
        return prefer

    
    def find_best_wardrobe_wall(self, bed_wall):
        """
        Find best wall for wardrobe using topology rules:
        1. Must not face bed directly
        2. Must not be on window wall
        3. Must not be on door wall (if possible)
        4. Must have space for built-in niche (600mm depth)
        5. Must have 200mm clearance from openings
        """
        candidate_walls = []
        
        # Opposite walls
        opposite = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }
        
        bed_opposite = opposite[bed_wall]
        
        for wall_name in ['top', 'bottom', 'left', 'right']:
            # Critical rule: wardrobe can NEVER be on the same wall as the bed.
            # Otherwise it can overlap the anchored bed group.
            if wall_name == bed_wall:
                continue
            # Rule 1: Don't face bed
            if wall_name == bed_opposite:
                continue
            
            # Rule 2: Not on window wall
            if wall_name == self.window_wall:
                continue
            
            # Check if wall has enough length
            wall = self.get_wall_info(wall_name)
            required_length = self.wardrobe_width + 2 * self.clearances['wardrobe_niche_clearance']
            
            if wall['length'] >= required_length:
                # Strongly avoid the door wall for wardrobe placement.
                score = 100 if wall_name != self.door_wall else -1000
                candidate_walls.append((wall_name, score))
        
        if not candidate_walls:
            raise Exception("No suitable wall for wardrobe placement")
        
        candidate_walls.sort(key=lambda x: x[1], reverse=True)
        
        return candidate_walls[0][0]


    def calculate_layout(self, dressing_table_side='right'):
        """Calculate complete layout with constraint solver"""
        
        validation_issues = []
        self.placed_furniture = []
        
        ext_wall = self.external_wall_thickness
        
        # 1. WALLS
        walls = {
            'external': {
                'top': {'x': 0, 'y': self.external_depth - ext_wall, 'width': self.external_width, 'depth': ext_wall, 'thickness': ext_wall},
                'bottom': {'x': 0, 'y': 0, 'width': self.external_width, 'depth': ext_wall, 'thickness': ext_wall},
                'left': {'x': 0, 'y': 0, 'width': ext_wall, 'depth': self.external_depth, 'thickness': ext_wall},
                'right': {'x': self.external_width - ext_wall, 'y': 0, 'width': ext_wall, 'depth': self.external_depth, 'thickness': ext_wall}
            },
            'internal': None  # Will be calculated based on bed wall
        }
        
        # 2. DOOR - Place on user-specified wall
        door_wall_info = self.get_wall_info(self.door_wall)
        
        if self.door_wall in ['top', 'bottom']:
            door_x = ext_wall + max(0, min(self.door_from_wall, self.internal_width - self.door_width))
            door_y = ext_wall + self.internal_depth if self.door_wall == 'top' else ext_wall
            door = {
                'id': f'DOOR-{self.room_id}-001',
                'x': door_x,
                'y': door_y,
                'width': self.door_width,
                'depth': 50,
                'wall': self.door_wall,
                'hinge': self.door_hinge,
                'swing': self.door_swing,
                'swing_radius': self.door_width,
                'open_angle': self.door_open_angle_deg
            }
        else:
            door_y = ext_wall + max(0, min(self.door_from_wall, self.internal_depth - self.door_width))
            door_x = ext_wall + self.internal_width if self.door_wall == 'right' else ext_wall
            door = {
                'id': f'DOOR-{self.room_id}-001',
                'x': door_x,
                'y': door_y,
                'width': 50,
                'depth': self.door_width,
                'wall': self.door_wall,
                'hinge': self.door_hinge,
                'swing': self.door_swing,
                'swing_radius': self.door_width,
                'open_angle': self.door_open_angle_deg
            }
        
        # 3. WINDOW - Place on user-specified wall
        window_wall_info = self.get_wall_info(self.window_wall)
        
        if self.window_wall in ['top', 'bottom']:
            window_x = ext_wall + (self.internal_width - self.window_width) / 2
            window_y = ext_wall + self.internal_depth if self.window_wall == 'top' else ext_wall
            window = {
                'id': f'WIN-{self.room_id}-001',
                'x': window_x,
                'y': window_y,
                'width': self.window_width,
                'depth': 50,
                'wall': self.window_wall,
                'sill_height': self.window_sill
            }
        else:
            window_y = ext_wall + (self.internal_depth - self.window_width) / 2
            window_x = ext_wall + self.internal_width if self.window_wall == 'right' else ext_wall
            window = {
                'id': f'WIN-{self.room_id}-001',
                'x': window_x,
                'y': window_y,
                'width': 50,
                'depth': self.window_width,
                'wall': self.window_wall,
                'sill_height': self.window_sill
            }
        
        # 3.5 OPENING KEEP-OUT ZONES (HARD)
        # Conservative rectangles used to prevent furniture overlapping doors/windows.
        self._keepouts = self._build_opening_keepouts(door, window)

        # 4. BED + BEDSIDE GROUP (HARD FIT)
        bed_wall = self.find_best_bed_wall()

        # If the bed group is tight, shrink bedside width but never delete tables.
        bst_count = max(0, min(int(self.bedside_table_count), 2))
        bst_w = int(self.bedside_table_width) if bst_count else 0
        bst_d = int(self.bedside_table_depth) if bst_count else 0

        if bst_count:
            wall = self.get_wall_info(bed_wall)
            margin = 100
            needed = self.bed_width + (bst_w * bst_count)
            if wall['length'] < needed + margin:
                avail = max(0.0, wall['length'] - self.bed_width - margin)
                bst_w = int(max(350.0, avail / bst_count))
                self.bedside_table_width = bst_w
                self.furniture_specs['bedside_table_left']['width'] = bst_w
                self.furniture_specs['bedside_table_right']['width'] = bst_w

        group_along = self.bed_width + (bst_w * bst_count)

        # Place the whole bed-group first so nothing can drift out of bounds or into openings.
        grp_x, grp_y, grp_w, grp_d = self._slide_along_wall_to_fit(
            bed_wall,
            group_along,
            self.bed_depth,
            item_height=self.furniture_specs['bed'].get('height', 0),
            clearance=0,
            preferred_offset=None,
        )

        # Derive bed placement inside the group (tables touch bed with no gap by design).
        if bed_wall in ('top', 'bottom'):
            bed_x = grp_x + (bst_w if bst_count else 0)
            bed_y = grp_y
            bed_w, bed_d = self.bed_width, self.bed_depth
        else:
            bed_x = grp_x
            bed_y = grp_y + (bst_w if bst_count else 0)
            bed_w, bed_d = self.bed_depth, self.bed_width  # swapped by global axis alignment

        bed_data = {
            **self.furniture_specs['bed'],
            'x': bed_x,
            'y': bed_y,
            'width': bed_w,
            'depth': bed_d,
            'wall': bed_wall
        }
        self.placed_furniture.append(bed_data)

        # 5. HEADBOARD - Same wall as bed; align to bed center; never overlaps keepouts.
        if bed_wall in ('top', 'bottom'):
            bed_center = bed_x + bed_w / 2
            hb_off = max(0.0, bed_center - self.headboard_width / 2 - self.external_wall_thickness)
            headboard_x, headboard_y, headboard_w, headboard_d = self._slide_along_wall_to_fit(
                bed_wall,
                self.headboard_width,
                50,
                item_height=self.furniture_specs['headboard'].get('height', 0),
                clearance=0,
                preferred_offset=hb_off,
            )
        else:
            bed_center = bed_y + bed_d / 2
            hb_off = max(0.0, bed_center - self.headboard_width / 2 - self.external_wall_thickness)
            headboard_x, headboard_y, headboard_w, headboard_d = self._slide_along_wall_to_fit(
                bed_wall,
                self.headboard_width,
                50,
                item_height=self.furniture_specs['headboard'].get('height', 0),
                clearance=0,
                preferred_offset=hb_off,
            )

        headboard_data = {
            **self.furniture_specs['headboard'],
            'x': headboard_x,
            'y': headboard_y,
            'width': headboard_w,
            'depth': headboard_d,
            'wall': bed_wall
        }

        # 5.5 Package initial furniture
        furniture = {'bed': bed_data, 'headboard': headboard_data}
# 6. BEDSIDE TABLES (RIGID GROUP; NEVER OVERLAP OR PENETRATE)
        if bst_count >= 1:
            if bed_wall in ('top', 'bottom'):
                # Left table
                bst_left_x = grp_x
                bst_left_y = bed_y
                bst_left_w = bst_w
                bst_left_d = bst_d
            else:
                # Vertical wall: into-room is X (bst_d), along-wall is Y (bst_w)
                bst_left_x = bed_x
                bst_left_y = grp_y
                bst_left_w = bst_d
                bst_left_d = bst_w

            if self._can_place_rect(bst_left_x, bst_left_y, bst_left_w, bst_left_d, item_height=self.furniture_specs['bedside_table_left'].get('height',0), clearance=0):
                bst_left_data = {
                    **self.furniture_specs['bedside_table_left'],
                    'x': bst_left_x,
                    'y': bst_left_y,
                    'width': bst_left_w,
                    'depth': bst_left_d,
                    'wall': bed_wall
                }
                furniture['bedside_table_left'] = bst_left_data
                self.placed_furniture.append(bst_left_data)
            else:
                validation_issues.append('Bedside table (left) could not be placed without violating HARD constraints.')

        if bst_count >= 2:
            if bed_wall in ('top', 'bottom'):
                bst_right_x = bed_x + bed_w
                bst_right_y = bed_y
                bst_right_w = bst_w
                bst_right_d = bst_d
            else:
                bst_right_x = bed_x
                bst_right_y = bed_y + bed_d
                bst_right_w = bst_d
                bst_right_d = bst_w

            if self._can_place_rect(bst_right_x, bst_right_y, bst_right_w, bst_right_d, item_height=self.furniture_specs['bedside_table_right'].get('height',0), clearance=0):
                bst_right_data = {
                    **self.furniture_specs['bedside_table_right'],
                    'x': bst_right_x,
                    'y': bst_right_y,
                    'width': bst_right_w,
                    'depth': bst_right_d,
                    'wall': bed_wall
                }
                furniture['bedside_table_right'] = bst_right_data
                self.placed_furniture.append(bst_right_data)
            else:
                validation_issues.append('Bedside table (right) could not be placed without violating HARD constraints.')

        # 7. WARDROBE OPTIONS (explicit user mode + auto thresholds)
        mode = self.resolve_wardrobe_mode()
        wardrobe_is_enclosed = mode in ('enclosed', 'walkin_l', 'walkin_u')
        wardrobe_is_walkin = mode in ('walkin_l', 'walkin_u')
        walkin_aisle = self._walkin_aisle_depth(prefer=900, tight=750) if wardrobe_is_walkin else 0
        walkin_band = 600 + walkin_aisle if wardrobe_is_walkin else 0  # wardrobe depth + aisle

        # 7. WARDROBE (never deleted; may be shrunk/repositioned)
        wardrobe_wall = self.find_best_wardrobe_wall(bed_wall)

        # Pick a placement segment that avoids door/window zones on the wardrobe wall
        required_len = self.wardrobe_width
        off = self._largest_free_segment(wardrobe_wall, required_len)
        if off is None:
            # If the wardrobe wall has an opening and no segment fits, fall back to a wall without openings
            for alt in ['top','bottom','left','right']:
                if alt in (self.window_wall,):
                    continue
                if alt == {'top':'bottom','bottom':'top','left':'right','right':'left'}[bed_wall]:
                    continue
                off = self._largest_free_segment(alt, required_len)
                if off is not None:
                    wardrobe_wall = alt
                    break

        # If we still couldn't find a segment on the chosen wall, SHRINK the wardrobe to fit the largest free segment.
        if off is None:
            wall = self.get_wall_info(wardrobe_wall)
            intervals = self._opening_intervals_on_wall(wardrobe_wall)
            # compute free segments
            free = []
            cur = 0
            for a, b in intervals:
                if a - cur > 0:
                    free.append((cur, a))
                cur = max(cur, b)
            if wall['length'] - cur > 0:
                free.append((cur, wall['length']))

            if free:
                free.sort(key=lambda s: s[1] - s[0], reverse=True)
                a, b = free[0]
                max_len = b - a
                if max_len >= 800:  # minimum viable wardrobe
                    required_len = min(required_len, max_len)
                    self.wardrobe_width = int(required_len)
                    self.furniture_specs['wardrobe']['width'] = int(required_len)
                    off = a + (max_len - required_len) / 2

        wardrobe_x, wardrobe_y, wardrobe_w, wardrobe_d = self._slide_along_wall_to_fit(
            wardrobe_wall,
            self.wardrobe_width,
            600,
            item_height=self.furniture_specs['wardrobe'].get('height', 0),
            clearance=0,
            preferred_offset=off,
        )

        wardrobe_data = {
            **self.furniture_specs['wardrobe'],
            'x': wardrobe_x,
            'y': wardrobe_y,
            'width': wardrobe_w,
            'depth': wardrobe_d,
            'wall': wardrobe_wall
        }
        furniture['wardrobe'] = wardrobe_data
        self.placed_furniture.append(wardrobe_data)

        # --- HARD FIXES ---
        # (A) Wardrobe must never clash with the door keep-out zone.
        # If it does (can happen when only one wall is viable), re-position within the
        # largest available segment away from the door interval.
        def _rects_intersect(r1, r2):
            x1,y1,w1,d1=r1; x2,y2,w2,d2=r2
            return not (x1+w1 <= x2 or x2+w2 <= x1 or y1+d1 <= y2 or y2+d2 <= y1)

        door_rect = None
        if wardrobe_wall == self.door_wall:
            # Door rectangle in internal coordinates (including ext wall offset)
            if self.door_wall in ['top','bottom']:
                door_rect = (door['x'], door['y']-self.external_wall_thickness, self.door_width, self.external_wall_thickness)
            else:
                door_rect = (door['x']-self.external_wall_thickness, door['y'], self.external_wall_thickness, self.door_width)

        if door_rect is not None:
            wr = (wardrobe_x, wardrobe_y, wardrobe_w, wardrobe_d)
            # Expand door keepout by 200mm in all directions
            dx,dy,dw,dd = door_rect
            keep = (dx-200, dy-200, dw+400, dd+400)
            if _rects_intersect(wr, keep):
                wall = self.get_wall_info(wardrobe_wall)
                free = []
                cur = 0
                for a,b in self._opening_intervals_on_wall(wardrobe_wall):
                    if a - cur > 0:
                        free.append((cur,a))
                    cur = max(cur,b)
                if wall['length'] - cur > 0:
                    free.append((cur, wall['length']))

                # choose placement that maximizes distance from the door interval center
                if free:
                    # door center along axis
                    door_center = self.door_from_wall + self.door_width/2
                    best = None
                    for a,b in free:
                        if (b-a) < wardrobe_w:
                            continue
                        cand = a if door_center < (a+b)/2 else (b-wardrobe_w)
                        cand = max(a, min(cand, b-wardrobe_w))
                        dist = abs((cand + wardrobe_w/2) - door_center)
                        if best is None or dist > best[0]:
                            best = (dist, cand)
                    if best is not None:
                        cand_off = best[1]
                        wardrobe_x, wardrobe_y, wardrobe_w, wardrobe_d = self.place_item_on_wall(
                            wardrobe_wall, wardrobe_w, wardrobe_d, offset_from_start=cand_off, center=False
                        )
                        wardrobe_data['x']=wardrobe_x; wardrobe_data['y']=wardrobe_y

        # (B) Maintain a MIN 750mm clearance between wardrobe and bed group.
        # We keep the bed anchored to its wall plane, but allow sliding along the wall.
        min_clear = 750
        bed_rect = (furniture['bed']['x'], furniture['bed']['y'], furniture['bed']['width'], furniture['bed']['depth'])
        wr_rect  = (wardrobe_data['x'], wardrobe_data['y'], wardrobe_data['width'], wardrobe_data['depth'])

        def _min_edge_distance(a, b):
            ax,ay,aw,ad=a; bx,by,bw,bd=b
            dx = max(bx-(ax+aw), ax-(bx+bw), 0)
            dy = max(by-(ay+ad), ay-(by+bd), 0)
            return max(dx, dy) if dx==0 or dy==0 else (dx**2+dy**2)**0.5

        if _min_edge_distance(bed_rect, wr_rect) < min_clear:
            # Slide along bed wall axis away from wardrobe center
            bw = bed_rect[2]; bd = bed_rect[3]
            ext = self.external_wall_thickness
            if bed_wall in ['top','bottom']:
                bed_c = bed_rect[0] + bw/2
                wr_c  = wr_rect[0] + wr_rect[2]/2
                dirn = -1 if bed_c > wr_c else 1
                # compute max slide to stay inside inner boundary
                min_x = ext
                max_x = ext + self.internal_width - bw
                # target shift = (min_clear - current_clear) + 50 buffer
                shift = dirn * (min_clear - _min_edge_distance(bed_rect, wr_rect) + 50)
                new_x = max(min_x, min(max_x, bed_rect[0] + shift))
                dxy = new_x - bed_rect[0]
                # apply to bed group
                for k in ['bed','headboard','bedside_table_left','bedside_table_right','banquet']:
                    if k in furniture:
                        furniture[k]['x'] += dxy
                bed_rect = (furniture['bed']['x'], furniture['bed']['y'], furniture['bed']['width'], furniture['bed']['depth'])
            else:
                bed_c = bed_rect[1] + bd/2
                wr_c  = wr_rect[1] + wr_rect[3]/2
                dirn = -1 if bed_c > wr_c else 1
                min_y = ext
                max_y = ext + self.internal_depth - bd
                shift = dirn * (min_clear - _min_edge_distance(bed_rect, wr_rect) + 50)
                new_y = max(min_y, min(max_y, bed_rect[1] + shift))
                dxy = new_y - bed_rect[1]
                for k in ['bed','headboard','bedside_table_left','bedside_table_right','banquet']:
                    if k in furniture:
                        furniture[k]['y'] += dxy
                bed_rect = (furniture['bed']['x'], furniture['bed']['y'], furniture['bed']['width'], furniture['bed']['depth'])

            if _min_edge_distance(bed_rect, wr_rect) < min_clear:
                validation_issues.append("Could not reach 750mm clear between bed and wardrobe without leaving the inner boundary. Try reducing wardrobe width or enabling a tight aisle.")



        # Enclosure walls (optional): two return walls, each 600mm length, 120mm thick, full room height.
        # They start at the wall line and are anchored to wardrobe sides without overlapping the wardrobe volume.

        enclosure = []
        if wardrobe_is_enclosed:
            t = self.internal_wall_thickness  # 120
            L = 600  # must match wardrobe depth

            if wardrobe_wall in ['top', 'bottom']:
                # Returns are vertical segments at wardrobe ends, running from the wall line into the room
                # spanning exactly the wardrobe depth.
                enclosure.append({
                    'id': f'WALL-{self.room_id}-WL',
                    'x': wardrobe_x - t,
                    'y': wardrobe_y,
                    'width': t,
                    'depth': L,
                    'height': self.height
                })
                enclosure.append({
                    'id': f'WALL-{self.room_id}-WR',
                    'x': wardrobe_x + wardrobe_w,
                    'y': wardrobe_y,
                    'width': t,
                    'depth': L,
                    'height': self.height
                })
            else:
                # Returns are horizontal segments at wardrobe ends, running from the wall line into the room
                # spanning exactly the wardrobe depth.
                enclosure.append({
                    'id': f'WALL-{self.room_id}-WB',
                    'x': wardrobe_x,
                    'y': wardrobe_y - t,
                    'width': L,
                    'depth': t,
                    'height': self.height
                })
                enclosure.append({
                    'id': f'WALL-{self.room_id}-WT',
                    'x': wardrobe_x,
                    'y': wardrobe_y + wardrobe_d,
                    'width': L,
                    'depth': t,
                    'height': self.height
                })

        walls['wardrobe_enclosure'] = enclosure if wardrobe_is_enclosed else []

        # Enforce min 750mm between wardrobe and bed by shifting the BED GROUP along its wall (never delete items).
        bed_rect = (bed_data['x'], bed_data['y'], bed_data['width'], bed_data['depth'])
        wr_rect = (wardrobe_data['x'], wardrobe_data['y'], wardrobe_data['width'], wardrobe_data['depth'])
        min_clear=750
        dist=self._rect_distance(bed_rect, wr_rect)
        if dist < min_clear:
            # Move bed group along wall axis away from wardrobe, within wall bounds
            wall = self.get_wall_info(bed_wall)
            if bed_wall in ['top','bottom']:
                # shift in X
                direction = -1 if bed_data['x'] > wardrobe_data['x'] else 1
                delta = (min_clear - dist) + 50
                new_x = bed_data['x'] + direction*delta
                # clamp
                min_x = wall['start'][0]
                max_x = wall['start'][0] + wall['length'] - self.bed_width
                new_x = max(min_x, min(max_x, new_x))
                dx = new_x - bed_data['x']
                for k in ['bed','headboard','bedside_table_left','bedside_table_right','banquet']:
                    if k in furniture:
                        furniture[k]['x'] += dx
                bed_data['x']=furniture['bed']['x']
            else:
                # shift in Y
                direction = -1 if bed_data['y'] > wardrobe_data['y'] else 1
                delta = (min_clear - dist) + 50
                new_y = bed_data['y'] + direction*delta
                min_y = wall['start'][1]
                max_y = wall['start'][1] + wall['length'] - self.bed_width
                new_y = max(min_y, min(max_y, new_y))
                dy = new_y - bed_data['y']
                for k in ['bed','headboard','bedside_table_left','bedside_table_right','banquet']:
                    if k in furniture:
                        furniture[k]['y'] += dy
                bed_data['y']=furniture['bed']['y']

        # Walk-in wardrobe reserved zone: NEVER push the anchored bed group off its wall.
        # Instead, if the walk-in band intersects the bed zone, we surface a validation issue.
        # The solver earlier will try different wardrobe walls / shrink widths; at this stage
        # we do not mutate already-anchored bedroom elements.
        if wardrobe_is_walkin:
            if wardrobe_wall == 'bottom':
                zone = (wardrobe_data['x'], 0, wardrobe_data['width'], walkin_band)
            elif wardrobe_wall == 'top':
                zone = (wardrobe_data['x'], self.internal_depth - walkin_band, wardrobe_data['width'], walkin_band)
            elif wardrobe_wall == 'left':
                zone = (0, wardrobe_data['y'], walkin_band, wardrobe_data['depth'])
            else:
                zone = (self.internal_width - walkin_band, wardrobe_data['y'], walkin_band, wardrobe_data['depth'])

            def _intersect(r1, r2):
                x1,y1,w1,d1=r1; x2,y2,w2,d2=r2
                return not (x1+w1 <= x2 or x2+w2 <= x1 or y1+d1 <= y2 or y2+d2 <= y1)

            bed_rect = (furniture['bed']['x'], furniture['bed']['y'], furniture['bed']['width'], furniture['bed']['depth'])
            if _intersect(bed_rect, zone):
                validation_issues.append(
                    "Walk-in closet aisle zone intersects the anchored bed zone. Try a different wardrobe wall, reduce wardrobe width, or allow a tight aisle (750mm)."
                )

        # 8. TV UNIT - Place opposite to bed
        opposite_walls = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }
        
        tv_wall = opposite_walls[bed_wall]
        tv_x, tv_y, tv_w, tv_d = self.place_item_on_wall(tv_wall, self.tv_unit_width, 400, center=True)
        
        tv_data = {
            **self.furniture_specs['tv_unit'],
            'x': tv_x,
            'y': tv_y,
            'width': tv_w,
            'depth': tv_d,
            'wall': tv_wall
        }
        furniture['tv_unit'] = tv_data
        self.placed_furniture.append(tv_data)
        
        # 9. DRESSING TABLE - MUST BE BESIDE TV, SAME DEPTH AS TV UNIT, NEVER DELETED
        # Match TV unit depth into room (keep CAD consistency)
        dt_depth = 400
        dt_width = self.dressing_table_width

        # Candidate: beside TV on same wall
        gap=100
        wall = self.get_wall_info(tv_wall)
        along_axis_start = wall['start'][0] if wall['direction']=='horizontal' else wall['start'][1]
        tv_off = (tv_x - wall['start'][0]) if wall['direction']=='horizontal' else (tv_y - wall['start'][1])
        tv_along = self.tv_unit_width

        if dressing_table_side == 'right':
            dt_off = tv_off + tv_along + gap
        else:
            dt_off = tv_off - dt_width - gap

        # Clamp/resize to fit wall
        if dt_off < 0:
            dt_off = 0
        if dt_off + dt_width > wall['length']:
            dt_width = max(600, wall['length'] - dt_off)

        dt_x, dt_y, dt_w, dt_d = self.place_item_on_wall(tv_wall, dt_width, dt_depth, offset_from_start=dt_off, center=False)

        dt_data = {
            **self.furniture_specs['dressing_table'],
            'x': dt_x,
            'y': dt_y,
            'width': dt_w,
            'depth': dt_d,
            'wall': tv_wall
        }
        furniture['dressing_table'] = dt_data
        self.placed_furniture.append(dt_data)

        # 9b. TV PANEL (wall mounted) + MIRROR (above dressing) as BIM-like thin elements
        # TV sizing from diagonal (16:9): width ≈ 0.871*diag, height ≈ 0.49*diag
        diag_mm = float(self.tv_size) * 25.4
        tv_w = max(500.0, diag_mm * 0.871)
        tv_h = max(300.0, diag_mm * 0.490)
        tv_t = 40.0

        # Place TV centered above the TV unit along the same wall, flush to wall plane
        tv_off = (tv_off + (tv_along - tv_w)/2)
        tv_x, tv_y, tv_rect_w, tv_rect_d = self.place_item_on_wall(tv_wall, tv_w, tv_t, offset_from_start=tv_off, center=False)

        tv_panel = {
            'id': f'TV-{self.room_id}-001',
            'x': tv_x,
            'y': tv_y,
            'width': tv_rect_w,
            'depth': tv_rect_d,
            'height': tv_h,
            'mount_z': self._recommended_tv_center_z() - tv_h/2,
            'wall': tv_wall,
            'material': 'Electronics',
            'unit_cost': 0,
        }

        mirror_t = 30.0
        mirror_w = min(1200.0, max(600.0, dt_width))
        mirror_h = 900.0
        # Mirror centered above dressing table on same wall
        dt_off2 = (dt_x - wall['start'][0]) if wall['direction']=='horizontal' else (dt_y - wall['start'][1])
        m_off = dt_off2 + (dt_width - mirror_w)/2
        m_x, m_y, m_rect_w, m_rect_d = self.place_item_on_wall(tv_wall, mirror_w, mirror_t, offset_from_start=m_off, center=False)
        mirror = {
            'id': f'MIR-{self.room_id}-001',
            'x': m_x,
            'y': m_y,
            'width': m_rect_w,
            'depth': m_rect_d,
            'height': mirror_h,
            'mount_z': 1100.0,
            'wall': tv_wall,
            'material': 'Glass',
            'unit_cost': 0,
        }

        furniture['tv_panel'] = tv_panel
        furniture['mirror'] = mirror

        # 10. BANQUET - Place at foot of bed if included
        if self.include_banquet:
            if bed_wall in ['top', 'bottom']:
                banquet_x = bed_x + (self.bed_width - self.banquet_width) / 2
                banquet_y = bed_y + self.bed_depth + 100 if bed_wall == 'bottom' else bed_y - self.banquet_depth - 100
            else:
                banquet_x = bed_x + self.bed_width + 100 if bed_wall == 'left' else bed_x - self.banquet_width - 100
                banquet_y = bed_y + (self.bed_depth - self.banquet_depth) / 2
            
            banquet_data = {
                **self.furniture_specs['banquet'],
                'x': banquet_x,
                'y': banquet_y
            }
            furniture['banquet'] = banquet_data
        
        # 11. SYSTEMS
        systems = self.calculate_systems(furniture)
        
        # 12. BOQ
        boq = self.generate_boq(furniture, systems)
        
        # 13. METADATA
        metadata = {
            'room_id': self.room_id,
            'tv_size': self.tv_size,
            'viewing_distance': self.clearances['tv_viewing_distance'],
            'bed_wall': bed_wall,
            'wardrobe_wall': wardrobe_wall,
            'wardrobe_mode': mode,
            'walkin_aisle': self._walkin_aisle_depth() if mode in ('walkin_l','walkin_u') else 0,
            'tv_wall': tv_wall,
            'window_wall': self.window_wall,
            'door_wall': self.door_wall,
            'bedside_table_count': self.bedside_table_count,
            'include_banquet': self.include_banquet,
            'validation_issues': validation_issues,
            'generated_at': datetime.now().isoformat()
        }
        
        return {
            'room': {
                'id': self.room_id,
                'internal_width': self.internal_width,
                'internal_depth': self.internal_depth,
                'external_width': self.external_width,
                'external_depth': self.external_depth,
                'height': self.height,
                'area_m2': round((self.internal_width * self.internal_depth) / 1000000, 2),
                'external_wall_thickness': self.external_wall_thickness,
                'internal_wall_thickness': self.internal_wall_thickness
            },
            'walls': walls,
            'architectural': {
                'door': door,
                'window': window,
                'bed_wall': {'type': bed_wall}
            },
            'furniture': furniture,
            'systems': systems,
            'boq': boq,
            'metadata': metadata
        }
    
    def calculate_systems(self, furniture):
        """Calculate electrical, lighting, and AC systems"""
        systems = {
            'electrical': [],
            'lighting': [],
            'ac': []
        }
        
        socket_id = 1
        
        # Electrical sockets
        if self.include_electrical:
            # TV wall socket
            systems['electrical'].append({
                'id': f'ELEC-{self.room_id}-{socket_id:03d}',
                'type': '5-pin socket',
                'location': 'tv_wall',
                'quantity': 2,
                'unit_cost': 25
            })
            socket_id += 1
            
            # Bedside sockets
            if 'bedside_table_left' in furniture:
                systems['electrical'].append({
                    'id': f'ELEC-{self.room_id}-{socket_id:03d}',
                    'type': '5-pin socket',
                    'location': 'bedside_left',
                    'quantity': 1,
                    'unit_cost': 25
                })
                socket_id += 1
            
            if 'bedside_table_right' in furniture:
                systems['electrical'].append({
                    'id': f'ELEC-{self.room_id}-{socket_id:03d}',
                    'type': '5-pin socket',
                    'location': 'bedside_right',
                    'quantity': 1,
                    'unit_cost': 25
                })
                socket_id += 1
            
            # Dressing table socket
            systems['electrical'].append({
                'id': f'ELEC-{self.room_id}-{socket_id:03d}',
                'type': '5-pin socket',
                'location': 'dressing_table',
                'quantity': 1,
                'unit_cost': 25
            })
        
        # Lighting
        if self.include_lighting:
            light_count = int((self.internal_width * self.internal_depth) / 4000000) + 2
            
            for i in range(light_count):
                systems['lighting'].append({
                    'id': f'LIGHT-{self.room_id}-{i+1:03d}',
                    'type': self.lighting_type,
                    'wattage': 15,
                    'unit_cost': 50
                })
        
        # AC
        if self.include_ac:
            ac_capacity = self.calculate_ac_capacity()
            systems['ac'].append({
                'id': f'AC-{self.room_id}-001',
                'type': self.ac_type,
                'capacity_hp': ac_capacity,
                'capacity_btu': int(ac_capacity * 12000 / 1.5),
                'unit_cost': int(ac_capacity * 500)
            })
        
        return systems
    
    def generate_boq(self, furniture, systems):
        """Generate Bill of Quantities"""
        items = []
        
        # Furniture
        for name, item in furniture.items():
            items.append({
                'id': item['id'],
                'category': 'Furniture',
                'item': name.replace('_', ' ').title(),
                'specification': f"{item['width']}x{item['depth']}x{item['height']}mm - {item['material']}",
                'quantity': 1,
                'unit': 'nos',
                'unit_cost': item['unit_cost'],
                'total_cost': item['unit_cost']
            })
        
        # Electrical
        for socket in systems['electrical']:
            items.append({
                'id': socket['id'],
                'category': 'Electrical',
                'item': socket['type'],
                'specification': socket['location'],
                'quantity': socket['quantity'],
                'unit': 'nos',
                'unit_cost': socket['unit_cost'],
                'total_cost': socket['quantity'] * socket['unit_cost']
            })
        
        # Lighting
        for light in systems['lighting']:
            items.append({
                'id': light['id'],
                'category': 'Lighting',
                'item': f"{light['type']} - {light['wattage']}W",
                'specification': 'LED downlight',
                'quantity': 1,
                'unit': 'nos',
                'unit_cost': light['unit_cost'],
                'total_cost': light['unit_cost']
            })
        
        # AC
        for ac in systems['ac']:
            items.append({
                'id': ac['id'],
                'category': 'AC',
                'item': f"{ac['type']} - {ac['capacity_hp']} HP",
                'specification': f"{ac['capacity_btu']} BTU",
                'quantity': 1,
                'unit': 'nos',
                'unit_cost': ac['unit_cost'],
                'total_cost': ac['unit_cost']
            })
        
        total_cost = sum(item['total_cost'] for item in items)
        
        return {
            'items': items,
            'total_cost': total_cost,
            'currency': 'USD'
        }
    
    def create_visualization(self, layout):
        """Create 2D floor plan visualization"""
        fig, ax = plt.subplots(figsize=(18, 16))
        
        ext_wall = layout['room']['external_wall_thickness']
        ext_width = layout['room']['external_width']
        ext_depth = layout['room']['external_depth']
        
        # Draw external walls
        wall_color = '#9ca3af'
        for wall_name, wall in layout['walls']['external'].items():
            rect = patches.Rectangle(
                (wall['x'], wall['y']),
                wall['width'],
                wall['depth'],
                linewidth=0,
                facecolor=wall_color,
                alpha=0.8,
                zorder=2
            )
            ax.add_patch(rect)
        

        # Draw wardrobe enclosure walls (two returns) - 600mm length x 120mm thick
        for w in layout['walls'].get('wardrobe_enclosure', []):
            rect = patches.Rectangle(
                (w['x'], w['y']),
                w['width'],
                w['depth'],
                linewidth=0,
                facecolor='#d1d5db',
                alpha=0.9,
                zorder=2
            )
            ax.add_patch(rect)

        # CAD/BIM-like boolean openings: cut door and window openings out of the wall bands
        bg = 'white'
        door = layout['architectural']['door']
        window = layout['architectural']['window']

        def cut_opening(opening, is_door: bool):
            wn = opening['wall']
            wall = layout['walls']['external'][wn]
            if wn in ['top', 'bottom']:
                ox = float(opening['x'])
                ow = float(opening['width'])
                oy = float(wall['y'])
                od = float(wall['depth'])
            else:
                ox = float(wall['x'])
                ow = float(wall['width'])
                oy = float(opening['y'])
                od = float(opening['depth'])

            ax.add_patch(
                patches.Rectangle(
                    (ox, oy), ow, od,
                    linewidth=0,
                    facecolor=bg,
                    zorder=2.5,
                )
            )

        cut_opening(door, is_door=True)
        cut_opening(window, is_door=False)
        
        
        # Draw door (HINGED LEAF - NO ARC). Leaf can be shown at open_angle (default 0deg closed).
        door = layout['architectural']['door']
        door_wall = door['wall']
        
        # Opening line (jamb)
        if door_wall in ['top', 'bottom']:
            ax.plot([door['x'], door['x'] + door['width']], [door['y'], door['y']], color='#111827', linewidth=2, zorder=3)
        else:
            ax.plot([door['x'], door['x']], [door['y'], door['y'] + door['depth']], color='#111827', linewidth=2, zorder=3)
        
        # Leaf line
        ang = float(door.get('open_angle', 45))
        # hinge point
        if door_wall in ['top','bottom']:
            hx = door['x'] if door['hinge']=='left' else door['x']+door['width']
            hy = door['y']
            # into room direction
            sign = -1 if door_wall=='top' else 1
            # rotate from wall axis into room
            # 0deg is along wall; leaf swings into room
            theta = (90 - ang) if door['hinge']=='left' else (90 + ang)
            import numpy as _np
            rad = _np.deg2rad(theta)
            lx = hx + door['width'] * _np.cos(rad)
            ly = hy + sign * abs(door['width'] * _np.sin(rad))
            ax.plot([hx, lx], [hy, ly], color='#111827', linewidth=2, zorder=3)
        else:
            hy = door['y'] if door['hinge']=='left' else door['y']+door['depth']
            hx = door['x']
            sign = -1 if door_wall=='right' else 1
            import numpy as _np
            theta = (0 + ang) if door['hinge']=='left' else (180 - ang)
            rad = _np.deg2rad(theta)
            lx = hx + sign * abs(door['depth'] * _np.cos(rad))
            ly = hy + door['depth'] * _np.sin(rad)
            ax.plot([hx, lx], [hy, ly], color='#111827', linewidth=2, zorder=3)
        
                
        # Draw window (SLIDING symbol)
        window = layout['architectural']['window']
        if window['wall'] in ['top', 'bottom']:
            x0 = window['x']; x1 = window['x'] + window['width']
            y = window['y']
            # two rails inside the wall thickness
            ax.plot([x0, x1], [y + 15, y + 15], color='#111827', linewidth=2, zorder=3)
            ax.plot([x0, x1], [y - 15, y - 15], color='#111827', linewidth=2, zorder=3)
            # sliding panel line (center)
            ax.plot([x0 + window['width']/2, x0 + window['width']/2], [y - 15, y + 15], color='#111827', linewidth=2, zorder=3)
        else:
            y0 = window['y']; y1 = window['y'] + window['depth']
            x = window['x']
            ax.plot([x + 15, x + 15], [y0, y1], color='#111827', linewidth=2, zorder=3)
            ax.plot([x - 15, x - 15], [y0, y1], color='#111827', linewidth=2, zorder=3)
            ax.plot([x - 15, x + 15], [y0 + window['depth']/2, y0 + window['depth']/2], color='#111827', linewidth=2, zorder=3)
        
        # Draw furniture (CAD-like: white fill, dark outline, short tags)
        ordered_keys = [
            'bed', 'headboard', 'bedside_table_left', 'bedside_table_right',
            'wardrobe', 'tv_unit', 'tv_panel', 'dressing_table', 'mirror',
            'banquet'
        ]
        # Keep remaining keys at the end
        rest = [k for k in layout['furniture'].keys() if k not in ordered_keys]
        keys = [k for k in ordered_keys if k in layout['furniture']] + rest

        for idx, name in enumerate(keys, start=1):
            item = layout['furniture'][name]
            tag = f"FUR-{idx:02d}"
            rect = patches.Rectangle(
                (item['x'], item['y']),
                item['width'],
                item['depth'],
                linewidth=1.8,
                edgecolor='#111827',
                facecolor='white',
                alpha=1.0,
                zorder=4
            )
            ax.add_patch(rect)

            ax.text(
                item['x'] + 20,
                item['y'] + item['depth'] - 30,
                tag,
                ha='left', va='top',
                fontsize=8, fontweight='bold',
                color='#111827',
                zorder=5
            )
        
        # (Optional) sockets: intentionally omitted from the CAD plan to avoid confusing symbols.
        
        # Set up plot
        ax.set_xlim(-400, ext_width + 400)
        ax.set_ylim(-400, ext_depth + 400)
        ax.set_aspect('equal')
        ax.set_xlabel('Width (mm)', fontsize=12)
        ax.set_ylabel('Depth (mm)', fontsize=12)
        ax.set_title(f'BEDROOM LAYOUT - ID: {self.room_id} | TV: {layout["metadata"]["tv_size"]}" | Total: ${layout["boq"]["total_cost"]}',
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        plt.tight_layout()
        return fig
            
    def generate_3d_view(self, layout):
        """Generate 3D view.

        - If Plotly is available, return a Plotly figure with true 360° orbit controls.
        - Otherwise fall back to matplotlib.
        """

        # --- Plotly (preferred): true orbit + solid BIM-like wall masses ---
        if go is not None:
            ext_w = float(layout['room']['external_width'])
            ext_d = float(layout['room']['external_depth'])
            ext_t = float(layout['room']['external_wall_thickness'])
            H = float(layout['room']['height'])

            door = layout['architectural']['door']
            window = layout['architectural']['window']
            door_h = float(self.door_height)
            win_sill = float(self.window_sill)
            win_h = float(self.window_height)

            fig = go.Figure()

            def add_box(x, y, z, w, d, h, color, opacity=1.0, name=None):
                # 8 vertices of the box
                X = [x, x+w, x+w, x, x, x+w, x+w, x]
                Y = [y, y, y+d, y+d, y, y, y+d, y+d]
                Z = [z, z, z, z, z+h, z+h, z+h, z+h]
                # 12 triangles (two per face)
                I = [0, 0, 0, 1, 1, 2, 4, 4, 4, 5, 5, 6]
                J = [1, 2, 3, 2, 5, 3, 5, 6, 7, 6, 1, 7]
                K = [2, 3, 1, 5, 2, 6, 6, 7, 5, 1, 4, 3]
                fig.add_trace(go.Mesh3d(
                    x=X, y=Y, z=Z,
                    i=I, j=J, k=K,
                    color=color,
                    opacity=opacity,
                    flatshading=True,
                    name=name or '',
                    hoverinfo='skip',
                    showscale=False,
                ))

            wall_color = '#9ca3af'

            # Helper: split a wall run by an opening interval
            def split_run(total_len, open_a, open_b):
                segs=[]
                if open_a > 0:
                    segs.append((0, open_a))
                if open_b < total_len:
                    segs.append((open_b, total_len))
                return segs

            # --- External walls (as solid boxes), split by openings ---
            # Bottom wall
            if door['wall'] == 'bottom':
                open_a = float(door['x'])
                open_b = float(door['x'] + door['width'])
                for a,b in split_run(ext_w, open_a, open_b):
                    add_box(a, 0, 0, b-a, ext_t, H, wall_color, 1.0, 'wall')
                # lintel above door
                add_box(open_a, 0, door_h, open_b-open_a, ext_t, H-door_h, wall_color, 1.0, 'lintel')
            else:
                add_box(0, 0, 0, ext_w, ext_t, H, wall_color, 1.0, 'wall')

            # Top wall
            if door['wall'] == 'top':
                open_a = float(door['x'])
                open_b = float(door['x'] + door['width'])
                for a,b in split_run(ext_w, open_a, open_b):
                    add_box(a, ext_d-ext_t, 0, b-a, ext_t, H, wall_color, 1.0, 'wall')
                add_box(open_a, ext_d-ext_t, door_h, open_b-open_a, ext_t, H-door_h, wall_color, 1.0, 'lintel')
            else:
                add_box(0, ext_d-ext_t, 0, ext_w, ext_t, H, wall_color, 1.0, 'wall')

            # Left wall
            if door['wall'] == 'left':
                open_a = float(door['y'])
                open_b = float(door['y'] + door['depth'])
                for a,b in split_run(ext_d, open_a, open_b):
                    add_box(0, a, 0, ext_t, b-a, H, wall_color, 1.0, 'wall')
                add_box(0, open_a, door_h, ext_t, open_b-open_a, H-door_h, wall_color, 1.0, 'lintel')
            else:
                add_box(0, 0, 0, ext_t, ext_d, H, wall_color, 1.0, 'wall')

            # Right wall
            if door['wall'] == 'right':
                open_a = float(door['y'])
                open_b = float(door['y'] + door['depth'])
                for a,b in split_run(ext_d, open_a, open_b):
                    add_box(ext_w-ext_t, a, 0, ext_t, b-a, H, wall_color, 1.0, 'wall')
                add_box(ext_w-ext_t, open_a, door_h, ext_t, open_b-open_a, H-door_h, wall_color, 1.0, 'lintel')
            else:
                add_box(ext_w-ext_t, 0, 0, ext_t, ext_d, H, wall_color, 1.0, 'wall')

            # --- Window opening (sill + lintel) ---
            # We represent the opening by *not* cutting the wall mass (Plotly boolean is heavy),
            # but we do add explicit sill & lintel masses so it reads as BIM.
            # A more detailed wall-splitting for windows can be added next.
            win_wall = window['wall']
            if win_wall in ('top','bottom'):
                wx0 = float(window['x']); wx1 = float(window['x'] + window['width'])
                wy = float(window['y']) if win_wall=='bottom' else float(window['y'])
                # sill
                add_box(wx0, (0 if win_wall=='bottom' else ext_d-ext_t), 0, wx1-wx0, ext_t, win_sill, wall_color, 1.0, 'sill')
                # lintel
                add_box(wx0, (0 if win_wall=='bottom' else ext_d-ext_t), win_sill+win_h, wx1-wx0, ext_t, max(0.0, H-(win_sill+win_h)), wall_color, 1.0, 'lintel')
            else:
                wy0 = float(window['y']); wy1 = float(window['y'] + window['depth'])
                wx = float(window['x'])
                add_box((0 if win_wall=='left' else ext_w-ext_t), wy0, 0, ext_t, wy1-wy0, win_sill, wall_color, 1.0, 'sill')
                add_box((0 if win_wall=='left' else ext_w-ext_t), wy0, win_sill+win_h, ext_t, wy1-wy0, max(0.0, H-(win_sill+win_h)), wall_color, 1.0, 'lintel')

            # Wardrobe enclosure return walls
            for w in layout['walls'].get('wardrobe_enclosure', []):
                add_box(float(w['x']), float(w['y']), 0, float(w['width']), float(w['depth']), H, '#d1d5db', 1.0, 'wardrobe_wall')

            # Furniture masses (simple BIM blocks)
            for name, item in layout['furniture'].items():
                # TV panel + mirror are wall-mounted: use their mount_z if present
                z0 = float(item.get('mount_z', 0.0))
                h = float(item.get('height', 600.0))
                add_box(float(item['x']), float(item['y']), z0, float(item['width']), float(item['depth']), h, '#e5e7eb', 1.0, name)

            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                scene=dict(
                    xaxis_title='X (mm)',
                    yaxis_title='Y (mm)',
                    zaxis_title='Z (mm)',
                    aspectmode='data',
                    dragmode='orbit',
                    camera=dict(eye=dict(x=1.6, y=1.6, z=1.1)),
                ),
                showlegend=False,
            )
            return fig

        # --- Matplotlib fallback ---
        fig = plt.figure(figsize=(16, 14))
        ax = fig.add_subplot(111, projection='3d')
        
        ext_width = layout['room']['external_width']
        ext_depth = layout['room']['external_depth']
        height = layout['room']['height']
        
        # Draw floor
        X, Y = np.meshgrid([0, ext_width], [0, ext_depth])
        Z = np.zeros_like(X)
        ax.plot_surface(X, Y, Z, alpha=0.3, color='#d1d5db')
        

        # Draw BIM-like walls with boolean-like openings (door + window) and lintels/sills
        wall_color = '#9ca3af'
        edge_color = '#6b7280'
        
        def add_plane(poly, alpha=0.85, fc=wall_color):
            ax.add_collection3d(Poly3DCollection([poly], alpha=alpha, facecolor=fc, edgecolor=edge_color))
        
        # Helper to add wall segments on each boundary plane
        def add_wall_segments(wall_name, along_len, opening=None, opening_z=(0,0), opening_type=None):
            """wall_name: bottom/top/left/right. opening: (a,b) along axis, opening_z: (z0,z1) void."""
            segments=[(0,along_len)]
            if opening:
                a,b=opening
                new=[]
                for s0,s1 in segments:
                    if b<=s0 or a>=s1:
                        new.append((s0,s1))
                    else:
                        if a>s0: new.append((s0,a))
                        if b<s1: new.append((b,s1))
                segments=new
            # create solid segments
            for s0,s1 in segments:
                if wall_name=='bottom':
                    add_plane([[s0,0,0],[s1,0,0],[s1,0,height],[s0,0,height]])
                elif wall_name=='top':
                    add_plane([[s0,ext_depth,0],[s1,ext_depth,0],[s1,ext_depth,height],[s0,ext_depth,height]])
                elif wall_name=='left':
                    add_plane([[0,s0,0],[0,s1,0],[0,s1,height],[0,s0,height]])
                elif wall_name=='right':
                    add_plane([[ext_width,s0,0],[ext_width,s1,0],[ext_width,s1,height],[ext_width,s0,height]])
        
            # If there is an opening, add sill/lintel pieces on that same plane
            if opening and opening_type in ('door','window'):
                a,b=opening
                z0,z1=opening_z
                if z1 < height:  # lintel above
                    if wall_name=='bottom':
                        add_plane([[a,0,z1],[b,0,z1],[b,0,height],[a,0,height]])
                    elif wall_name=='top':
                        add_plane([[a,ext_depth,z1],[b,ext_depth,z1],[b,ext_depth,height],[a,ext_depth,height]])
                    elif wall_name=='left':
                        add_plane([[0,a,z1],[0,b,z1],[0,b,height],[0,a,height]])
                    elif wall_name=='right':
                        add_plane([[ext_width,a,z1],[ext_width,b,z1],[ext_width,b,height],[ext_width,a,height]])
                if opening_type=='window' and z0>0:  # wall below sill
                    if wall_name=='bottom':
                        add_plane([[a,0,0],[b,0,0],[b,0,z0],[a,0,z0]])
                    elif wall_name=='top':
                        add_plane([[a,ext_depth,0],[b,ext_depth,0],[b,ext_depth,z0],[a,ext_depth,z0]])
                    elif wall_name=='left':
                        add_plane([[0,a,0],[0,b,0],[0,b,z0],[0,a,z0]])
                    elif wall_name=='right':
                        add_plane([[ext_width,a,0],[ext_width,b,0],[ext_width,b,z0],[ext_width,a,z0]])
        
        # Determine door/window intervals in wall axis coords
        door = layout['architectural']['door']
        window = layout['architectural']['window']
        
        # Default: no openings
        for wn in ['bottom','top','left','right']:
            opening=None; oz=(0,0); otype=None
            if door['wall']==wn:
                if wn in ['bottom','top']:
                    a=float(door['x']); b=float(door['x']+door['width'])
                else:
                    a=float(door['y']); b=float(door['y']+door['depth'])
                opening=(a,b); oz=(0,float(self.door_height)); otype='door'
            elif window['wall']==wn:
                if wn in ['bottom','top']:
                    a=float(window['x']); b=float(window['x']+window['width'])
                else:
                    a=float(window['y']); b=float(window['y']+window['depth'])
                opening=(a,b); oz=(float(self.window_sill), float(self.window_sill+self.window_height)); otype='window'
        
            along = ext_width if wn in ['bottom','top'] else ext_depth
            add_wall_segments(wn, along, opening=opening, opening_z=oz, opening_type=otype)
        
        # Add wardrobe enclosure walls as 3D boxes (full height)
        for w in layout['walls'].get('wardrobe_enclosure', []):
            x,y = w['x'], w['y']
            wW, wD = w['width'], w['depth']
            h = w.get('height', height)
            verts = [
                [x,y,0],[x+wW,y,0],[x+wW,y+wD,0],[x,y+wD,0],
                [x,y,h],[x+wW,y,h],[x+wW,y+wD,h],[x,y+wD,h]
            ]
            faces = [
                [verts[0],verts[1],verts[5],verts[4]],
                [verts[1],verts[2],verts[6],verts[5]],
                [verts[2],verts[3],verts[7],verts[6]],
                [verts[3],verts[0],verts[4],verts[7]],
                [verts[4],verts[5],verts[6],verts[7]],
                [verts[0],verts[1],verts[2],verts[3]]
            ]
            for f in faces:
                ax.add_collection3d(Poly3DCollection([f], alpha=0.9, facecolor='#d1d5db', edgecolor=edge_color))
        
        # Draw furniture in 3D
        colors_3d = {
            'bed': '#3b82f6',
            'headboard': '#1d4ed8',
            'wardrobe': '#78350f',
            'tv_unit': '#4b5563',
            'dressing_table': '#d946ef',
            'banquet': '#f97316',
            'bedside_table_left': '#10b981',
            'bedside_table_right': '#10b981'
        }

        for name, item in layout['furniture'].items():
            if name in colors_3d:
                x, y = item['x'], item['y']
                w, d = item['width'], item['depth']
                h = item.get('height', 500)

                vertices = [
                    [x, y, 0], [x+w, y, 0], [x+w, y+d, 0], [x, y+d, 0],
                    [x, y, h], [x+w, y, h], [x+w, y+d, h], [x, y+d, h]
                ]

                faces = [
                    [vertices[0], vertices[1], vertices[5], vertices[4]],
                    [vertices[2], vertices[3], vertices[7], vertices[6]],
                    [vertices[0], vertices[3], vertices[7], vertices[4]],
                    [vertices[1], vertices[2], vertices[6], vertices[5]],
                    [vertices[0], vertices[1], vertices[2], vertices[3]],
                    [vertices[4], vertices[5], vertices[6], vertices[7]]
                ]

                for face in faces:
                    poly = Poly3DCollection([face], alpha=0.8, facecolor=colors_3d[name], edgecolor='#1f2937')
                    ax.add_collection3d(poly)

        # Set labels and title
        ax.set_xlabel('Width (mm)', fontsize=11, labelpad=10)
        ax.set_ylabel('Depth (mm)', fontsize=11, labelpad=10)
        ax.set_zlabel('Height (mm)', fontsize=11, labelpad=10)
        ax.set_title('3D View - Interactive (drag to rotate, scroll to zoom)', fontsize=14, pad=20)

        # Set view angle
        ax.view_init(elev=25, azim=45)

        # Set equal aspect ratio
        max_dim = max(ext_width, ext_depth, height)
        ax.set_xlim(0, max_dim)
        ax.set_ylim(0, max_dim)
        ax.set_zlim(0, max_dim)

        plt.tight_layout()
        return fig
