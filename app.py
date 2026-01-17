# app.py - UPDATED SIDEBAR SECTION
import streamlit as st
import json
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from bedroom_engine import BedroomEngine
from dxf_exporter import export_to_dxf

# ---- UI Defaults / Controls (single source of truth) ----
def _load_ui_controls(path: str = "ui_controls.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"defaults": {}}

_UI = _load_ui_controls()
_DEFAULTS = _UI.get("defaults", {})

def ensure_state(key: str, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

# Page configuration
st.set_page_config(
    page_title="Professional Bedroom Designer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (keep the same as before)
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-box {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #BAE6FD;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .boq-table {
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    .total-cost {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 1rem;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        border: none;
        color: white;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏠 Professional Bedroom Design System</h1>', unsafe_allow_html=True)

# Feature highlights (keep the same)
st.markdown("""
<div class="feature-box">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
        <div>
            <strong>🎯 SMART DESIGN FEATURES:</strong><br>
            • TV size calculated automatically<br>
            • Optimal viewing distance<br>
            • Unique IDs for all items<br>
            • Auto BOQ generation<br>
            • Collision detection
        </div>
        <div>
            <strong>🏗️ COMPLETE SYSTEMS:</strong><br>
            • Electrical sockets layout<br>
            • Lighting design<br>
            • AC placement<br>
            • DXF export<br>
            • 3D visualization
        </div>
        <div>
            <strong>📊 PROFESSIONAL OUTPUTS:</strong><br>
            • Bill of Quantities (BOQ)<br>
            • Cost estimation<br>
            • Material specifications<br>
            • Professional drawings<br>
            • All IDs tracked
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar - UPDATED
with st.sidebar:
    # Sidebar global expand/collapse (applies to all expanders)
    if 'sidebar_expand_all' not in st.session_state:
        st.session_state.sidebar_expand_all = True

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Expand all", use_container_width=True):
            st.session_state.sidebar_expand_all = True
    with col_b:
        if st.button("Collapse all", use_container_width=True):
            st.session_state.sidebar_expand_all = False

    st.markdown("### ⚙️ Input Method")

    # ---- Persistent UI defaults (single source of truth: ui_controls.json) ----
    for _k, _v in _DEFAULTS.items():
        ensure_state(_k, _v)

    # Back-compat keys used by earlier sidebar widgets
    ensure_state('wardrobe_width', st.session_state.get('wardrobe_width_mm', 1800))
    ensure_state('wardrobe_depth', st.session_state.get('wardrobe_depth_mm', 600))
    ensure_state('tv_unit_width', st.session_state.get('tv_unit_width_mm', 1200))
    ensure_state('dressing_table_width', st.session_state.get('dressing_table_width_mm', 1000))
    ensure_state('dresser_width', st.session_state.get('dresser_width_mm', 1200))
    ensure_state('dresser_depth', st.session_state.get('dresser_depth_mm', 500))
    ensure_state('include_tv', st.session_state.get('tv_enabled', True))
    ensure_state('include_dressing_table', st.session_state.get('dressing_table_enabled', False))
    ensure_state('include_dresser', st.session_state.get('include_dresser', False))
    ensure_state('include_chair', st.session_state.get('include_under_window_chair', True))
    ensure_state('include_banquet', False)
    ensure_state('headboard_width_mm', 1600)
    ensure_state('headboard_height_mm', 1000)
    
    input_method = st.radio("Choose input method:", 
                           ["Manual Parameters", "Upload DXF (Coming Soon)"], 
                           index=0)
    
    if "Upload DXF" in input_method:
        st.warning("DXF upload feature is under development. Using manual parameters.")
        input_method = "Manual Parameters"
    
    st.markdown("---")
    
    if input_method == "Manual Parameters":
        with st.expander("📐 Room", expanded=st.session_state.sidebar_expand_all):
            col1, col2 = st.columns(2)
            with col1:
                width = st.number_input(
                    "Width (mm) - Internal",
                    2000, 10000,
                    int(st.session_state.get('room_width_mm', 4500)),
                    100,
                    key='room_width_mm'
                )
            with col2:
                depth = st.number_input(
                    "Depth (mm) - Internal",
                    2000, 10000,
                    int(st.session_state.get('room_depth_mm', 4000)),
                    100,
                    key='room_depth_mm'
                )
            height = st.number_input(
                "Height (mm)",
                2400, 5000,
                int(st.session_state.get('room_height_mm', 3000)),
                100,
                key='room_height_mm'
            )

        # --- Doors & Windows ---
        with st.expander("🚪 Doors", expanded=st.session_state.sidebar_expand_all):
            door_wall = st.selectbox(
                "Door Wall",
                ["top", "bottom", "left", "right"],
                index=["top","bottom","left","right"].index(st.session_state.get('door_wall','top')),
                key='door_wall'
            )
            _door_max = int(max(0, min(width, depth) - 600))
            # clamp stored value into dynamic range
            if st.session_state.get('door_offset_mm', 0) > _door_max:
                st.session_state['door_offset_mm'] = _door_max
            door_from_wall = st.number_input(
                "Door offset from corner (mm)",
                0, _door_max,
                int(st.session_state.get('door_offset_mm', 200)),
                50,
                key='door_offset_mm'
            )
            door_width = st.number_input(
                "Door Width (mm)",
                600, 1200,
                int(st.session_state.get('door_width_mm', 900)),
                50,
                key='door_width_mm'
            )
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                door_hinge = st.selectbox(
                    "Hinge Side",
                    ["left", "right"],
                    index=["left","right"].index(st.session_state.get('door_hinge_side','left')),
                    key='door_hinge_side'
                )
            with col_d2:
                door_swing = st.selectbox(
                    "Swing",
                    ["inward", "outward"],
                    index=["inward","outward"].index(st.session_state.get('door_swing','inward')),
                    key='door_swing'
                )

        with st.expander("🪟 Windows", expanded=st.session_state.sidebar_expand_all):
            window_wall = st.selectbox(
                "Window Wall",
                ["right", "left", "bottom", "top"],
                index=["right","left","bottom","top"].index(st.session_state.get('window_wall','right')),
                key='window_wall'
            )
            window_width = st.number_input(
                "Window Width (mm)",
                800, 3000,
                int(st.session_state.get('window_width_mm', 1800)),
                100,
                key='window_width_mm'
            )
            window_sill = st.number_input(
                "Window Sill (mm)",
                200, 1200,
                int(st.session_state.get('window_sill_mm', 300)),
                50,
                key='window_sill_mm'
            )

            # Under-window options based on sill height rules
            _uw_prev = st.session_state.get('under_window_use', 'auto')
            if window_sill < 450:
                st.info("Sill < 450mm → keep window wall clear (no bench/desk).")
                under_window_use = 'none'
            elif 450 <= window_sill < 600:
                under_window_use = st.selectbox(
                    "Under-window option (450–600mm sill)",
                    ["none", "bench"],
                    index=["none","bench"].index('bench' if _uw_prev=='bench' else 'none'),
                    help="Bench is allowed below window when sill is 450–600mm."
                )
            elif 600 <= window_sill <= 900:
                under_window_use = st.selectbox(
                    "Under-window option (600–900mm sill)",
                    ["none", "bench", "study_table"],
                    index=["none","bench","study_table"].index(_uw_prev if _uw_prev in ["none","bench","study_table"] else "none"),
                    help="Bench OR study table is allowed when sill is 600–900mm. Study table will face the window (desk against window wall)."
                )
            else:
                st.info("Sill outside typical range → keeping window wall clear for safety.")
                under_window_use = 'none'

            # Persist the selection so next rerun keeps it
            st.session_state['under_window_use'] = under_window_use

            # Optional chair (only meaningful when a study table exists)
            if under_window_use == 'study_table':
                include_chair = st.checkbox(
                    "Include chair (if desk is used)",
                    value=bool(st.session_state.include_chair),
                    key='include_chair'
                )
            else:
                include_chair = False

        with st.expander("🛏️ Bed group", expanded=st.session_state.sidebar_expand_all):
            # Default bed preset is driven by ui_controls.json
            _bed_labels = [
                "King (1800x2000)",
                "Queen (1600x2000)",
                "Double (1400x1900)",
                "Single (1200x1900)",
            ]
            _bed_key_to_label = {
                "king_1800x2000": "King (1800x2000)",
                "queen_1600x2000": "Queen (1600x2000)",
                "double_1400x1900": "Double (1400x1900)",
                "single_1200x1900": "Single (1200x1900)",
            }
            _default_bed_label = _bed_key_to_label.get(st.session_state.get('bed_preset', 'queen_1600x2000'), "Queen (1600x2000)")
            bed_type = st.selectbox(
                "Bed Size",
                _bed_labels,
                index=_bed_labels.index(_default_bed_label),
                key='bed_size_label'
            )

            bed_wall_label = st.selectbox(
                "Bed Wall (Anchoring)",
                ["Auto", "Top", "Bottom", "Left", "Right"],
                index=0,
                help="Forces the bed group to anchor to the selected wall (cannot be the window wall)."
            )

            bed_wall_preference = {
                "Auto": "auto",
                "Top": "top",
                "Bottom": "bottom",
                "Left": "left",
                "Right": "right",
            }[bed_wall_label]

            bedside_table_count = st.slider("Bedside Tables", 0, 2, 2, key='bedside_table_count')
            include_banquet = st.checkbox("Include Banquet", bool(st.session_state.get('include_banquet', False)), key='include_banquet')

            col1, col2 = st.columns(2)
            with col1:
                headboard_width = st.number_input(
                    "Headboard Width (mm)",
                    1200, 2200,
                    int(st.session_state.get('headboard_width_mm', 1600)),
                    50,
                    key='headboard_width_mm'
                )
            with col2:
                headboard_height = st.number_input(
                    "Headboard Height (mm)",
                    800, 1500,
                    int(st.session_state.get('headboard_height_mm', 1000)),
                    50,
                    key='headboard_height_mm'
                )

            # NOTE: Streamlit does not allow nested expanders.
            # Use an "Advanced" toggle instead of an expander inside an expander.
            bedside_width = int(st.session_state.get('bedside_table_width_mm', 450))
            bedside_depth = int(st.session_state.get('bedside_table_depth_mm', 400))
            show_bedside_adv = st.checkbox("Advanced: bedside table dimensions", value=False)
            if show_bedside_adv:
                col1, col2 = st.columns(2)
                with col1:
                    bedside_width = st.number_input(
                        "Bedside Width (mm)",
                        300, 800,
                        int(st.session_state.get('bedside_table_width_mm', 450)),
                        50,
                        key='bedside_table_width_mm'
                    )
                with col2:
                    bedside_depth = st.number_input(
                        "Bedside Depth (mm)",
                        300, 600,
                        int(st.session_state.get('bedside_table_depth_mm', 400)),
                        50,
                        key='bedside_table_depth_mm'
                    )

        with st.expander("🗄️ Wardrobe", expanded=st.session_state.sidebar_expand_all):
            colw1, colw2 = st.columns(2)
            with colw1:
                wardrobe_width = st.number_input(
                    "Wardrobe Width (mm)",
                    1200, 4000,
                    int(st.session_state.wardrobe_width),
                    100,
                    key='wardrobe_width'
                )
            with colw2:
                wardrobe_depth = st.number_input(
                    "Wardrobe Depth (mm)",
                    450, 800,
                    int(st.session_state.wardrobe_depth),
                    50,
                    key='wardrobe_depth'
                )

            wardrobe_config_label = st.selectbox(
                "Wardrobe configuration",
                [
                    "W-1 Centered (no return wall)",
                    "W-2 Full wall (wall-to-wall)",
                    "W-3 Built-in (return wall)",
                ],
                index=0,
                help="W-1: centered on clear wall segment. W-2: spans entire wall if no door/window conflicts. W-3: built-in (surrounded by walls) with a 600mm return wall (120mm thick) placed to avoid the door arc."
            )

            wardrobe_config = {
                "W-1 Centered (no return wall)": "centered",
                "W-2 Full wall (wall-to-wall)": "full_wall",
                "W-3 Built-in (return wall)": "built_in",
            }[wardrobe_config_label]

            wardrobe_type = "built_in" if wardrobe_config == "built_in" else "freestanding"
            wardrobe_return_wall_enabled = wardrobe_config == "built_in"
            wardrobe_allow_fallback = st.checkbox(
                "Allow fallback if built-in fails (recommended)",
                value=True
            )

        with st.expander("📺 TV + Dressing + Dresser", expanded=st.session_state.sidebar_expand_all):
            include_tv = st.checkbox("Include TV + TV Unit (auto TV size)", value=bool(st.session_state.include_tv), key='include_tv')
            tv_unit_width = st.number_input(
                "TV Unit Width (mm)",
                800, 2000,
                int(st.session_state.tv_unit_width),
                100,
                key='tv_unit_width',
                disabled=not include_tv
            )

            include_dressing_table = st.checkbox(
                "Include Dressing Table",
                value=bool(st.session_state.include_dressing_table),
                key='include_dressing_table',
                disabled=not include_tv
            )
            dressing_table_width = st.number_input(
                "Dressing Table Width (mm)",
                800, 2000,
                int(st.session_state.dressing_table_width),
                100,
                key='dressing_table_width',
                disabled=(not include_tv or not include_dressing_table)
            )
            dressing_table_side = st.radio(
                "Dressing Table Side",
                ["Right of TV", "Left of TV"],
                disabled=(not include_tv or not include_dressing_table)
            )

            include_dresser = st.checkbox("Include Dresser (low storage)", value=bool(st.session_state.include_dresser), key='include_dresser')
            cold1, cold2 = st.columns(2)
            with cold1:
                    dresser_width = st.number_input(
                        "Dresser Width (mm)",
                        800, 2000,
                        int(st.session_state.dresser_width),
                        100,
                        key='dresser_width',
                        disabled=not include_dresser
                    )
            with cold2:
                    dresser_depth = st.number_input(
                        "Dresser Depth (mm)",
                        350, 700,
                        int(st.session_state.dresser_depth),
                        50,
                        key='dresser_depth',
                        disabled=not include_dresser
                    )

        if include_banquet:
            with st.expander("🪑 Banquet", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    banquet_width = st.number_input("Width (mm)", 1000, 2000, 1400, 50)
                with col2:
                    banquet_depth = st.number_input("Depth (mm)", 300, 800, 500, 50)

        with st.expander("🧱 Internal wall gap", expanded=False):
            internal_wall_gap = st.number_input("Internal Wall Gap (mm)", 100, 500, 200, 50)
        
        st.markdown("### ⚡ Systems")
        
        include_electrical = st.checkbox("Include Electrical", True)
        include_lighting = st.checkbox("Include Lighting", True)
        include_ac = st.checkbox("Include AC", True)
        
        ac_type = "split"  # Default value
        lighting_type = "recessed"  # Default value
        
        if include_ac:
            ac_type = st.selectbox("AC Type", ["split", "concealed"])
        
        if include_lighting:
            lighting_type = st.selectbox("Lighting Type", ["recessed", "pendant", "track"])
        
        st.markdown("---")
        
        # Generate button
        generate_btn = st.button("🚀 GENERATE COMPLETE DESIGN", 
                               type="primary", 
                               use_container_width=True)

# Main content (keep the same tabs structure)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📐 Design", "🏗️ 3D View", "📊 BOQ", "⚡ Systems", "📤 Export"])

# Session state
if 'layout' not in st.session_state:
    st.session_state.layout = None
if 'engine' not in st.session_state:
    st.session_state.engine = None

if generate_btn or st.session_state.layout:
    if generate_btn:
        # Parse inputs
        bed_sizes = {
            "King (1800x2000)": "king",
            "Queen (1600x2000)": "queen",
            "Double (1400x1900)": "double",
            "Single (1200x1900)": "single"
        }
        
        bed_type_val = bed_sizes[bed_type]
        dt_side = "right" if dressing_table_side == "Right of TV" else "left"
        
        try:
            with st.spinner("🔄 Generating complete design with BOQ..."):
                def _run_with_bed(bed_type_val_run: str):
                    engine = BedroomEngine(
                        width=width,
                        depth=depth,
                        height=height,
                        door_from_wall=door_from_wall,
                        door_width=door_width,
                        door_wall=door_wall,
                        door_hinge=door_hinge,
                        door_swing=door_swing,
                        door_open_angle_deg=45,
                        window_wall=window_wall,
                        window_width=window_width,
                        window_sill=window_sill,
                        under_window_use=under_window_use,
                        internal_wall_gap=internal_wall_gap,
                        bed_wall_preference=bed_wall_preference,
                        bed_type=bed_type_val_run,
                        # Designer wardrobe controls
                        wardrobe_mode="auto",  # legacy field (kept for compatibility)
                        wardrobe_type=wardrobe_type,
                        wardrobe_config=wardrobe_config,
                        wardrobe_return_wall_enabled=wardrobe_return_wall_enabled,
                        wardrobe_allow_fallback=wardrobe_allow_fallback,
                        wardrobe_width=wardrobe_width,
                        wardrobe_depth=wardrobe_depth,
                        include_tv=include_tv,
                        include_dressing_table=include_dressing_table,
                        include_dresser=include_dresser,
                        dresser_width=dresser_width if include_dresser else 1200,
                        dresser_depth=dresser_depth if include_dresser else 500,
                        include_chair=include_chair,
                        tv_unit_width=tv_unit_width,
                        dressing_table_width=dressing_table_width,
                        bedside_table_count=bedside_table_count,
                        bedside_table_width=bedside_width,
                        bedside_table_depth=bedside_depth,
                        headboard_width=headboard_width,
                        headboard_height=headboard_height,
                        include_banquet=include_banquet,
                        banquet_width=banquet_width if include_banquet else 1400,
                        banquet_depth=banquet_depth if include_banquet else 500,
                        ac_type=ac_type,
                        lighting_type=lighting_type,
                        include_electrical=include_electrical,
                        include_lighting=include_lighting,
                        include_ac=include_ac
                    )
                    layout = engine.calculate_layout(dressing_table_side=dt_side)
                    return engine, layout

                # Adaptive ladder: if bedside tables are impossible, retry with a smaller bed preset.
                bed_order = ["king", "queen", "double", "single"]
                start_i = bed_order.index(bed_type_val)
                attempts = bed_order[start_i:]

                last_error = None
                engine = None
                layout = None
                for attempt_bed in attempts:
                    try:
                        engine, layout = _run_with_bed(attempt_bed)
                        if attempt_bed != bed_type_val:
                            # write back the adapted choice so UI stays consistent
                            label_map = {
                                "king": "King (1800x2000)",
                                "queen": "Queen (1600x2000)",
                                "double": "Double (1400x1900)",
                                "single": "Single (1200x1900)",
                            }
                            st.session_state['bed_size_label'] = label_map[attempt_bed]
                            st.warning(f"Bed size was reduced to {label_map[attempt_bed]} to fit two bedside tables.")
                        break
                    except Exception as e2:
                        last_error = e2
                        msg = str(e2).lower()
                        # Only ladder-adapt on bedside-table constraints; otherwise stop immediately.
                        if "bedside" not in msg:
                            raise
                        continue

                if layout is None:
                    raise last_error if last_error else Exception("Design failed.")

                st.session_state.layout = layout
                st.session_state.engine = engine

                st.success(f"✅ Design generated! Room ID: {layout['room']['id']}")

                # --- Validation + auto-revert (when engine corrects the user inputs) ---
                issues = layout.get('metadata', {}).get('validation_issues', []) or []
                if issues:
                    # Show all reasons
                    st.warning("Some inputs were adjusted or some items were skipped to respect rules:")
                    for msg in issues:
                        st.write(f"• {msg}")

                    # Auto-update wardrobe width if engine reduced it
                    for msg in issues:
                        if "Wardrobe width was reduced" in msg:
                            try:
                                # Example: "Wardrobe width was reduced from 2400mm to 1800mm ..."
                                parts = msg.replace('mm', '').split()
                                old_w = int(parts[5])
                                new_w = int(parts[7])
                                st.session_state['wardrobe_width'] = new_w
                                st.toast(f"Wardrobe width reverted from {old_w}mm to {new_w}mm to avoid conflicts.")
                            except Exception:
                                pass
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()
    
    # Tab 1: Design
    with tab1:
        st.markdown("### 📐 2D Floor Plan")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig = st.session_state.engine.create_visualization(st.session_state.layout)
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 📊 Design Info")
            
            metadata = st.session_state.layout['metadata']
            room = st.session_state.layout['room']
            
            st.metric("Room Area", f"{room['area_m2']:.2f} m²")
            st.metric("TV Size", f"{metadata.get('tv_size','N/A')}\"")
            st.metric("Viewing Distance", f"{int(metadata.get('viewing_distance',0))}mm")
            
            st.markdown("**Dimensions:**")
            st.write(f"Internal: {room['internal_width']} x {room['internal_depth']} mm")
            st.write(f"External: {room['external_width']} x {room['external_depth']} mm")
            
            st.markdown("**Design Features:**")
            st.write(f"• Bed on {st.session_state.layout['architectural']['bed_wall']['type']} wall")
            st.write(f"• Window on {metadata['window_wall']} wall")
            st.write(f"• Wardrobe mode: {metadata.get('wardrobe_mode','').replace('_',' ').title()}")
            st.write(f"• Bedside tables: {metadata.get('bedside_table_count','N/A')}")
            st.write(f"• Banquet included: {'Yes' if metadata['include_banquet'] else 'No'}")
            
            if metadata.get('validation_issues'):
                with st.expander("⚠️ Issues", expanded=True):
                    for issue in metadata.get('validation_issues', []):
                        st.warning(issue)
    
    # Tab 2: 3D View
    with tab2:
        st.markdown("### 🏗️ 3D Visualization")

        fig_3d = st.session_state.engine.generate_3d_view(st.session_state.layout)

        # Prefer Plotly for true 360° orbit. Fall back to matplotlib if Plotly is unavailable.
        if hasattr(fig_3d, "to_dict") and hasattr(fig_3d, "update_layout"):
            st.plotly_chart(fig_3d, use_container_width=True, config={'scrollZoom': True, 'displaylogo': False})
            st.info("360° Orbit: left-drag rotate (orbit), scroll to zoom, right-drag pan")
        else:
            st.pyplot(fig_3d)
            st.info("Rotate: click+drag, scroll to zoom")
    
    # Tab 3: BOQ
    with tab3:
        st.markdown("### 💰 Bill of Quantities (BOQ)")
        
        boq = st.session_state.layout['boq']
        
        # Display BOQ table
        boq_df = pd.DataFrame(boq['items'])
        
        st.markdown('<div class="boq-table">', unsafe_allow_html=True)
        st.dataframe(boq_df, use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Total cost
        st.markdown(f'<div class="total-cost">TOTAL PROJECT COST: ${boq["total_cost"]:,.2f} {boq["currency"]}</div>', 
                   unsafe_allow_html=True)
        
        # Category breakdown
        st.markdown("### 📊 Cost Breakdown by Category")
        
        category_totals = {}
        for item in boq['items']:
            cat = item['category']
            category_totals[cat] = category_totals.get(cat, 0) + item['total_cost']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pie chart
            fig_pie, ax = plt.subplots(figsize=(8, 6))
            ax.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%',
                  startangle=90, colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444'])
            ax.set_title('Cost Distribution by Category')
            st.pyplot(fig_pie)
        
        with col2:
            st.markdown("**Category Totals:**")
            for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                st.metric(cat, f"${total:,.2f}")
    
    # Tab 4: Systems
    with tab4:
        st.markdown("### ⚡ Systems Design")
        
        systems = st.session_state.layout['systems']
        
        # Electrical Systems
        st.markdown("#### 🔌 Electrical Layout")
        
        if systems['electrical']:
            elec_df = pd.DataFrame(systems['electrical'])
            st.dataframe(elec_df, use_container_width=True)
            
            total_sockets = sum(s['quantity'] for s in systems['electrical'])
            st.info(f"Total Sockets: {total_sockets}")
        else:
            st.warning("No electrical systems included")
        
        st.markdown("---")
        
        # Lighting Systems
        st.markdown("#### 💡 Lighting Design")
        
        if systems['lighting']:
            light_df = pd.DataFrame(systems['lighting'])
            st.dataframe(light_df, use_container_width=True)
            
            total_lights = len(systems['lighting'])
            total_wattage = sum(l['wattage'] for l in systems['lighting'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Lights", total_lights)
            with col2:
                st.metric("Total Load", f"{total_wattage}W")
        else:
            st.warning("No lighting systems included")
        
        st.markdown("---")
        
        # AC Systems
        st.markdown("#### ❄️ Air Conditioning")
        
        if systems['ac']:
            for ac in systems['ac']:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Type", ac['type'].title())
                with col2:
                    st.metric("Capacity", f"{ac['capacity_hp']} HP")
                with col3:
                    st.metric("BTU", f"{ac['capacity_btu']:,}")
                
                st.success(f"✅ AC System: {ac['id']} - {ac['type'].title()} {ac['capacity_hp']} HP ({ac['capacity_btu']} BTU)")
        else:
            st.warning("No AC system included")
    
    # Tab 5: Export
    with tab5:
        st.markdown("### 📤 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 DXF Export")
            st.info("Export your design to AutoCAD-compatible DXF format for professional use")
            
            if st.button("🔽 Generate DXF File", type="primary", use_container_width=True):
                with st.spinner("Generating DXF..."):
                    try:
                        dxf_path = export_to_dxf(st.session_state.layout)
                        
                        # Read DXF file
                        with open(dxf_path, 'rb') as f:
                            dxf_data = f.read()
                        
                        # Provide download button
                        st.download_button(
                            label="📥 Download DXF",
                            data=dxf_data,
                            file_name=f"bedroom_layout_{st.session_state.layout['room']['id']}.dxf",
                            mime="application/dxf",
                            use_container_width=True
                        )
                        
                        st.success("✅ DXF file generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating DXF: {str(e)}")
        
        with col2:
            st.markdown("#### 📊 JSON Export")
            st.info("Export complete layout data as JSON for further processing")
            
            if st.button("🔽 Generate JSON File", type="primary", use_container_width=True):
                try:
                    json_data = json.dumps(st.session_state.layout, indent=2)
                    
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=f"bedroom_layout_{st.session_state.layout['room']['id']}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    
                    st.success("✅ JSON file ready for download!")
                    
                except Exception as e:
                    st.error(f"Error generating JSON: {str(e)}")
        
        st.markdown("---")
        
        st.markdown("#### 📋 Layout Summary")
        
        metadata = st.session_state.layout.get('metadata', {})

        room_id = metadata.get('room_id') or metadata.get('project_id') or st.session_state.layout.get('room', {}).get('id', 'N/A')
        generated_at = metadata.get('generated_at', 'N/A')

        summary = f"""
        **Project ID:** {room_id}
        **Generated:** {generated_at}
        
        **Room Configuration:**
        - Internal Dimensions: {st.session_state.layout['room']['internal_width']} x {st.session_state.layout['room']['internal_depth']} mm
        - External Dimensions: {st.session_state.layout['room']['external_width']} x {st.session_state.layout['room']['external_depth']} mm
        - Height: {st.session_state.layout['room']['height']} mm
        - Area: {st.session_state.layout['room']['area_m2']} m²
        
        **Design Details:**
        - TV Size: {metadata.get('tv_size','N/A')}
        - Viewing Distance: {int(metadata.get('viewing_distance',0))} mm
        - Bed Wall: {str(metadata.get('bed_wall','N/A')).title()}
        - Wardrobe Wall: {str(metadata.get('wardrobe_wall','N/A')).title()}
        - Window Wall: {str(metadata.get('window_wall','N/A')).title()}
        - Door Wall: {str(metadata.get('door_wall','N/A')).title()}
        - Bedside Tables: {metadata.get('bedside_table_count','N/A')}
        - Banquet Included: {'Yes' if metadata.get('include_banquet', False) else 'No'}
        
        **BOQ Total:** ${st.session_state.layout['boq']['total_cost']:,.2f}
        """
        
        st.markdown(summary)
        
        if metadata.get('validation_issues'):
            st.warning("⚠️ Validation Issues:")
            for issue in metadata.get('validation_issues', []):
                st.write(f"- {issue}")

else:
    # Welcome screen (keep the same)
    pass

# Footer (keep the same)
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <p>🏠 <strong>Professional Bedroom Design System</strong> | Complete BOQ | TV Size Optimization | Systems Design | DXF Export</p>
    <p>📊 <strong>All Requirements Implemented:</strong> TV sizing, Viewing distance, Unique IDs, BOQ, Systems, DXF, 3D</p>
    <p>💡 <strong>How to use:</strong> Set parameters → Generate → Check BOQ → Export DXF → Share with team</p>
</div>
""", unsafe_allow_html=True)