"""
Data Manager Module
Handles Excel operations for student practice records and statistics
"""

import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
import numpy as np


class DataManager:
    """Manages student practice data and statistics in Excel"""
    
    def __init__(self, excel_path="practice_data.xlsx"):
        self.excel_path = excel_path
        self.users_file = "users.xlsx"
        self._initialize_files()
    
    def _initialize_files(self):
        """Create Excel files if they don't exist"""
        # Initialize practice data file
        if not os.path.exists(self.excel_path):
            df = pd.DataFrame(columns=[
                'Student_ID', 'Student_Name', 'Pose_Type', 
                'Accuracy', 'Date', 'Time', 'Duration_Seconds',
                'Rules_Passed', 'Rules_Failed'
            ])
            df.to_excel(self.excel_path, index=False)
            self._format_excel(self.excel_path)
        
        # Initialize users file
        if not os.path.exists(self.users_file):
            users_df = pd.DataFrame({
                'Username': ['student1', 'student2', 'teacher1'],
                'Password': ['pass123', 'pass123', 'admin123'],
                'Role': ['student', 'student', 'teacher'],
                'Full_Name': ['Demo Student 1', 'Demo Student 2', 'Demo Teacher']
            })
            users_df.to_excel(self.users_file, index=False)
            self._format_excel(self.users_file)
    
    def _format_excel(self, filepath):
        """Apply formatting to Excel file"""
        try:
            wb = load_workbook(filepath)
            ws = wb.active
            
            # Header formatting
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            wb.save(filepath)
        except Exception as e:
            print(f"Formatting error: {e}")
    
    def authenticate_user(self, username, password, role):
        """Authenticate user based on credentials"""
        try:
            users_df = pd.read_excel(self.users_file)
            user = users_df[
                (users_df['Username'] == username) & 
                (users_df['Password'] == password) & 
                (users_df['Role'] == role)
            ]
            
            if not user.empty:
                return True, user.iloc[0]['Full_Name']
            return False, None
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, None
    
    def save_practice_record(self, student_id, student_name, pose_type, accuracy, duration, rules_passed=None, rules_failed=None):
        """Save a student's practice session record"""
        try:
            now = datetime.now()
            
            new_record = {
                'Student_ID': student_id,
                'Student_Name': student_name,
                'Pose_Type': pose_type,
                'Accuracy': round(accuracy, 2),
                'Date': now.strftime('%Y-%m-%d'),
                'Time': now.strftime('%H:%M:%S'),
                'Duration_Seconds': duration,
                'Rules_Passed': rules_passed if rules_passed else '',
                'Rules_Failed': rules_failed if rules_failed else ''
            }
            
            # Read existing data
            df = pd.read_excel(self.excel_path)
            
            # Append new record
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.excel_path, index=False)
            self._format_excel(self.excel_path)
            
            return True
        except Exception as e:
            print(f"Error saving record: {e}")
            return False
    
    def get_student_stats(self, student_id):
        """Get statistics for a specific student"""
        try:
            df = pd.read_excel(self.excel_path)
            student_data = df[df['Student_ID'] == student_id]
            
            if student_data.empty:
                return None
            
            stats = {
                'total_sessions': len(student_data),
                'avg_accuracy': round(student_data['Accuracy'].mean(), 2),
                'max_accuracy': round(student_data['Accuracy'].max(), 2),
                'min_accuracy': round(student_data['Accuracy'].min(), 2),
                'recent_sessions': student_data.tail(10).to_dict('records'),
                'pose_breakdown': student_data.groupby('Pose_Type').agg({
                    'Accuracy': ['mean', 'count']
                }).round(2).to_dict()
            }
            
            return stats
        except Exception as e:
            print(f"Error getting student stats: {e}")
            return None
    
    def get_all_students_summary(self):
        """Get summary statistics for all students"""
        try:
            df = pd.read_excel(self.excel_path)
            
            if df.empty:
                return []
            
            summary = df.groupby(['Student_ID', 'Student_Name']).agg({
                'Accuracy': ['mean', 'count', 'max', 'min'],
                'Date': 'max'
            }).round(2)
            
            summary.columns = ['Avg_Accuracy', 'Total_Sessions', 'Max_Accuracy', 'Min_Accuracy', 'Last_Practice']
            summary = summary.reset_index()
            
            return summary.to_dict('records')
        except Exception as e:
            print(f"Error getting summary: {e}")
            return []
    
    def get_pose_statistics(self):
        """Get overall statistics by pose type"""
        try:
            df = pd.read_excel(self.excel_path)
            
            if df.empty:
                return {}
            
            pose_stats = df.groupby('Pose_Type').agg({
                'Accuracy': ['mean', 'count', 'max', 'min']
            }).round(2)
            
            pose_stats.columns = ['Average', 'Sessions', 'Best', 'Worst']
            
            return pose_stats.to_dict('index')
        except Exception as e:
            print(f"Error getting pose stats: {e}")
            return {}
    
    def get_recent_activities(self, limit=20):
        """Get recent practice activities across all students"""
        try:
            df = pd.read_excel(self.excel_path)
            
            if df.empty:
                return []
            
            recent = df.sort_values(['Date', 'Time'], ascending=False).head(limit)
            return recent.to_dict('records')
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []
