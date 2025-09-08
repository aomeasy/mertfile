import unittest
import pandas as pd
import io
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import FileMerger

class TestFileMerger(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.merger = FileMerger()
        
        # Create sample CSV data
        self.csv_data1 = "Name,Age,City\nJohn,25,Bangkok\nJane,30,Chiang Mai"
        self.csv_data2 = "Name,Age,Country\nBob,35,Thailand\nAlice,28,Thailand"
        
        # Create sample DataFrames
        self.df1 = pd.DataFrame({
            'Name': ['John', 'Jane'],
            'Age': [25, 30],
            'City': ['Bangkok', 'Chiang Mai']
        })
        
        self.df2 = pd.DataFrame({
            'Name': ['Bob', 'Alice'], 
            'Age': [35, 28],
            'Country': ['Thailand', 'Thailand']
        })
    
    def test_get_file_type(self):
        """Test file type detection"""
        self.assertEqual(self.merger.get_file_type("test.csv"), "csv")
        self.assertEqual(self.merger.get_file_type("test.xlsx"), "excel")
        self.assertEqual(self.merger.get_file_type("test.xls"), "excel")
        self.assertEqual(self.merger.get_file_type("test.txt"), "unknown")
    
    def test_analyze_headers_matching(self):
        """Test header analysis with matching headers"""
        processed_data = {
            'file1.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df1}
            },
            'file2.csv': {
                'sheets': ['Sheet1'], 
                'data': {'Sheet1': self.df1.copy()}
            }
        }
        
        selected_sheets = {'file1.csv': 'Sheet1', 'file2.csv': 'Sheet1'}
        
        headers, has_mismatch, file_headers = self.merger.analyze_headers(
            processed_data, selected_sheets
        )
        
        self.assertFalse(has_mismatch)
        self.assertEqual(set(headers), {'Name', 'Age', 'City'})
    
    def test_analyze_headers_mismatched(self):
        """Test header analysis with mismatched headers"""
        processed_data = {
            'file1.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df1}
            },
            'file2.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df2}
            }
        }
        
        selected_sheets = {'file1.csv': 'Sheet1', 'file2.csv': 'Sheet1'}
        
        headers, has_mismatch, file_headers = self.merger.analyze_headers(
            processed_data, selected_sheets
        )
        
        self.assertTrue(has_mismatch)
        self.assertEqual(set(headers), {'Name', 'Age', 'City', 'Country'})
    
    def test_merge_files_simple(self):
        """Test simple file merging"""
        processed_data = {
            'file1.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df1}
            },
            'file2.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df1.copy()}
            }
        }
        
        selected_sheets = {'file1.csv': 'Sheet1', 'file2.csv': 'Sheet1'}
        
        merged_df = self.merger.merge_files(processed_data, selected_sheets)
        
        # Should have 4 rows (2 from each file) + source column
        self.assertEqual(len(merged_df), 4)
        self.assertIn('_source_file', merged_df.columns)
        self.assertEqual(merged_df['_source_file'].nunique(), 2)
    
    def test_merge_files_with_mapping(self):
        """Test file merging with header mapping"""
        processed_data = {
            'file1.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df1}
            },
            'file2.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': self.df2}
            }
        }
        
        selected_sheets = {'file1.csv': 'Sheet1', 'file2.csv': 'Sheet1'}
        header_mapping = {
            'file2.csv': {'Country': 'City'}  # Map Country to City
        }
        
        merged_df = self.merger.merge_files(
            processed_data, selected_sheets, header_mapping
        )
        
        # Should have both City and Country columns merged
        self.assertEqual(len(merged_df), 4)
        self.assertIn('City', merged_df.columns)
        self.assertNotIn('Country', merged_df.columns)
    
    def test_convert_to_csv(self):
        """Test CSV conversion"""
        df = pd.DataFrame({
            'Name': ['John', 'Jane'],
            'Age': [25, 30],
            'City': ['Bangkok', 'Chiang Mai']
        })
        
        csv_content = self.merger.convertToCSV(df.to_dict('records'))
        
        # Check if CSV content is properly formatted
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 data rows
        self.assertTrue(lines[0].startswith('Name,Age,City'))
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames"""
        processed_data = {}
        selected_sheets = {}
        
        merged_df = self.merger.merge_files(processed_data, selected_sheets)
        
        self.assertTrue(merged_df.empty)
    
    def test_header_analysis_empty_data(self):
        """Test header analysis with no data"""
        processed_data = {}
        selected_sheets = {}
        
        headers, has_mismatch, file_headers = self.merger.analyze_headers(
            processed_data, selected_sheets
        )
        
        self.assertEqual(headers, [])
        self.assertFalse(has_mismatch)
        self.assertEqual(file_headers, {})

class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def setUp(self):
        self.merger = FileMerger()
    
    def test_special_characters_in_csv(self):
        """Test handling of special characters in CSV"""
        df_special = pd.DataFrame({
            'Name': ['John "Johnny" Doe', 'Jane, Smith'],
            'Description': ['Test\nwith\nnewlines', 'Test,with,commas'],
            'Value': [100.50, 200.75]
        })
        
        csv_content = self.merger.convertToCSV(df_special.to_dict('records'))
        
        # Should properly escape special characters
        self.assertIn('"John ""Johnny"" Doe"', csv_content)
        self.assertIn('"Jane, Smith"', csv_content)
    
    def test_mixed_data_types(self):
        """Test handling of mixed data types"""
        df_mixed = pd.DataFrame({
            'ID': [1, 2, 3],
            'Name': ['John', 'Jane', 'Bob'],
            'Score': [95.5, 87.2, 92.8],
            'Active': [True, False, True],
            'Date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        
        processed_data = {
            'test.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': df_mixed}
            }
        }
        
        selected_sheets = {'test.csv': 'Sheet1'}
        merged_df = self.merger.merge_files(processed_data, selected_sheets)
        
        self.assertEqual(len(merged_df), 3)
        self.assertIn('_source_file', merged_df.columns)
    
    def test_duplicate_column_names(self):
        """Test handling of duplicate column names"""
        # This would typically be handled by pandas automatically
        df_with_dupes = pd.DataFrame({
            'Name': ['John', 'Jane'],
            'Name.1': ['Johnny', 'Janey'],  # pandas style duplicate
            'Age': [25, 30]
        })
        
        processed_data = {
            'test.csv': {
                'sheets': ['Sheet1'],
                'data': {'Sheet1': df_with_dupes}
            }
        }
        
        selected_sheets = {'test.csv': 'Sheet1'}
        headers, has_mismatch, file_headers = self.merger.analyze_headers(
            processed_data, selected_sheets
        )
        
        # Should detect all unique column names
        self.assertEqual(len(headers), 3)
        self.assertIn('Name', headers)
        self.assertIn('Name.1', headers)

if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFileMerger))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
