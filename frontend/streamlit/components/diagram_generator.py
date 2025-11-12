"""
Diagram Generator UI Component for Streamlit
Beautiful interface for creating, editing, and exporting diagrams
"""
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, List
import base64
from datetime import datetime

from backend.tools.diagram_generator import diagram_generator
from frontend.streamlit.components.ui_utils import (
    show_toast,
    render_empty_state,
    render_loading_skeleton
)


class DiagramGeneratorUI:
    """Diagram generator interface with modern UI"""
    
    # Default diagram code for new diagrams
    DEFAULT_CODE = {
        'mermaid': '''flowchart TD
    Start([Start]) --> Input[/Enter Data/]
    Input --> Process[Process]
    Process --> End([End])''',
        'plantuml': '''@startuml
title Simple Diagram
start
:Action;
stop
@enduml'''
    }
    
    @staticmethod
    def render():
        """Main render method for diagram generator"""
        if 'user_id' not in st.session_state:
            st.warning("⚠️ Please log in to access the diagram generator.")
            return
        
        # Initialize session state
        DiagramGeneratorUI._init_session_state()
        
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>📊 Diagram Generator</h1>
            <p style='color: var(--color-text-secondary);'>
                Create beautiful diagrams using Mermaid, PlantUML, and more
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Create main layout
        tab1, tab2, tab3, tab4 = st.tabs([
            "✏️ Create Diagram",
            "📚 Templates",
            "💾 My Diagrams",
            "ℹ️ Help & Examples"
        ])
        
        with tab1:
            DiagramGeneratorUI.render_diagram_editor()
        
        with tab2:
            DiagramGeneratorUI.render_templates()
        
        with tab3:
            DiagramGeneratorUI.render_saved_diagrams()
        
        with tab4:
            DiagramGeneratorUI.render_help()
    
    @staticmethod
    def _init_session_state():
        """Initialize session state variables"""
        defaults = {
            'diagram_code': '',
            'diagram_type': 'mermaid',
            'current_diagram_path': None,
            'diagram_history': [],
            'show_preview': True,
            'auto_preview': True,
            'export_format': 'svg'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def render_diagram_editor():
        """Render the main diagram editor interface"""
        
        # Editor header with controls
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            diagram_type = st.selectbox(
                "📋 Diagram Type",
                options=['mermaid', 'plantuml', 'graphviz', 'blockdiag', 'bpmn'],
                index=['mermaid', 'plantuml', 'graphviz', 'blockdiag', 'bpmn'].index(
                    st.session_state.diagram_type
                ),
                help="Select the type of diagram to create"
            )
            st.session_state.diagram_type = diagram_type
        
        with col2:
            output_format = st.selectbox(
                "📄 Export Format",
                options=['svg', 'png'],
                index=['svg', 'png'].index(st.session_state.export_format),
                help="Format for exporting the diagram"
            )
            st.session_state.export_format = output_format
        
        with col3:
            auto_preview = st.checkbox(
                "🔄 Auto",
                value=st.session_state.auto_preview,
                help="Automatically preview as you type"
            )
            st.session_state.auto_preview = auto_preview
        
        with col4:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear editor"):
                st.session_state.diagram_code = ''
                st.rerun()
        
        st.divider()
        
        # Two-column layout: Editor and Preview
        col_editor, col_preview = st.columns([1, 1])
        
        with col_editor:
            st.markdown("### ✏️ Editor")
            
            # Load default code if empty
            if not st.session_state.diagram_code:
                st.session_state.diagram_code = DiagramGeneratorUI.DEFAULT_CODE.get(
                    diagram_type,
                    DiagramGeneratorUI.DEFAULT_CODE['mermaid']
                )
            
            # Code editor
            diagram_code = st.text_area(
                "Diagram Code",
                value=st.session_state.diagram_code,
                height=400,
                help="Enter your diagram code here",
                label_visibility="collapsed",
                key="diagram_editor"
            )
            
            # Update session state
            if diagram_code != st.session_state.diagram_code:
                st.session_state.diagram_code = diagram_code
            
            # Action buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                generate_btn = st.button(
                    "🎨 Generate",
                    use_container_width=True,
                    type="primary",
                    help="Generate diagram"
                )
            
            with btn_col2:
                validate_btn = st.button(
                    "✓ Validate",
                    use_container_width=True,
                    help="Validate diagram syntax"
                )
            
            with btn_col3:
                export_btn = st.button(
                    "💾 Export",
                    use_container_width=True,
                    help="Export diagram in selected format"
                )
            
            # Handle validation
            if validate_btn:
                is_valid, error = diagram_generator.validate_diagram_code(
                    diagram_code,
                    diagram_type
                )
                if is_valid:
                    st.success("✅ Diagram code is valid!")
                else:
                    st.error(f"❌ Validation Error: {error}")
        
        with col_preview:
            st.markdown("### 👁️ Preview")
            
            # Generate preview
            should_preview = (
                (auto_preview and diagram_code) or
                generate_btn or
                export_btn
            )
            
            if should_preview:
                if not diagram_code.strip():
                    st.warning("⚠️ Please enter diagram code to preview")
                else:
                    # Validate first
                    is_valid, error = diagram_generator.validate_diagram_code(
                        diagram_code,
                        diagram_type
                    )
                    
                    if not is_valid:
                        st.error(f"❌ {error}")
                    else:
                        # Show loading spinner
                        with st.spinner("🎨 Generating diagram..."):
                            success, file_path, error = diagram_generator.generate_diagram(
                                diagram_code,
                                diagram_type,
                                output_format
                            )
                        
                        if success:
                            st.session_state.current_diagram_path = file_path
                            
                            # Display diagram
                            DiagramGeneratorUI._display_diagram(file_path, output_format)
                            
                            # Show diagram info
                            diagram_info = diagram_generator.get_diagram_info(file_path)
                            if diagram_info:
                                st.caption(
                                    f"📊 Size: {diagram_info['size_kb']} KB | "
                                    f"Format: {diagram_info['format'].upper()}"
                                )
                            
                            # Download button
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            st.download_button(
                                "⬇️ Download Diagram",
                                data=file_data,
                                file_name=Path(file_path).name,
                                mime=f"image/{output_format}",
                                use_container_width=True
                            )
                            
                            # Export to multiple formats
                            if export_btn:
                                st.markdown("---")
                                st.markdown("#### 📦 Export All Formats")
                                
                                formats = ['svg', 'png']
                                results = diagram_generator.export_diagram(
                                    diagram_code,
                                    diagram_type,
                                    formats
                                )
                                
                                export_cols = st.columns(len(formats))
                                for idx, (fmt, path) in enumerate(results.items()):
                                    with export_cols[idx]:
                                        if path:
                                            with open(path, 'rb') as f:
                                                data = f.read()
                                            st.download_button(
                                                f"⬇️ {fmt.upper()}",
                                                data=data,
                                                file_name=Path(path).name,
                                                mime=f"image/{fmt}",
                                                use_container_width=True,
                                                key=f"export_{fmt}"
                                            )
                                
                                st.success("✅ Diagram ready for export!")
                        
                        else:
                            st.error(f"❌ Error: {error}")
                            st.info("💡 Tip: Check the Help & Examples tab for syntax reference")
            
            else:
                # Show empty state
                render_empty_state(
                    icon="🎨",
                    title="No Preview",
                    description="Click 'Generate' or enable 'Auto Preview' to see your diagram"
                )
    
    @staticmethod
    def _display_diagram(file_path: str, format: str):
        """Display diagram in the preview area"""
        try:
            if format == 'svg':
                # Display SVG directly
                with open(file_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                st.markdown(
                    f'<div style="background: white; padding: 1rem; border-radius: 10px; text-align: center;">{svg_content}</div>',
                    unsafe_allow_html=True
                )
            else:
                # Display PNG
                st.image(file_path, use_column_width=True)
        
        except Exception as e:
            st.error(f"Error displaying diagram: {str(e)}")
    
    @staticmethod
    def render_templates():
        """Render diagram templates library"""
        st.markdown("### 📚 Diagram Templates")
        st.markdown("Click any template to load it into the editor")
        
        templates = diagram_generator.get_diagram_templates()
        
        # Group templates by type
        mermaid_templates = {k: v for k, v in templates.items() if v['type'] == 'mermaid'}
        plantuml_templates = {k: v for k, v in templates.items() if v['type'] == 'plantuml'}
        other_templates = {k: v for k, v in templates.items() if v['type'] not in ['mermaid', 'plantuml']}
        
        # Mermaid templates
        if mermaid_templates:
            st.markdown("#### 🔷 Mermaid Templates")
            DiagramGeneratorUI._render_template_grid(mermaid_templates)
        
        # PlantUML templates
        if plantuml_templates:
            st.markdown("#### 🔶 PlantUML Templates")
            DiagramGeneratorUI._render_template_grid(plantuml_templates)
        
        # Other templates
        if other_templates:
            st.markdown("#### 🔸 Other Templates")
            DiagramGeneratorUI._render_template_grid(other_templates)
    
    @staticmethod
    def _render_template_grid(templates: Dict):
        """Render template cards in a grid"""
        # Create grid layout (2 columns)
        template_items = list(templates.items())
        
        for i in range(0, len(template_items), 2):
            cols = st.columns(2)
            
            for col_idx, col in enumerate(cols):
                if i + col_idx < len(template_items):
                    template_id, template = template_items[i + col_idx]
                    
                    with col:
                        with st.container():
                            st.markdown(f"""
                            <div style='
                                background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(157, 78, 221, 0.05));
                                border: 1px solid rgba(255, 255, 255, 0.1);
                                border-radius: 15px;
                                padding: 1rem;
                                margin-bottom: 1rem;
                                transition: all 0.3s ease;
                            '>
                                <h4 style='margin: 0 0 0.5rem 0;'>{template['name']}</h4>
                                <p style='color: var(--color-text-secondary); font-size: 0.9rem; margin: 0;'>
                                    {template['description']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(
                                "📋 Use Template",
                                key=f"template_{template_id}",
                                use_container_width=True
                            ):
                                st.session_state.diagram_code = template['code']
                                st.session_state.diagram_type = template['type']
                                show_toast("Template loaded! Switch to 'Create Diagram' tab", "success")
                                st.rerun()
                            
                            # Show preview in expander
                            with st.expander("👁️ Preview Code"):
                                st.code(template['code'], language=template['type'])
    
    @staticmethod
    def render_saved_diagrams():
        """Render saved diagrams gallery"""
        st.markdown("### 💾 My Diagrams")
        
        output_dir = Path("output/diagrams")
        
        if not output_dir.exists() or not any(output_dir.iterdir()):
            render_empty_state(
                icon="📊",
                title="No Saved Diagrams",
                description="Create your first diagram in the 'Create Diagram' tab!"
            )
            return
        
        # Get all diagram files
        diagram_files = sorted(
            output_dir.glob("*.*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not diagram_files:
            render_empty_state(
                icon="📊",
                title="No Saved Diagrams",
                description="Create your first diagram in the 'Create Diagram' tab!"
            )
            return
        
        st.markdown(f"**Found {len(diagram_files)} diagram(s)**")
        st.divider()
        
        # Display diagrams in grid (2 columns)
        for i in range(0, len(diagram_files), 2):
            cols = st.columns(2)
            
            for col_idx, col in enumerate(cols):
                if i + col_idx < len(diagram_files):
                    file_path = diagram_files[i + col_idx]
                    
                    with col:
                        DiagramGeneratorUI._render_diagram_card(file_path)
    
    @staticmethod
    def _render_diagram_card(file_path: Path):
        """Render a single diagram card"""
        diagram_info = diagram_generator.get_diagram_info(str(file_path))
        
        if not diagram_info:
            return
        
        with st.container():
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(157, 78, 221, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 1rem;
                margin-bottom: 1rem;
            '>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h4 style='margin: 0;'>📊 {diagram_info['filename']}</h4>
                </div>
                <p style='color: var(--color-text-secondary); font-size: 0.85rem; margin: 0.5rem 0;'>
                    Size: {diagram_info['size_kb']} KB | Format: {diagram_info['format'].upper()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Preview
            try:
                if diagram_info['format'] == 'svg':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    st.markdown(
                        f'<div style="background: white; padding: 0.5rem; border-radius: 10px; max-height: 200px; overflow: hidden;">{svg_content}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.image(str(file_path), use_column_width=True)
            except:
                st.warning("Unable to preview diagram")
            
            # Actions
            action_cols = st.columns([2, 1])
            
            with action_cols[0]:
                # Download button
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                st.download_button(
                    "⬇️ Download",
                    data=file_data,
                    file_name=file_path.name,
                    mime=f"image/{diagram_info['format']}",
                    use_container_width=True,
                    key=f"download_{file_path.name}"
                )
            
            with action_cols[1]:
                # Delete button
                if st.button(
                    "🗑️",
                    key=f"delete_{file_path.name}",
                    use_container_width=True,
                    help="Delete diagram"
                ):
                    try:
                        file_path.unlink()
                        st.success("✅ Diagram deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting: {str(e)}")
    
    @staticmethod
    def render_help():
        """Render help and documentation"""
        st.markdown("### ℹ️ Help & Examples")
        
        help_tabs = st.tabs([
            "📖 Getting Started",
            "🔷 Mermaid Syntax",
            "🔶 PlantUML Syntax",
            "💡 Tips & Tricks"
        ])
        
        with help_tabs[0]:
            st.markdown("""
            ## Getting Started with Diagram Generator
            
            ### Quick Start
            1. **Choose a diagram type** from the dropdown (Mermaid, PlantUML, etc.)
            2. **Write your diagram code** in the editor or use a template
            3. **Click 'Generate'** to see the preview
            4. **Export** your diagram in SVG or PNG format
            
            ### Features
            - ✏️ **Live Editor** - Write diagram code with syntax highlighting
            - 🔄 **Auto Preview** - See changes in real-time
            - 📚 **Templates** - Start with pre-made diagram templates
            - 💾 **Export** - Download diagrams as SVG or PNG
            - 📊 **Gallery** - View and manage your saved diagrams
            
            ### Supported Diagram Types
            - **Mermaid** - Flowcharts, sequence diagrams, class diagrams, etc.
            - **PlantUML** - Comprehensive UML diagrams
            - **Graphviz** - Graph visualization
            - **BlockDiag** - Simple block diagrams
            - **BPMN** - Business process diagrams
            """)
        
        with help_tabs[1]:
            st.markdown("""
            ## Mermaid Diagram Syntax
            
            ### Flowchart
            ```mermaid
            flowchart LR
                A[Start] --> B{Decision}
                B -->|Yes| C[Action 1]
                B -->|No| D[Action 2]
                C --> E[End]
                D --> E
            ```
            
            ### Sequence Diagram
            ```mermaid
            sequenceDiagram
                Alice->>John: Hello John!
                John-->>Alice: Hi Alice!
                Alice->>John: How are you?
            ```
            
            ### Class Diagram
            ```mermaid
            classDiagram
                Animal <|-- Dog
                Animal <|-- Cat
                Animal : +int age
                Animal : +String name
                Animal: +makeSound()
            ```
            
            ### State Diagram
            ```mermaid
            stateDiagram-v2
                [*] --> Still
                Still --> Moving
                Moving --> Still
                Moving --> Crash
                Crash --> [*]
            ```
            
            ### Gantt Chart
            ```mermaid
            gantt
                title Project Timeline
                dateFormat YYYY-MM-DD
                section Phase 1
                Task 1    :2024-01-01, 30d
                Task 2    :2024-02-01, 20d
            ```
            
            **Resources:**
            - [Mermaid Official Documentation](https://mermaid.js.org/)
            - [Mermaid Live Editor](https://mermaid.live/)
            """)
        
        with help_tabs[2]:
            st.markdown("""
            ## PlantUML Diagram Syntax
            
            ### Class Diagram
            ```plantuml
            @startuml
            class Animal {
              +String name
              +void makeSound()
            }
            class Dog extends Animal
            class Cat extends Animal
            @enduml
            ```
            
            ### Sequence Diagram
            ```plantuml
            @startuml
            Alice -> Bob: Request
            Bob --> Alice: Response
            @enduml
            ```
            
            ### Use Case Diagram
            ```plantuml
            @startuml
            actor User
            User --> (Login)
            User --> (Browse)
            @enduml
            ```
            
            ### Activity Diagram
            ```plantuml
            @startuml
            start
            :Action 1;
            if (condition?) then (yes)
              :Action 2;
            else (no)
              :Action 3;
            endif
            stop
            @enduml
            ```
            
            **Resources:**
            - [PlantUML Official Documentation](https://plantuml.com/)
            - [PlantUML Online Server](http://www.plantuml.com/plantuml/)
            """)
        
        with help_tabs[3]:
            st.markdown("""
            ## Tips & Tricks
            
            ### Best Practices
            
            #### 1. Start with Templates
            - Use the **Templates** tab to find pre-made diagrams
            - Modify templates to fit your needs
            - Save time on boilerplate code
            
            #### 2. Use Auto Preview
            - Enable **Auto Preview** for real-time feedback
            - Disable it for large diagrams to save resources
            
            #### 3. Validate Before Generating
            - Click **Validate** to check syntax errors
            - Fix errors before generating
            
            #### 4. Choose the Right Format
            - **SVG** - Best for web, scalable, smaller file size
            - **PNG** - Best for presentations, documents
            
            #### 5. Organize Your Diagrams
            - Use descriptive names in your diagram code
            - Export with meaningful filenames
            - Keep a backup of your diagram code
            
            ### Common Issues
            
            #### Diagram Not Rendering
            - Check syntax with the Validate button
            - Ensure all tags are closed (PlantUML)
            - Check for typos in keywords
            
            #### Preview Taking Too Long
            - Disable Auto Preview for complex diagrams
            - Simplify your diagram
            - Try a different format
            
            #### Export Issues
            - Make sure the diagram generates successfully first
            - Try both SVG and PNG formats
            - Check your internet connection (diagrams are rendered online)
            
            ### Keyboard Shortcuts
            - `Ctrl + Enter` - Generate diagram
            - `Ctrl + S` - Save (browser default)
            - `Ctrl + A` - Select all text in editor
            
            ### Need Help?
            - Check the documentation links in other tabs
            - Use the validation feature to debug syntax
            - Start with simple examples and build up
            """)


def render_diagram_generator():
    """Wrapper function to render diagram generator UI"""
    DiagramGeneratorUI.render()

