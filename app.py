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
    
    .info-box {
        background: #E6F3FF;
        border: 1px solid #99D3F5;
        color: #2B6CB0;
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
    
    .empty-column-item {
        background: #FFF5F5;
        border: 1px solid #FEB2B2;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .keep-column-item {
        background: #F0FFF4;
        border: 1px solid #9AE6B4;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .column-analysis-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
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
    
    def analyze_headers(self, processed_data: Dict, selected_sheets: Dict) -> Tuple[List[str], bool]:
        """Analyze headers across all selected sheets"""
        all_headers = set()
        file_headers = {}
        
        for filename, file_info in processed_data.items():
            sheet_name = selected_sheets.get(filename, file_info['sheets'][0])
            if sheet_name in file_info['data']:
                df = file_info['data'][sheet_name]
                headers = list(df.columns)
                file_headers[filename] = headers
                all_headers.update(headers)
        
        # Check for header consistency
        all_headers_list = list(all_headers)
        has_mismatch = False
        
        for filename, headers in file_headers.items():
            if set(headers) != all_headers:
                has_mismatch = True
                break
                
        return all_headers_list, has_mismatch, file_headers
    
    def merge_files(self, processed_data: Dict, selected_sheets: Dict, header_mapping: Dict = None, excluded_headers: Dict = None) -> pd.DataFrame:
        """Merge all files into a single DataFrame"""
        merged_dfs = []
        
        for filename, file_info in processed_data.items():
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
    
    def analyze_empty_columns(self, df: pd.DataFrame) -> Dict:
        """Analyze empty or mostly empty columns in the merged DataFrame"""
        column_analysis = {}
        total_rows = len(df)
        
        for col in df.columns:
            if col == '_source_file':  # Skip source file column
                continue
                
            # Count non-null values
            non_null_count = df[col].count()
            null_count = total_rows - non_null_count
            null_percentage = (null_count / total_rows) * 100
            
            # Check for empty strings or whitespace
            if df[col].dtype == 'object':
                # Count empty strings and whitespace
                empty_string_count = df[col].fillna('').astype(str).str.strip().eq('').sum()
                effective_empty_count = null_count + empty_string_count
                effective_empty_percentage = (effective_empty_count / total_rows) * 100
            else:
                effective_empty_count = null_count
                effective_empty_percentage = null_percentage
            
            # Get sample of non-empty values
            non_empty_values = df[col].dropna()
            if df[col].dtype == 'object':
                non_empty_values = non_empty_values[non_empty_values.astype(str).str.strip() != '']
            
            sample_values = non_empty_values.head(3).tolist() if len(non_empty_values) > 0 else []
            
            column_analysis[col] = {
                'null_count': null_count,
                'null_percentage': null_percentage,
                'effective_empty_count': effective_empty_count,
                'effective_empty_percentage': effective_empty_percentage,
                'non_empty_count': total_rows - effective_empty_count,
                'sample_values': sample_values,
                'data_type': str(df[col].dtype)
            }
        
        return column_analysis
    
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
    if 'final_df' not in st.session_state:
        st.session_state.final_df = None
    if 'empty_columns_analysis' not in st.session_state:
        st.session_state.empty_columns_analysis = {}
    
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
                st.session_state.final_df = None
                st.session_state.empty_columns_analysis = {}
    
    # Main content
    if st.session_state.processed_data:
        # File information section
        st.header("📋 ไฟล์ที่อัปโหลด")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_sheets = {}
            
            for filename, file_info in st.session_state.processed_data.items():
                with st.expander(f"📄 {filename}", expanded=True):
                    col_info, col_sheet = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        <div class="file-info">
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
                                index=0
                            )
                            selected_sheets[filename] = selected_sheet
                        else:
                            selected_sheets[filename] = file_info['sheets'][0]
                            st.info(f"Sheet: {file_info['sheets'][0]}")
                    
                    # Show data preview
                    sheet_name = selected_sheets[filename]
                    if sheet_name in file_info['data']:
                        df = file_info['data'][sheet_name]
                        st.write(f"**Preview ({len(df)} แถว, {len(df.columns)} คอลัมน์):**")
                        st.dataframe(df.head(3), use_container_width=True)
        
        with col2:
            # Statistics
            total_files = len(st.session_state.processed_data)
            total_records = sum([
                len(file_info['data'][selected_sheets.get(filename, file_info['sheets'][0])]) 
                for filename, file_info in st.session_state.processed_data.items()
                if selected_sheets.get(filename, file_info['sheets'][0]) in file_info['data']
            ])
            
            st.markdown(f"""
            <div class="stat-card">
                <h3>📊 สถิติ</h3>
                <p><strong>จำนวนไฟล์:</strong> {total_files}</p>
                <p><strong>จำนวนแถวรวม:</strong> {total_records:,}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Header analysis
        st.header("🔍 การวิเคราะห์ Headers")
        
        all_headers, has_mismatch, file_headers = merger.analyze_headers(
            st.session_state.processed_data, 
            selected_sheets
        )
        
        if has_mismatch:
            st.markdown("""
            <div class="warning-box">
                ⚠️ พบความไม่สอดคล้องของ Headers - กรุณาตรวจสอบและปรับแต่ง
            </div>
            """, unsafe_allow_html=True)
            
            # Show header comparison
            st.subheader("เปรียบเทียบ Headers")
            
            for filename, headers in file_headers.items():
                with st.expander(f"Headers ของ {filename}"):
                    cols = st.columns(min(len(headers), 4))
                    for i, header in enumerate(headers):
                        with cols[i % 4]:
                            if header in all_headers and all([header in h for h in file_headers.values()]):
                                st.success(header)
                            else:
                                st.error(header)
            
            # Enhanced Header mapping interface
            st.subheader("🔧 ปรับแต่ง Headers สำหรับการรวมไฟล์")
            
            st.markdown("""
            <div style="background: #E8F4FD; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <h4 style="color: #1E40AF; margin: 0;">📝 วิธีใช้งาน:</h4>
                <p style="margin: 0.5rem 0 0 0;">
                1. ดูตัวอย่างข้อมูลแต่ละไฟล์<br>
                2. เลือกว่า Header ไหนจะใช้ หรือลบทิ้ง<br>
                3. จับคู่ Headers ที่มีความหมายเหมือนกัน
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            header_mapping = {}
            excluded_headers = {}
            
            for filename, headers in file_headers.items():
                st.markdown("---")
                st.markdown(f"### 📁 {filename}")
                
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
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 3])
                        
                        with col1:
                            st.markdown(f"**`{header}`**")
                            # Show sample values
                            if header in sample_df.columns:
                                sample_values = sample_df[header].dropna().head(3).tolist()
                                if sample_values:
                                    st.caption(f"ตัวอย่าง: {', '.join(str(v)[:15] + ('...' if len(str(v)) > 15 else '') for v in sample_values)}")
                                else:
                                    st.caption("ไม่มีข้อมูล")
                        
                        with col2:
                            # Action selection with clearer options
                            action = st.selectbox(
                                "การดำเนินการ:",
                                ["✅ ใช้งาน", "❌ ลบทิ้ง"],
                                key=f"action_{filename}_{i}",
                                index=0,
                                label_visibility="collapsed"
                            )
                        
                        with col3:
                            if action == "✅ ใช้งาน":
                                # Create mapping options
                                mapping_options = []
                                mapping_options.append(f"📌 ใช้ชื่อเดิม: {header}")
                                
                                # Add other headers as mapping options
                                for other_header in all_headers:
                                    if other_header != header:
                                        mapping_options.append(f"🔗 จับคู่กับ: {other_header}")
                                
                                mapping_options.append("✏️ สร้างชื่อใหม่")
                                
                                selected_mapping = st.selectbox(
                                    "เลือกการจับคู่:",
                                    mapping_options,
                                    key=f"map_{filename}_{i}",
                                    label_visibility="collapsed"
                                )
                                
                                if selected_mapping.startswith("🔗 จับคู่กับ:"):
                                    mapped_header = selected_mapping.replace("🔗 จับคู่กับ: ", "")
                                    file_mapping[header] = mapped_header
                                    
                                elif selected_mapping == "✏️ สร้างชื่อใหม่":
                                    custom_header = st.text_input(
                                        "พิมพ์ชื่อใหม่:",
                                        value=header,
                                        key=f"custom_{filename}_{i}",
                                        label_visibility="collapsed",
                                        placeholder="พิมพ์ชื่อ header ใหม่..."
                                    )
                                    if custom_header and custom_header != header:
                                        file_mapping[header] = custom_header
                            else:
                                file_excluded.append(header)
                                st.markdown("🗑️ **Header นี้จะถูกลบออก**")
                        
                        # Add spacing between headers
                        if i < len(headers) - 1:
                            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # Summary for this file
                if file_mapping or file_excluded:
                    with st.expander(f"📋 สรุปการเปลี่ยนแปลงสำหรับ {filename}", expanded=False):
                        if file_mapping:
                            st.write("**🔄 Headers ที่จะถูกเปลี่ยนชื่อ/จับคู่:**")
                            for old, new in file_mapping.items():
                                st.write(f"• `{old}` → `{new}`")
                        
                        if file_excluded:
                            st.write("**🗑️ Headers ที่จะถูกลบออก:**")
                            for excluded in file_excluded:
                                st.write(f"• `{excluded}`")
                
                if file_mapping:
                    header_mapping[filename] = file_mapping
                if file_excluded:
                    excluded_headers[filename] = file_excluded
            
            # Store in session state for merge process
            st.session_state.header_mapping = header_mapping
            st.session_state.excluded_headers = excluded_headers
        
        else:
            st.markdown("""
            <div class="success-box">
                ✅ Headers ทั้งหมดสอดคล้องกัน - พร้อมสำหรับการรวมไฟล์
            </div>
            """, unsafe_allow_html=True)
            st.session_state.header_mapping = {}
            st.session_state.excluded_headers = {}
        
        # Merge button
        st.header("⚙️ การรวมไฟล์")
        
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
                    st.session_state.get('header_mapping', {}),
                    st.session_state.get('excluded_headers', {})
                )
                
                st.session_state.merged_df = merged_df
                
                # Analyze empty columns
                empty_analysis = merger.analyze_empty_columns(merged_df)
                st.session_state.empty_columns_analysis = empty_analysis
                
                # Set initial final_df to merged_df
                st.session_state.final_df = merged_df.copy()
                
                progress_bar.progress(100)
                status_text.text('เสร็จสิ้น!')
                
                st.success(f"✅ รวมไฟล์สำเร็จ! ได้รับ {len(merged_df)} แถว")
        
        # Show merged results and empty column analysis
        if st.session_state.merged_df is not None:
            st.header("📊 ผลลัพธ์การรวมไฟล์")
            
            merged_df = st.session_state.merged_df
            empty_analysis = st.session_state.empty_columns_analysis
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("จำนวนแถวรวม", f"{len(merged_df):,}")
            with col2:
                st.metric("จำนวนคอลัมน์", len(merged_df.columns))
            with col3:
                st.metric("ไฟล์ต้นทาง", len(st.session_state.processed_data))
            with col4:
                memory_usage = merged_df.memory_usage(deep=True).sum() / 1024 / 1024
                st.metric("ใช้หน่วยความจำ", f"{memory_usage:.2f} MB")
            
            # Empty Column Analysis Section
            if empty_analysis:
                st.markdown("""
                <div class="column-analysis-header">
                    <h2>🔍 การวิเคราะห์คอลัมน์ที่ไม่มีข้อมูล</h2>
                    <p>ตรวจสอบและเลือกคอลัมน์ที่ต้องการลบออกก่อนดาวน์โหลด</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Find columns with high empty percentage
                empty_columns = []
                partially_empty_columns = []
                full_columns = []
                
                for col, analysis in empty_analysis.items():
                    if analysis['effective_empty_percentage'] >= 95:
                        empty_columns.append((col, analysis))
                    elif analysis['effective_empty_percentage'] >= 50:
                        partially_empty_columns.append((col, analysis))
                    else:
                        full_columns.append((col, analysis))
                
                # Show summary
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="stat-card" style="border-left-color: #EF4444;">
                        <h4 style="color: #DC2626; margin: 0;">🗑️ คอลัมน์ที่แนะนำให้ลบ</h4>
                        <p style="margin: 0.5rem 0;"><strong>{len(empty_columns)}</strong> คอลัมน์</p>
                        <p style="margin: 0; font-size: 0.9em;">ข้อมูลว่าง ≥ 95%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stat-card" style="border-left-color: #F59E0B;">
                        <h4 style="color: #D97706; margin: 0;">⚠️ คอลัมน์ที่ควรพิจารณา</h4>
                        <p style="margin: 0.5rem 0;"><strong>{len(partially_empty_columns)}</strong> คอลัมน์</p>
                        <p style="margin: 0; font-size: 0.9em;">ข้อมูลว่าง 50-94%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="stat-card" style="border-left-color: #10B981;">
                        <h4 style="color: #059669; margin: 0;">✅ คอลัมน์ที่มีข้อมูลดี</h4>
                        <p style="margin: 0.5rem 0;"><strong>{len(full_columns)}</strong> คอลัมน์</p>
                        <p style="margin: 0; font-size: 0.9em;">ข้อมูลว่าง < 50%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Column selection interface
                if empty_columns or partially_empty_columns:
                    st.markdown("""
                    <div class="info-box">
                        💡 <strong>คำแนะนำ:</strong> คลิกเพื่อเลือก/ยกเลิกคอลัมน์ที่ต้องการลบ 
                        คอลัมน์ที่มีข้อมูลว่างมากจะช่วยลดขนาดไฟล์และเพิ่มประสิทธิภาพ
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Initialize columns to remove in session state
                    if 'columns_to_remove' not in st.session_state:
                        # Auto-select columns with >95% empty data
                        st.session_state.columns_to_remove = [col for col, _ in empty_columns]
                    
                    # Create tabs for different categories
                    if empty_columns or partially_empty_columns:
                        tab1, tab2, tab3 = st.tabs([
                            f"🗑️ แนะนำให้ลบ ({len(empty_columns)})",
                            f"⚠️ ควรพิจารณา ({len(partially_empty_columns)})",
                            f"✅ คอลัมน์ดี ({len(full_columns)})"
                        ])
                        
                        with tab1:
                            if empty_columns:
                                st.markdown("**คอลัมน์ที่มีข้อมูลว่าง 95% ขึ้นไป:**")
                                for col, analysis in empty_columns:
                                    col1, col2 = st.columns([1, 3])
                                    
                                    with col1:
                                        remove_col = st.checkbox(
                                            "ลบคอลัมน์นี้",
                                            value=col in st.session_state.columns_to_remove,
                                            key=f"remove_{col}",
                                            help=f"ลบคอลัมน์ {col} ออกจากไฟล์สุดท้าย"
                                        )
                                        
                                        if remove_col and col not in st.session_state.columns_to_remove:
                                            st.session_state.columns_to_remove.append(col)
                                        elif not remove_col and col in st.session_state.columns_to_remove:
                                            st.session_state.columns_to_remove.remove(col)
                                    
                                    with col2:
                                        st.markdown(f"""
                                        <div class="{'empty-column-item' if col in st.session_state.columns_to_remove else 'keep-column-item'}">
                                            <div>
                                                <strong>{col}</strong><br>
                                                <span style="color: #666;">ข้อมูลว่าง: {analysis['effective_empty_percentage']:.1f}% 
                                                ({analysis['effective_empty_count']:,}/{len(merged_df):,} แถว)</span><br>
                                                <span style="color: #888; font-size: 0.9em;">
                                                    ตัวอย่าง: {', '.join([str(v)[:20] + ('...' if len(str(v)) > 20 else '') for v in analysis['sample_values']]) if analysis['sample_values'] else 'ไม่มีข้อมูล'}
                                                </span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("ไม่พบคอลัมน์ที่มีข้อมูลว่างมากกว่า 95%")
                        
                        with tab2:
                            if partially_empty_columns:
                                st.markdown("**คอลัมน์ที่มีข้อมูลว่าง 50-94%:**")
                                for col, analysis in partially_empty_columns:
                                    col1, col2 = st.columns([1, 3])
                                    
                                    with col1:
                                        remove_col = st.checkbox(
                                            "ลบคอลัมน์นี้",
                                            value=col in st.session_state.columns_to_remove,
                                            key=f"remove_partial_{col}",
                                            help=f"ลบคอลัมน์ {col} ออกจากไฟล์สุดท้าย"
                                        )
                                        
                                        if remove_col and col not in st.session_state.columns_to_remove:
                                            st.session_state.columns_to_remove.append(col)
                                        elif not remove_col and col in st.session_state.columns_to_remove:
                                            st.session_state.columns_to_remove.remove(col)
                                    
                                    with col2:
                                        st.markdown(f"""
                                        <div class="{'empty-column-item' if col in st.session_state.columns_to_remove else 'keep-column-item'}">
                                            <div>
                                                <strong>{col}</strong><br>
                                                <span style="color: #666;">ข้อมูลว่าง: {analysis['effective_empty_percentage']:.1f}% 
                                                ({analysis['effective_empty_count']:,}/{len(merged_df):,} แถว)</span><br>
                                                <span style="color: #888; font-size: 0.9em;">
                                                    ตัวอย่าง: {', '.join([str(v)[:20] + ('...' if len(str(v)) > 20 else '') for v in analysis['sample_values']]) if analysis['sample_values'] else 'ไม่มีข้อมูล'}
                                                </span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("ไม่พบคอลัมน์ที่มีข้อมูลว่าง 50-94%")
                        
                        with tab3:
                            if full_columns:
                                st.markdown("**คอลัมน์ที่มีข้อมูลดี (ข้อมูลว่างน้อยกว่า 50%):**")
                                for col, analysis in full_columns:
                                    col1, col2 = st.columns([1, 3])
                                    
                                    with col1:
                                        remove_col = st.checkbox(
                                            "ลบคอลัมน์นี้",
                                            value=col in st.session_state.columns_to_remove,
                                            key=f"remove_full_{col}",
                                            help=f"ลบคอลัมน์ {col} ออกจากไฟล์สุดท้าย (ไม่แนะนำ)"
                                        )
                                        
                                        if remove_col and col not in st.session_state.columns_to_remove:
                                            st.session_state.columns_to_remove.append(col)
                                        elif not remove_col and col in st.session_state.columns_to_remove:
                                            st.session_state.columns_to_remove.remove(col)
                                    
                                    with col2:
                                        st.markdown(f"""
                                        <div class="{'empty-column-item' if col in st.session_state.columns_to_remove else 'keep-column-item'}">
                                            <div>
                                                <strong>{col}</strong><br>
                                                <span style="color: #666;">ข้อมูลว่าง: {analysis['effective_empty_percentage']:.1f}% 
                                                ({analysis['effective_empty_count']:,}/{len(merged_df):,} แถว)</span><br>
                                                <span style="color: #888; font-size: 0.9em;">
                                                    ตัวอย่าง: {', '.join([str(v)[:20] + ('...' if len(str(v)) > 20 else '') for v in analysis['sample_values']]) if analysis['sample_values'] else 'ไม่มีข้อมูล'}
                                                </span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("ไม่พบคอลัมน์ที่มีข้อมูลดี")
                    
                    # Quick action buttons
                    st.markdown("---")
                    st.subheader("🚀 การดำเนินการเร็ว")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("🗑️ ลบทั้งหมดที่แนะนำ", use_container_width=True):
                            st.session_state.columns_to_remove = [col for col, _ in empty_columns]
                            st.rerun()
                    
                    with col2:
                        if st.button("⚠️ ลบที่ว่าง > 75%", use_container_width=True):
                            cols_to_remove = []
                            for col, analysis in empty_analysis.items():
                                if analysis['effective_empty_percentage'] > 75:
                                    cols_to_remove.append(col)
                            st.session_state.columns_to_remove = cols_to_remove
                            st.rerun()
                    
                    with col3:
                        if st.button("✅ เก็บทั้งหมด", use_container_width=True):
                            st.session_state.columns_to_remove = []
                            st.rerun()
                    
                    with col4:
                        if st.button("🔄 รีเซ็ต", use_container_width=True):
                            st.session_state.columns_to_remove = [col for col, _ in empty_columns]
                            st.rerun()
                    
                    # Apply column removal
                    if st.session_state.columns_to_remove:
                        st.markdown("---")
                        
                        if st.button("🎯 ปรับปรุงไฟล์ (ลบคอลัมน์ที่เลือก)", type="primary", use_container_width=True):
                            with st.spinner("กำลังปรับปรุงไฟล์..."):
                                # Create final dataframe by removing selected columns
                                columns_to_keep = [col for col in merged_df.columns if col not in st.session_state.columns_to_remove]
                                st.session_state.final_df = merged_df[columns_to_keep].copy()
                                
                                removed_count = len(st.session_state.columns_to_remove)
                                remaining_count = len(columns_to_keep)
                                
                                st.success(f"✅ ปรับปรุงเสร็จสิ้น! ลบ {removed_count} คอลัมน์ เหลือ {remaining_count} คอลัมน์")
                        
                        # Show summary of columns to be removed
                        with st.expander(f"📋 รายการคอลัมน์ที่จะลบ ({len(st.session_state.columns_to_remove)} คอลัมน์)", expanded=False):
                            for col in st.session_state.columns_to_remove:
                                if col in empty_analysis:
                                    analysis = empty_analysis[col]
                                    st.write(f"• **{col}** - ข้อมูลว่าง {analysis['effective_empty_percentage']:.1f}%")
                    else:
                        # No columns to remove, use merged_df as final
                        st.session_state.final_df = merged_df.copy()
                        st.info("ไม่มีคอลัมน์ที่เลือกให้ลบ - ไฟล์จะใช้ข้อมูลทั้งหมด")
                else:
                    st.success("🎉 ไม่พบคอลัมน์ที่มีข้อมูลว่างมาก ข้อมูลของคุณมีคุณภาพดี!")
                    st.session_state.final_df = merged_df.copy()
            
            # Data preview section
            st.header("👁️ ตัวอย่างข้อมูลสุดท้าย")
            
            final_df = st.session_state.final_df if st.session_state.final_df is not None else merged_df
            
            # Show comparison if columns were removed
            if st.session_state.final_df is not None and len(st.session_state.final_df.columns) != len(merged_df.columns):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "คอลัมน์เดิม", 
                        len(merged_df.columns),
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "คอลัมน์หลังปรับปรุง", 
                        len(final_df.columns),
                        delta=len(final_df.columns) - len(merged_df.columns)
                    )
                
                with col3:
                    original_size = len(merged_df.to_csv(index=False).encode('utf-8'))
                    new_size = len(final_df.to_csv(index=False).encode('utf-8'))
                    size_reduction = ((original_size - new_size) / original_size) * 100
                    
                    st.metric(
                        "ลดขนาดไฟล์", 
                        f"{size_reduction:.1f}%",
                        delta=f"-{(original_size - new_size) / 1024:.1f} KB"
                    )
            
            st.dataframe(final_df.head(100), use_container_width=True)
            
            # Download section
            st.header("⬇️ ดาวน์โหลด")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                filename = f"merged_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_data = final_df.to_csv(index=False)
                
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
            if '_source_file' in final_df.columns:
                st.subheader("📈 การกระจายข้อมูลตามไฟล์ต้นทาง")
                
                source_counts = final_df['_source_file'].value_counts()
                
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
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 ตรวจสอบอัตโนมัติ
            - เช็ค Header consistency
            - วิเคราะห์คอลัมน์ว่าง
            - แสดงข้อมูลสถิติ
            """)
        
        with col3:
            st.markdown("""
            ### ⚙️ ปรับแต่งได้
            - Mapping Headers
            - เลือก/ลบ Headers
            - ลบคอลัมน์ว่าง
            - ดาวน์โหลดผลลัพธ์
            """)

if __name__ == "__main__":
    main()
