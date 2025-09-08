import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime
import openpyxl
from typing import List, Dict, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="File Merger - by Bot Aom",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Earth Tone theme
def load_css():
    st.markdown("""
    <style>
    :root {
        --earth-brown: #8B4513;
        --warm-beige: #F5E6D3;
        --sand: #E5D4B1;
        --sage: #9CAF88;
        --clay: #CD853F;
        --stone: #A0826D;
        --dark-brown: #654321;
        --light-cream: #FDF5E6;
    }
    
    .main-header {
        background: linear-gradient(135deg, #8B4513 0%, #CD853F 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #F5E6D3 0%, #E5D4B1 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #9CAF88;
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: #F0FFF4;
        border: 1px solid #9AE6B4;
        color: #276749;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #FFF5F5;
        border: 1px solid #FEB2B2;
        color: #C53030;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .file-info {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #9CAF88;
        box-shadow: 0 2px 8px rgba(139, 69, 19, 0.1);
        margin: 1rem 0;
    }
    
    .file-info.disabled {
        background: #f8f8f8;
        border-left: 4px solid #ccc;
        opacity: 0.6;
    }
    
    .header-mapping-section {
        background: #FDF5E6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #E5D4B1;
    }
    
    .sample-data {
        background: white;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #ddd;
    }
    
    .header-match {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: bold;
    }
    
    .header-no-match {
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        margin: 0.1rem;
        display: inline-block;
        font-size: 0.85rem;
        font-weight: bold;
    }
    
    .file-selector {
        background: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #bee5eb;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit style elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

class FileMerger:
    def __init__(self):
        self.uploaded_files = []
        self.processed_data = {}
        self.merged_df = None
        self.header_mapping = {}
        
    def process_uploaded_files(self, files) -> Dict:
        """Process uploaded files and extract data"""
        processed = {}
        
        for file in files:
            file_info = {
                'name': file.name,
                'size': file.size,
                'type': self.get_file_type(file.name)
            }
            
            try:
                if file_info['type'] == 'csv':
                    df = pd.read_csv(file)
                    file_info['sheets'] = ['Sheet1']
                    file_info['data'] = {'Sheet1': df}
                    
                elif file_info['type'] == 'excel':
                    # Read all sheets
                    excel_file = pd.ExcelFile(file)
                    file_info['sheets'] = excel_file.sheet_names
                    file_info['data'] = {}
                    
                    for sheet in excel_file.sheet_names:
                        df = pd.read_excel(file, sheet_name=sheet)
                        file_info['data'][sheet] = df
                        
                processed[file.name] = file_info
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
                
        return processed
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        if filename.lower().endswith('.csv'):
            return 'csv'
        elif filename.lower().endswith(('.xlsx', '.xls')):
            return 'excel'
        return 'unknown'
    
    def analyze_headers(self, processed_data: Dict, selected_sheets: Dict, selected_files: Dict) -> Tuple[List[str], bool]:
        """Analyze headers across all selected sheets"""
        all_headers = set()
        file_headers = {}
        
        # Only analyze selected files
        for filename, file_info in processed_data.items():
            if selected_files.get(filename, True):  # Default to True if not specified
                sheet_name = selected_sheets.get(filename, file_info['sheets'][0])
                if sheet_name in file_info['data']:
                    df = file_info['data'][sheet_name]
                    headers = list(df.columns)
                    file_headers[filename] = headers
                    all_headers.update(headers)
        
        # Check for header consistency
        all_headers_list = list(all_headers)
        has_mismatch = False
        
        if len(file_headers) > 1:  # Only check if we have multiple files
            reference_headers = set(next(iter(file_headers.values())))
            for filename, headers in file_headers.items():
                if set(headers) != reference_headers:
                    has_mismatch = True
                    break
                    
        return all_headers_list, has_mismatch, file_headers
    
    def get_header_match_status(self, header: str, all_file_headers: Dict, current_filename: str) -> str:
        """Check if header exists in other files"""
        other_files = [f for f in all_file_headers.keys() if f != current_filename]
        
        if not other_files:
            return "single_file"
        
        exists_in_others = any(header in all_file_headers[f] for f in other_files)
        return "match" if exists_in_others else "no_match"
    
    def merge_files(self, processed_data: Dict, selected_sheets: Dict, selected_files: Dict, header_mapping: Dict = None, excluded_headers: Dict = None) -> pd.DataFrame:
        """Merge all files into a single DataFrame"""
        merged_dfs = []
        
        for filename, file_info in processed_data.items():
            # Only merge selected files
            if selected_files.get(filename, True):
                sheet_name = selected_sheets.get(filename, file_info['sheets'][0])
                if sheet_name in file_info['data']:
                    df = file_info['data'][sheet_name].copy()
                    
                    # Remove excluded headers first
                    if excluded_headers and filename in excluded_headers:
                        columns_to_keep = [col for col in df.columns if col not in excluded_headers[filename]]
                        df = df[columns_to_keep]
                    
                    # Apply header mapping if provided
                    if header_mapping and filename in header_mapping:
                        df.rename(columns=header_mapping[filename], inplace=True)
                    
                    # Add source file column
                    df['_source_file'] = filename
                    merged_dfs.append(df)
        
        if merged_dfs:
            return pd.concat(merged_dfs, ignore_index=True, sort=False)
        return pd.DataFrame()
    
    def create_download_link(self, df: pd.DataFrame, filename: str) -> str:
        """Create download link for merged file"""
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">ดาวน์โหลดไฟล์ที่รวมแล้ว</a>'
        return href

def main():
    load_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📁 File Merger - by Bot Aom</h1>
        <p>รวมไฟล์ CSV และ Excel หลายไฟล์เข้าด้วยกัน</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'merger' not in st.session_state:
        st.session_state.merger = FileMerger()
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = {}
    if 'merged_df' not in st.session_state:
        st.session_state.merged_df = None
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = {}
    
    merger = st.session_state.merger
    
    # Sidebar for file upload and settings
    with st.sidebar:
        st.header("📤 อัปโหลดไฟล์")
        uploaded_files = st.file_uploader(
            "เลือกไฟล์ CSV หรือ Excel",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="รองรับไฟล์ CSV และ Excel หลายไฟล์"
        )
        
        if uploaded_files:
            if len(uploaded_files) != len(st.session_state.get('last_uploaded', [])):
                st.session_state.processed_data = merger.process_uploaded_files(uploaded_files)
                st.session_state.last_uploaded = uploaded_files
                st.session_state.merged_df = None
                # Initialize selected files to all True
                st.session_state.selected_files = {f.name: True for f in uploaded_files}
    
    # Main content
    if st.session_state.processed_data:
        # File Selection Section
        if len(st.session_state.processed_data) > 1:
            st.header("🎯 เลือกไฟล์สำหรับการรวม")
            st.markdown("""
            <div class="file-selector">
                <h4 style="margin-top: 0; color: #0f5132;">📋 เลือกไฟล์ที่ต้องการรวม</h4>
                <p style="margin-bottom: 0; color: #0f5132;">คุณสามารถเลือกไฟล์ที่ต้องการรวมได้ หากไม่ต้องการรวมไฟล์ใดให้ยกเลิกการเลือก</p>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(min(len(st.session_state.processed_data), 3))
            
            for i, (filename, file_info) in enumerate(st.session_state.processed_data.items()):
                with cols[i % 3]:
                    selected = st.checkbox(
                        f"✅ {filename}",
                        value=st.session_state.selected_files.get(filename, True),
                        key=f"select_{filename}",
                        help=f"ขนาด: {file_info['size']/1024:.1f} KB"
                    )
                    st.session_state.selected_files[filename] = selected
            
            # Show selection summary
            selected_count = sum(st.session_state.selected_files.values())
            total_count = len(st.session_state.processed_data)
            
            if selected_count == 0:
                st.error("⚠️ กรุณาเลือกไฟล์อย่างน้อย 1 ไฟล์")
            elif selected_count < total_count:
                st.info(f"📊 เลือกแล้ว {selected_count} จาก {total_count} ไฟล์")
        else:
            # Single file - auto select
            filename = list(st.session_state.processed_data.keys())[0]
            st.session_state.selected_files = {filename: True}
        
        # File information section
        st.header("📋 ไฟล์ที่อัปโหลด")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_sheets = {}
            
            for filename, file_info in st.session_state.processed_data.items():
                is_selected = st.session_state.selected_files.get(filename, True)
                
                with st.expander(f"{'✅' if is_selected else '❌'} {filename}", expanded=is_selected):
                    col_info, col_sheet = st.columns([2, 1])
                    
                    with col_info:
                        css_class = "file-info" if is_selected else "file-info disabled"
                        status_text = "✅ เลือกสำหรับการรวม" if is_selected else "❌ ไม่รวมในการประมวลผล"
                        st.markdown(f"""
                        <div class="{css_class}">
                            <strong>สถานะ:</strong> {status_text}<br>
                            <strong>ขนาด:</strong> {file_info['size']/1024:.2f} KB<br>
                            <strong>ประเภท:</strong> {file_info['type'].upper()}<br>
                            <strong>จำนวน Sheets:</strong> {len(file_info['sheets'])}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_sheet:
                        if len(file_info['sheets']) > 1:
                            selected_sheet = st.selectbox(
                                "เลือก Sheet:",
                                file_info['sheets'],
                                key=f"sheet_{filename}",
                                index=0,
                                disabled=not is_selected
                            )
                            selected_sheets[filename] = selected_sheet
                        else:
                            selected_sheets[filename] = file_info['sheets'][0]
                            st.info(f"Sheet: {file_info['sheets'][0]}")
                    
                    # Show data preview only for selected files
                    if is_selected:
                        sheet_name = selected_sheets[filename]
                        if sheet_name in file_info['data']:
                            df = file_info['data'][sheet_name]
                            st.write(f"**Preview ({len(df)} แถว, {len(df.columns)} คอลัมน์):**")
                            st.dataframe(df.head(3), use_container_width=True)
                    else:
                        st.markdown("*ไฟล์นี้จะไม่ถูกรวมในการประมวลผล*")
        
        with col2:
            # Statistics for selected files only
            selected_files_data = {k: v for k, v in st.session_state.processed_data.items() 
                                 if st.session_state.selected_files.get(k, True)}
            
            total_files = len(selected_files_data)
            total_records = sum([
                len(file_info['data'][selected_sheets.get(filename, file_info['sheets'][0])]) 
                for filename, file_info in selected_files_data.items()
                if selected_sheets.get(filename, file_info['sheets'][0]) in file_info['data']
            ]) if selected_files_data else 0
            
            excluded_files = len(st.session_state.processed_data) - total_files
            
            st.markdown(f"""
            <div class="stat-card">
                <h3>📊 สถิติ</h3>
                <p><strong>ไฟล์ที่เลือก:</strong> {total_files}</p>
                <p><strong>ไฟล์ที่ไม่เลือก:</strong> {excluded_files}</p>
                <p><strong>จำนวนแถวรวม:</strong> {total_records:,}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Header analysis - only for selected files
        if any(st.session_state.selected_files.values()):
            st.header("🔍 การวิเคราะห์ Headers")
            
            all_headers, has_mismatch, file_headers = merger.analyze_headers(
                st.session_state.processed_data, 
                selected_sheets,
                st.session_state.selected_files
            )
            
            if has_mismatch and len(file_headers) > 1:
                st.markdown("""
                <div class="warning-box">
                    ⚠️ พบความไม่สอดคล้องของ Headers - กรุณาตรวจสอบและปรับแต่ง
                </div>
                """, unsafe_allow_html=True)
                
                # Show header comparison with color coding
                st.subheader("🎨 เปรียบเทียบ Headers (สีเขียว = มีในไฟล์อื่น, สีแดง = ไม่มีในไฟล์อื่น)")
                
                for filename, headers in file_headers.items():
                    with st.expander(f"Headers ของ {filename} ({len(headers)} headers)"):
                        # Create a nice display with color coding
                        header_html = "<div style='display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0;'>"
                        
                        for header in headers:
                            match_status = merger.get_header_match_status(header, file_headers, filename)
                            
                            if match_status == "match":
                                css_class = "header-match"
                                icon = "✅"
                            elif match_status == "no_match":
                                css_class = "header-no-match"  
                                icon = "❌"
                            else:  # single file
                                css_class = "header-match"
                                icon = "📄"
                            
                            header_html += f'<span class="{css_class}">{icon} {header}</span>'
                        
                        header_html += "</div>"
                        st.markdown(header_html, unsafe_allow_html=True)
                        
                        # Show statistics
                        matched_headers = [h for h in headers if merger.get_header_match_status(h, file_headers, filename) == "match"]
                        unmatched_headers = [h for h in headers if merger.get_header_match_status(h, file_headers, filename) == "no_match"]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success(f"✅ Headers ที่มีในไฟล์อื่น: {len(matched_headers)}")
                        with col2:
                            if unmatched_headers:
                                st.error(f"❌ Headers ที่ไม่มีในไฟล์อื่น: {len(unmatched_headers)}")
                            else:
                                st.success("🎉 ทุก Headers มีในไฟล์อื่น")
                
                # Enhanced Header mapping interface
                st.subheader("🔧 ปรับแต่ง Headers สำหรับการรวมไฟล์")
                
                st.markdown("""
                <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h4 style="color: #1E40AF; margin: 0;">📝 วิธีใช้งาน:</h4>
                    <p style="margin: 0.5rem 0 0 0;">
                    1. ดูตัวอย่างข้อมูลแต่ละไฟล์<br>
                    2. เลือกว่า Header ไหนจะใช้ หรือลบทิ้ง<br>
                    3. จับคู่ Headers ที่มีความหมายเหมือนกัน<br>
                    4. <strong style="color: #DC2626;">Headers สีแดงคือไม่มีในไฟล์อื่น</strong> - ควรพิจารณาจับคู่หรือลบ
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                header_mapping = {}
                excluded_headers = {}
                
                for filename, headers in file_headers.items():
                    st.markdown("---")
                    
                    # File header with match statistics
                    matched_count = len([h for h in headers if merger.get_header_match_status(h, file_headers, filename) == "match"])
                    unmatched_count = len(headers) - matched_count
                    
                    st.markdown(f"### 📁 {filename}")
                    
                    if unmatched_count > 0:
                        st.markdown(f"⚠️ **มี {unmatched_count} headers ที่ไม่ตรงกับไฟล์อื่น** (แสดงเป็นสีแดงด้านล่าง)")
                    else:
                        st.markdown("✅ **ทุก headers ตรงกับไฟล์อื่น**")
                    
                    # Get sample data for this file
                    sheet_name = selected_sheets.get(filename, st.session_state.processed_data[filename]['sheets'][0])
                    sample_df = st.session_state.processed_data[filename]['data'][sheet_name].head(5)
                    
                    # Show sample data first
                    with st.expander(f"👁️ ดูตัวอย่างข้อมูล 5 แถวแรก", expanded=False):
                        st.dataframe(sample_df, use_container_width=True)
                    
                    st.write("**⚙️ จัดการ Headers:**")
                    
                    file_mapping = {}
                    file_excluded = []
                    
                    # Create a clean table-like interface
                    for i, header in enumerate(headers):
                        match_status = merger.get_header_match_status(header, file_headers, filename)
                        
                        with st.container():
                            col1, col2, col3 = st.columns([2, 2, 3])
                            
                            with col1:
                                # Show header with color coding
                                if match_status == "match":
                                    st.markdown(f"✅ **`{header}`**")
                                    st.caption("🟢 มีในไฟล์อื่น")
                                elif match_status == "no_match":
                                    st.markdown(f"❌ **`{header}`**")
                                    st.caption("🔴 ไม่มีในไฟล์อื่น - ควรพิจารณา")
                                else:
                                    st.markdown(f"📄 **`{header}`**")
                                    st.caption("📁 ไฟล์เดียว")
                                
                                # Show sample values
                                if header in sample_df.columns:
                                    sample_values = sample_df[header].dropna().head(3).tolist()
                                    if sample_values:
                                        st.caption(f"ตัวอย่าง: {', '.join(str(v)[:15] + ('...' if len(str(v)) > 15 else '') for v in sample_values)}")
                                    else:
                                        st.caption("ไม่มีข้อมูล")
                            
                            with col2:
                                # Action selection with default based on match status
                                default_action = 0 if match_status == "match" else 0  # Always default to "ใช้งาน"
                                
                                action = st.selectbox(
                                    "การดำเนินการ:",
                                    ["✅ ใช้งาน", "❌ ลบทิ้ง"],
                                    key=f"action_{filename}_{i}",
                                    index=default_action,
                                    label_visibility="collapsed",
                                    help="เลือกว่าจะใช้ header นี้หรือลบทิ้ง"
                                )
                            
                            with col3:
                                if action == "✅ ใช้งาน":
                                    # Create mapping options
                                    mapping_options = []
                                    mapping_options.append(f"📌 ใช้ชื่อเดิม: {header}")
                                    
                                    # Add other headers as mapping options (prioritize matching ones)
                                    matching_headers = [h for h in all_headers if h != header]
                                    for other_header in sorted(matching_headers):
                                        mapping_options.append(f"🔗 จับคู่กับ: {other_header}")
                                    
                                    mapping_options.append("✏️ สร้างชื่อใหม่")
                                    
                                    # Set default selection for unmatched headers
                                    default_mapping = 0
                                    if match_status == "no_match" and len(matching_headers) > 0:
                                        # Suggest the first available header for mapping
                                        st.info(f"💡 แนะนำ: header นี้ไม่มีในไฟล์อื่น คลิกเพื่อเลือกการจับคู่")
                                    
                                    selected_mapping = st.selectbox(
                                        "เลือกการจับคู่:",
                                        mapping_options,
                                        key=f"map_{filename}_{i}",
                                        index=default_mapping,
                                        label_visibility="collapsed",
                                        help="เลือกว่าจะใช้ชื่อเดิม จับคู่กับ header อื่น หรือสร้างชื่อใหม่"
                                    )
                                    
                                    if selected_mapping.startswith("🔗 จับคู่กับ:"):
                                        mapped_header = selected_mapping.replace("🔗 จับคู่กับ: ", "")
                                        file_mapping[header] = mapped_header
                                        st.success(f"✅ จับคู่: {header} → {mapped_header}")
                                        
                                    elif selected_mapping == "✏️ สร้างชื่อใหม่":
                                        custom_header = st.text_input(
                                            "พิมพ์ชื่อใหม่:",
                                            value=header,
                                            key=f"custom_{filename}_{i}",
                                            label_visibility="collapsed",
                                            placeholder="พิมพ์ชื่อ header ใหม่...",
                                            help="กรอกชื่อ header ใหม่ที่ต้องการใช้"
                                        )
                                        if custom_header and custom_header != header:
                                            file_mapping[header] = custom_header
                                            st.success(f"✅ เปลี่ยนชื่อ: {header} → {custom_header}")
                                    else:
                                        st.info("📌 ใช้ชื่อเดิม")
                                else:
                                    file_excluded.append(header)
                                    st.error("🗑️ **Header นี้จะถูกลบออก**")
                            
                            # Add spacing between headers
                            if i < len(headers) - 1:
                                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    
                    # Summary for this file
                    if file_mapping or file_excluded:
                        with st.expander(f"📋 สรุปการเปลี่ยนแปลงสำหรับ {filename}", expanded=False):
                            if file_mapping:
                                st.write("**🔄 Headers ที่จะถูกเปลี่ยนชื่อ/จับคู่:**")
                                for old, new in file_mapping.items():
                                    match_status = merger.get_header_match_status(old, file_headers, filename)
                                    icon = "❌→✅" if match_status == "no_match" else "🔄"
                                    st.write(f"• {icon} `{old}` → `{new}`")
                            
                            if file_excluded:
                                st.write("**🗑️ Headers ที่จะถูกลบออก:**")
                                for excluded in file_excluded:
                                    match_status = merger.get_header_match_status(excluded, file_headers, filename)
                                    icon = "❌🗑️" if match_status == "no_match" else "🗑️"
                                    st.write(f"• {icon} `{excluded}`")
                    
                    if file_mapping:
                        header_mapping[filename] = file_mapping
                    if file_excluded:
                        excluded_headers[filename] = file_excluded
                
                # Store in session state for merge process
                st.session_state.header_mapping = header_mapping
                st.session_state.excluded_headers = excluded_headers
            
            elif len(file_headers) > 1:
                st.markdown("""
                <div class="success-box">
                    ✅ Headers ทั้งหมดสอดคล้องกัน - พร้อมสำหรับการรวมไฟล์
                </div>
                """, unsafe_allow_html=True)
                st.session_state.header_mapping = {}
                st.session_state.excluded_headers = {}
            else:
                st.info("📄 มีเพียงไฟล์เดียวที่เลือก - ไม่ต้องการการปรับแต่ง Headers")
                st.session_state.header_mapping = {}
                st.session_state.excluded_headers = {}
            
            # Show final header preview before merge
            if len(file_headers) > 1:
                st.subheader("📋 ตัวอย่าง Headers หลังการปรับแต่ง")
                
                preview_headers = set()
                for filename, headers in file_headers.items():
                    mapped_headers = st.session_state.get('header_mapping', {}).get(filename, {})
                    excluded = st.session_state.get('excluded_headers', {}).get(filename, [])
                    
                    for header in headers:
                        if header not in excluded:
                            final_header = mapped_headers.get(header, header)
                            preview_headers.add(final_header)
                
                preview_headers.add('_source_file')  # Always added during merge
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Headers ที่จะปรากฏในไฟล์ที่รวมแล้ว:**")
                    header_html = "<div style='display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0;'>"
                    for header in sorted(preview_headers):
                        if header == '_source_file':
                            header_html += f'<span class="header-match">🏷️ {header}</span>'
                        else:
                            header_html += f'<span class="header-match">📋 {header}</span>'
                    header_html += "</div>"
                    st.markdown(header_html, unsafe_allow_html=True)
                
                with col2:
                    st.metric("จำนวน Headers รวม", len(preview_headers))
        else:
            st.warning("⚠️ กรุณาเลือกไฟล์อย่างน้อย 1 ไฟล์เพื่อดำเนินการต่อ")
            return
        
        # Merge button
        if any(st.session_state.selected_files.values()):
            st.header("⚙️ การรวมไฟล์")
            
            # Show merge summary
            selected_files_list = [f for f, selected in st.session_state.selected_files.items() if selected]
            excluded_files_list = [f for f, selected in st.session_state.selected_files.items() if not selected]
            
            col1, col2 = st.columns(2)
            with col1:
                if selected_files_list:
                    st.write("**✅ ไฟล์ที่จะรวม:**")
                    for f in selected_files_list:
                        st.write(f"• 📄 {f}")
            
            with col2:
                if excluded_files_list:
                    st.write("**❌ ไฟล์ที่ไม่รวม:**")
                    for f in excluded_files_list:
                        st.write(f"• 🚫 {f}")
            
            if st.button("🚀 เริ่มรวมไฟล์", type="primary", use_container_width=True):
                with st.spinner("กำลังรวมไฟล์..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate progress
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        status_text.text(f'กำลังประมวลผล... {i + 1}%')
                        
                    # Perform actual merge with header mapping and exclusions
                    merged_df = merger.merge_files(
                        st.session_state.processed_data,
                        selected_sheets,
                        st.session_state.selected_files,
                        st.session_state.get('header_mapping', {}),
                        st.session_state.get('excluded_headers', {})
                    )
                    
                    st.session_state.merged_df = merged_df
                    
                    progress_bar.progress(100)
                    status_text.text('เสร็จสิ้น!')
                    
                    selected_count = sum(st.session_state.selected_files.values())
                    st.success(f"✅ รวมไฟล์สำเร็จ! รวม {selected_count} ไฟล์ ได้รับ {len(merged_df):,} แถว")
        
        # Show merged results
        if st.session_state.merged_df is not None:
            st.header("📊 ผลลัพธ์การรวมไฟล์")
            
            merged_df = st.session_state.merged_df
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            selected_files_count = sum(st.session_state.selected_files.values())
            excluded_files_count = len(st.session_state.processed_data) - selected_files_count
            
            with col1:
                st.metric("จำนวนแถวรวม", f"{len(merged_df):,}")
            with col2:
                st.metric("จำนวนคอลัมน์", len(merged_df.columns))
            with col3:
                st.metric("ไฟล์ที่รวม", selected_files_count)
            with col4:
                memory_usage = merged_df.memory_usage(deep=True).sum() / 1024 / 1024
                st.metric("ใช้หน่วยความจำ", f"{memory_usage:.2f} MB")
            
            if excluded_files_count > 0:
                st.info(f"ℹ️ มี {excluded_files_count} ไฟล์ที่ไม่ได้รวมตามที่เลือก")
            
            # Data preview
            st.subheader("ตัวอย่างข้อมูล")
            st.dataframe(merged_df.head(100), use_container_width=True)
            
            # Download section
            st.header("⬇️ ดาวน์โหลด")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                filename = f"merged_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_data = merged_df.to_csv(index=False)
                
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                # File size info
                file_size = len(csv_data.encode('utf-8')) / 1024
                st.info(f"ขนาดไฟล์: {file_size:.2f} KB")
            
            # Data distribution chart
            if '_source_file' in merged_df.columns:
                st.subheader("📈 การกระจายข้อมูลตามไฟล์ต้นทาง")
                
                source_counts = merged_df['_source_file'].value_counts()
                
                fig = px.pie(
                    values=source_counts.values,
                    names=source_counts.index,
                    title="สัดส่วนข้อมูลจากแต่ละไฟล์"
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label'
                )
                fig.update_layout(
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Source file statistics table
                st.subheader("📋 สถิติรายละเอียดตามไฟล์")
                stats_df = pd.DataFrame({
                    'ไฟล์': source_counts.index,
                    'จำนวนแถว': source_counts.values,
                    'สัดส่วน (%)': (source_counts.values / len(merged_df) * 100).round(2)
                })
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    else:
        # Welcome message
        st.info("👆 กรุณาอัปโหลดไฟล์จาก Sidebar เพื่อเริ่มต้นใช้งาน")
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📁 รองรับหลายรูปแบบ
            - ไฟล์ CSV
            - Excel (.xlsx, .xls)
            - หลาย Sheet ใน Excel
            - **เลือกไฟล์ที่ต้องการรวม**
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 ตรวจสอบอัตโนมัติ
            - เช็ค Header consistency
            - **แสดงสี Headers ที่ไม่ match**
            - แสดงข้อมูลสถิติ
            - ตัวอย่างข้อมูล
            """)
        
        with col3:
            st.markdown("""
            ### ⚙️ ปรับแต่งได้
            - **เลือก/ไม่เลือกไฟล์**
            - Mapping Headers
            - เลือก/ลบ Headers
            - ดาวน์โหลดผลลัพธ์
            """)

if __name__ == "__main__":
    main()
