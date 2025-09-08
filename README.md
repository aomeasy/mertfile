# 📁 File Merger - Modern SPA

เว็บแอปพลิเคชันสำหรับรวมไฟล์ CSV และ Excel หลายไฟล์เข้าด้วยกันอย่างง่ายดาย พร้อมด้วย UI/UX ที่ทันสมัยและใช้งานง่าย

![File Merger Demo](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## ✨ คุณสมบัติหลัก

### 🎨 การออกแบบ
- **โทนสีเอิร์ธโทน (Earth Tone)** - สีอบอุ่นและเป็นมิตรต่อสายตา
- **Responsive Design** - รองรับทุกหน้าจอ มือถือ แท็บเล็ต เดสก์ท็อป
- **Modern UI/UX** - เมนูเรียบง่าย ใช้งานง่าย
- **Animation & Effects** - การเคลื่อนไหวนุ่มนวล

### 📊 ฟังก์ชันการทำงาน
- **รองรับหลายรูปแบบไฟล์:** CSV, Excel (.xlsx, .xls)
- **หลาย Sheet ใน Excel:** สามารถเลือก sheet ที่ต้องการได้
- **ตรวจสอบ Headers อัตโนมัติ:** เช็คความสอดคล้องของ column headers
- **ปรับแต่ง Header Mapping:** แก้ไขเมื่อ headers ไม่ตรงกัน
- **สถิติและข้อมูลโดยรวม:** แสดงจำนวน records ก่อน-หลังการรวม
- **ดาวน์โหลดผลลัพธ์:** ไฟล์ CSV พร้อมใช้งาน
- **ไม่เก็บข้อมูลในระบบ:** ประมวลผลในหน่วยความจำเท่านั้น

### 📈 การแสดงผลข้อมูล
- **Data Preview:** ตัวอย่างข้อมูลก่อนการรวม
- **Statistics Dashboard:** สถิติการรวมไฟล์แบบ real-time
- **Progress Tracking:** แสดงความคืบหน้าการประมวลผล
- **Data Distribution Chart:** กราฟแสดงสัดส่วนข้อมูลจากแต่ละไฟล์

## 🚀 การติดตั้งและใช้งาน

### วิธีที่ 1: ใช้งานบน Streamlit Cloud (แนะนำ)

1. **Fork หรือ Clone repository นี้**
   ```bash
   git clone https://github.com/your-username/file-merger-spa.git
   cd file-merger-spa
   ```

2. **Push ไปยัง GitHub repository ของคุณ**

3. **Deploy บน Streamlit Cloud**
   - เข้าไปที่ [share.streamlit.io](https://share.streamlit.io/)
   - เชื่อมต่อกับ GitHub account
   - เลือก repository และ branch
   - ระบุ main file: `app.py`
   - คลิก "Deploy!"

### วิธีที่ 2: รันในเครื่อง (Local Development)

1. **Clone repository**
   ```bash
   git clone https://github.com/your-username/file-merger-spa.git
   cd file-merger-spa
   ```

2. **สร้าง Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **ติดตั้ง Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **รันแอปพลิเคชัน**
   ```bash
   streamlit run app.py
   ```

5. **เข้าใช้งาน**
   - เปิดเบราว์เซอร์ไปที่ `http://localhost:8501`

## 📁 โครงสร้างโปรเจค

```
file-merger-spa/
├── app.py                 # Streamlit main application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── static/               # Static files (optional)
│   └── index.html        # HTML version (standalone)
├── tests/                # Unit tests (optional)
│   └── test_app.py
└── .streamlit/           # Streamlit configuration
    └── config.toml
```

## 🔧 การใช้งาน

### 1. อัปโหลดไฟล์
- ใช้ sidebar เพื่ออัปโหลดไฟล์ CSV หรือ Excel
- รองรับการอัปโหลดหลายไฟล์พร้อมกัน
- แสดงข้อมูลพื้นฐานของแต่ละไฟล์

### 2. เลือก Sheet (สำหรับ Excel)
- หากไฟล์ Excel มีหลาย sheet สามารถเลือกได้
- แสดง preview ข้อมูลของแต่ละ sheet

### 3. ตรวจสอบ Headers
- ระบบจะตรวจสอบความสอดคล้องของ headers อัตโนมัติ
- หาก headers ไม่ตรงกัน จะแสดง interface สำหรับ mapping

### 4. ปรับแต่ง Header Mapping (หากจำเป็น)
- สามารถ map headers ที่ไม่ตรงกันให้เป็นชื่อเดียวกัน
- แสดงตัวอย่างการ mapping

### 5. รวมไฟล์
- คลิกปุ่ม "เริ่มรวมไฟล์"
- แสดง progress bar และสถิติการรวม

### 6. ดาวน์โหลดผลลัพธ์
- ดาวน์โหลดไฟล์ CSV ที่รวมแล้ว
- แสดงสถิติข้อมูลและกราฟการกระจาย

## 🎯 การปรับแต่งและพัฒนาต่อ

### การเปลี่ยนธีมสี
แก้ไขค่าตัวแปร CSS ใน `load_css()` function:
```python
:root {
    --earth-brown: #8B4513;    # สีน้ำตาลหลัก
    --warm-beige: #F5E6D3;     # สีเบจอบอุ่น
    --sage: #9CAF88;           # สีเขียวอ่อน
    --clay: #CD853F;           # สีดินเหนียว
    # ... เพิ่มเติม
}
```

### การเพิ่มรูปแบบไฟล์ใหม่
เพิ่มใน `get_file_type()` method:
```python
def get_file_type(self, filename: str) -> str:
    if filename.lower().endswith('.csv'):
        return 'csv'
    elif filename.lower().endswith(('.xlsx', '.xls')):
        return 'excel'
    elif filename.lower().endswith('.json'):  # เพิ่มใหม่
        return 'json'
    return 'unknown'
```

### การเพิ่มฟีเจอร์การกรองข้อมูล
```python
# เพิ่มใน main() function
filter_column = st.selectbox("กรองตามคอลัมน์:", merged_df.columns)
filter_value = st.text_input("ค่าที่ต้องการกรอง:")

if filter_value:
    filtered_df = merged_df[merged_df[filter_column].astype(str).str.contains(filter_value, na=False)]
    st.dataframe(filtered_df)
```

## 🐛 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. **ไฟล์ Excel ไม่สามารถอ่านได้**
   ```
   Error: No module named 'openpyxl'
   ```
   **แก้ไข:** `pip install openpyxl`

2. **Memory Error เมื่อไฟล์ใหญ่**
   ```
   MemoryError: Unable to allocate memory
   ```
   **แก้ไข:** ประมวลผลทีละส่วน หรือใช้ `chunksize` parameter

3. **Encoding Error สำหรับไฟล์ CSV**
   ```
   UnicodeDecodeError: 'utf-8' codec can't decode
   ```
   **แก้ไข:** 
   ```python
   df = pd.read_csv(file, encoding='utf-8-sig')  # หรือ encoding='cp1252'
   ```

4. **Streamlit App ไม่แสดงอย่างถูกต้อง**
   - ตรวจสอบ Python version (ต้อง 3.8+)
   - Clear cache: `streamlit cache clear`
   - Restart แอปพลิเคชัน

## 📊 ตัวอย่างการใช้งาน

### Example 1: รวมไฟล์ Sales Data
```
ไฟล์:
- sales_q1.csv (100 แถว)
- sales_q2.xlsx (150 แถว) 
- sales_q3.csv (200 แถว)

Headers:
- Date, Product, Amount, Region

ผลลัพธ์:
- merged_sales_20240101.csv (450 แถว)
- เพิ่มคอลัมน์ _source_file
```

### Example 2: รวมข้อมูลพนักงานจากหลายแผนก
```
ไฟล์:
- hr_dept.xlsx (Sheet: Employees)
- finance_dept.csv
- it_dept.xlsx (Sheet: Staff)

Header Mapping:
- Name → FullName
- Emp_ID → EmployeeID
- Dept → Department

ผลลัพธ์:
- merged_employees.csv
```

## 🔒 ความปลอดภัยและความเป็นส่วนตัว

- **ไม่เก็บข้อมูล:** ไฟล์ทั้งหมดประมวลผลในหน่วยความจำเท่านั้น
- **ไม่มีการบันทึก:** ข้อมูลจะหายไปเมื่อปิดแอปพลิเคชัน
- **ประมวลผลในเครื่อง:** หากรันแบบ local ข้อมูลไม่ออกจากเครื่อง
- **Streamlit Cloud:** ข้อมูลจะถูกลบทันทีหลังการประมวลผล

## 🤝 การมีส่วนร่วมในการพัฒนา

### การรายงานปัญหา (Bug Report)
1. เข้าไปที่ [Issues](https://github.com/your-username/file-merger-spa/issues)
2. คลิก "New Issue"
3. เลือก Bug Report template
4. กรอกรายละเอียดที่ครบถ้วน

### การขอฟีเจอร์ใหม่ (Feature Request)
1. เข้าไปที่ [Issues](https://github.com/your-username/file-merger-spa/issues)
2. คลิก "New Issue"
3. เลือก Feature Request template
4. อธิบายฟีเจอร์ที่ต้องการ

### การส่ง Pull Request
1. Fork repository
2. สร้าง feature branch: `git checkout -b feature/AmazingFeature`
3. Commit การเปลี่ยนแปลง: `git commit -m 'Add some AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. เปิด Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 ผู้พัฒนา

- **Your Name** - *Initial work* - [YourGithub](https://github.com/yourusername)

## 🙏 ขอบคุณ

- [Streamlit](https://streamlit.io/) - สำหรับ framework ที่ยอดเยียม
- [Pandas](https://pandas.pydata.org/) - สำหรับการจัดการข้อมูล
- [Plotly](https://plotly.com/) - สำหรับการแสดงผลกราฟ
- [OpenPyXL](https://openpyxl.readthedocs.io/) - สำหรับการอ่านไฟล์ Excel

## 📞 ติดต่อ

- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

⭐ หากโปรเจคนี้มีประโยชน์ กรุณา Star ให้ด้วยนะครับ!

## 📋 TODO List

- [ ] เพิ่มรองรับไฟล์ JSON
- [ ] เพิ่มฟีเจอร์การกรองข้อมูล
- [ ] Export เป็น Excel format
- [ ] เพิ่ม Data validation
- [ ] สร้าง API endpoint
- [ ] เพิ่ม Unit tests
- [ ] Docker support
- [ ] Multi-language support

## 🔄 Version History

### v1.0.0 (2024-01-15)
- ✨ เวอร์ชันแรกที่พร้อมใช้งาน
- 📁 รองรับ CSV และ Excel
- 🔍 ตรวจสอบ Headers
- ⚙️ Header mapping
- 📊 สถิติและกราฟ
- ⬇️ ดาวน์โหลดผลลัพธ์

### v1.1.0 (Planning)
- 🔍 ฟีเจอร์ค้นหาและกรอง
- 📊 กราฟเพิ่มเติม
- 🎨 ธีมสีเพิ่มเติม
- 📱 ปรับปรุง Mobile UI
