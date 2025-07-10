import os
import logging
from datetime import datetime
from typing import Dict, List
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill


class ExcelReportGenerator:
    """Handles Excel report generation with formatting"""
    
    def __init__(self, output_directory: str = None):
        """Initialize Excel report generator
        
        Args:
            output_directory: Directory to save reports (defaults to current directory)
        """
        self.output_directory = output_directory or os.getcwd()
    
    def create_campaign_report(self, df: pd.DataFrame, use_openai: bool = True) -> str:
        """Create final Excel report with AI descriptions and all fields
        
        Args:
            df: DataFrame with campaign data and AI descriptions
            use_openai: Whether OpenAI was used (affects filename)
            
        Returns:
            Path to the created Excel file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not use_openai:
            filename = f"campaign_descriptions_PREVIEW_{timestamp}.xlsx"
        else:
            filename = f"campaign_descriptions_{timestamp}.xlsx"
        
        output_path = os.path.join(self.output_directory, filename)
        
        # Define column order
        priority_cols = ['AI_Sales_Description']
        if 'AI_Prompt' in df.columns:
            priority_cols.append('AI_Prompt')
        
        # Fields to show after AI columns
        key_fields = [
            'Description', 
            'Short_Description_for_Sales__c', 
            'Id', 
            'Name', 
            'BMID__c',
            'Intended_Product__c', 
            'Channel__c', 
            'Sub_Channel__c', 
            'Sub_Channel_Detail__c'
        ]
        
        # Get remaining columns
        all_cols = df.columns.tolist()
        remaining_cols = [col for col in all_cols if col not in priority_cols + key_fields]
        
        # Build final column order
        final_cols = priority_cols + [col for col in key_fields if col in all_cols] + remaining_cols
        
        # Reorder dataframe
        df_ordered = df[final_cols]
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_ordered.to_excel(writer, sheet_name='Campaign Descriptions', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Campaign Descriptions']
            
            # Format header row
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logging.info(f"Final report saved to {output_path}")
        return output_path
    
    def create_summary_report(self, df: pd.DataFrame, processing_stats: Dict) -> str:
        """Create a summary report with processing statistics
        
        Args:
            df: DataFrame with campaign data
            processing_stats: Dictionary with processing statistics
            
        Returns:
            Path to the created summary report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"campaign_summary_{timestamp}.xlsx"
        output_path = os.path.join(self.output_directory, filename)
        
        # Create summary DataFrame
        summary_data = {
            'Metric': [
                'Total Campaigns Processed',
                'Campaigns with AI Descriptions',
                'Processing Success Rate',
                'Average Description Length',
                'Unique Channels',
                'Unique Verticals',
                'Total Campaign Members'
            ],
            'Value': [
                len(df),
                df['AI_Sales_Description'].notna().sum(),
                f"{(df['AI_Sales_Description'].notna().sum() / len(df) * 100):.1f}%",
                f"{df['AI_Sales_Description'].str.len().mean():.1f} chars",
                df['Channel__c'].nunique(),
                df['Vertical__c'].nunique(),
                processing_stats.get('total_members', 'N/A')
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Channel breakdown
            channel_stats = df['Channel__c'].value_counts().reset_index()
            channel_stats.columns = ['Channel', 'Count']
            channel_stats.to_excel(writer, sheet_name='Channel Breakdown', index=False)
            
            # Vertical breakdown
            vertical_stats = df['Vertical__c'].value_counts().reset_index()
            vertical_stats.columns = ['Vertical', 'Count']
            vertical_stats.to_excel(writer, sheet_name='Vertical Breakdown', index=False)
        
        logging.info(f"Summary report saved to {output_path}")
        return output_path 