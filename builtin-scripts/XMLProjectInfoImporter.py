'''
XML Project Info Importer
Imports project information from an XML file and updates Archicad project info fields
'''

import aclib
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

class XMLProjectInfoImporter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("XML Project Info Importer")
        self.window.geometry("800x600")
        self.setup_ui()
        
    def setup_ui(self):
        # File selection frame
        file_frame = ttk.LabelFrame(self.window, text="XML File Selection", padding="10")
        file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Label(file_frame, text="XML File:").pack(side="left")
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side="left", padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self.window, text="XML Content Preview", padding="10")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # XML preview tab
        xml_frame = ttk.Frame(self.notebook)
        self.notebook.add(xml_frame, text="XML Content")
        
        self.xml_text = tk.Text(xml_frame, wrap="word", height=15)
        xml_scrollbar = ttk.Scrollbar(xml_frame, orient="vertical", command=self.xml_text.yview)
        self.xml_text.configure(yscrollcommand=xml_scrollbar.set)
        self.xml_text.pack(side="left", fill="both", expand=True)
        xml_scrollbar.pack(side="right", fill="y")
        
        # Mapping preview tab
        mapping_frame = ttk.Frame(self.notebook)
        self.notebook.add(mapping_frame, text="Field Mapping")
        
        self.mapping_text = tk.Text(mapping_frame, wrap="word", height=15)
        mapping_scrollbar = ttk.Scrollbar(mapping_frame, orient="vertical", command=self.mapping_text.yview)
        self.mapping_text.configure(yscrollcommand=mapping_scrollbar.set)
        self.mapping_text.pack(side="left", fill="both", expand=True)
        mapping_scrollbar.pack(side="right", fill="y")
        
        # Current project info tab
        current_frame = ttk.Frame(self.notebook)
        self.notebook.add(current_frame, text="Current Project Info")
        
        self.current_text = tk.Text(current_frame, wrap="word", height=15)
        current_scrollbar = ttk.Scrollbar(current_frame, orient="vertical", command=self.current_text.yview)
        self.current_text.configure(yscrollcommand=current_scrollbar.set)
        self.current_text.pack(side="left", fill="both", expand=True)
        current_scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Load XML", command=self.load_xml).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Import All", command=self.import_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Get Current Info", command=self.get_current_info).pack(side="left", padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(self.window, textvariable=self.status_var, relief="sunken").pack(fill="x", padx=10, pady=5)
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.load_xml()
    
    def load_xml(self):
        try:
            file_path = self.file_path_var.get()
            if not file_path:
                messagebox.showerror("Error", "Please select an XML file first")
                return
                
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Display XML content
            self.xml_text.delete(1.0, tk.END)
            self.xml_text.insert(tk.END, ET.tostring(root, encoding='unicode', method='xml'))
            
            # Extract project info fields
            self.project_data = self.extract_project_info(root)
            
            # Show mapping
            self.show_mapping()
            
            self.status_var.set(f"XML loaded successfully. Found {len(self.project_data)} fields.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load XML: {str(e)}")
            self.status_var.set("Error loading XML")
    
    def extract_project_info(self, root):
        """Extract project information from XML"""
        project_data = {}
        
        # Common XML structures for project info
        # You can customize this based on your XML format
        
        # Method 1: Direct field mapping
        for elem in root.iter():
            if elem.text and elem.text.strip():
                # Map XML tag names to project info IDs
                field_id = self.map_xml_to_project_info(elem.tag)
                if field_id:
                    project_data[field_id] = elem.text.strip()
        
        # Method 2: Structured project info section
        project_info = root.find('ProjectInfo')
        if project_info is not None:
            for field in project_info:
                if field.text and field.text.strip():
                    field_id = self.map_xml_to_project_info(field.tag)
                    if field_id:
                        project_data[field_id] = field.text.strip()
        
        return project_data
    
    def map_xml_to_project_info(self, xml_tag):
        """Map XML tag names to Archicad project info field IDs"""
        mapping = {
            # Project fields
            'ProjectName': 'PROJECTNAME',
            'ProjectDescription': 'PROJECT_DESCRIPTION',
            'ProjectID': 'PROJECT_ID',
            'ProjectCode': 'PROJECT_CODE',
            'ProjectNumber': 'PROJECTNUMBER',
            'ProjectStatus': 'PROJECTSTATUS',
            'Keywords': 'KEYWORDS',
            'Notes': 'NOTES',
            
            # Site fields
            'SiteName': 'SITE_NAME',
            'SiteDescription': 'SITE_DESCRIPTION',
            'SiteAddress': 'SITE_ADDRESS',
            
            # Building fields
            'BuildingName': 'BUILDING_NAME',
            'BuildingDescription': 'BUILDING_DESCRIPTION',
            'BuildingType': 'BUILDING_TYPE',
            
            # Contact fields
            'ClientName': 'CLIENT_NAME',
            'ClientAddress': 'CLIENT_ADDRESS',
            'ClientPhone': 'CLIENT_PHONE',
            'ClientEmail': 'CLIENT_EMAIL',
            
            # CAD Technician fields
            'CADTechnicianName': 'CAD_TECHNICIAN_NAME',
            'CADTechnicianCompany': 'CAD_TECHNICIAN_COMPANY',
            'CADTechnicianPhone': 'CAD_TECHNICIAN_PHONE',
            'CADTechnicianEmail': 'CAD_TECHNICIAN_EMAIL',
            
            # Additional mappings
            'name': 'PROJECTNAME',
            'description': 'PROJECT_DESCRIPTION',
            'id': 'PROJECT_ID',
            'code': 'PROJECT_CODE',
            'number': 'PROJECTNUMBER',
            'status': 'PROJECTSTATUS',
            'keywords': 'KEYWORDS',
            'notes': 'NOTES',
        }
        
        return mapping.get(xml_tag, None)
    
    def show_mapping(self):
        """Show the mapping between XML and project info fields"""
        self.mapping_text.delete(1.0, tk.END)
        
        if hasattr(self, 'project_data'):
            self.mapping_text.insert(tk.END, "XML to Project Info Field Mapping:\n")
            self.mapping_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for field_id, value in self.project_data.items():
                self.mapping_text.insert(tk.END, f"Field ID: {field_id}\n")
                self.mapping_text.insert(tk.END, f"Value: {value}\n")
                self.mapping_text.insert(tk.END, "-" * 30 + "\n")
    
    def get_current_info(self):
        """Get current project info from Archicad"""
        try:
            response = aclib.RunTapirCommand('GetProjectInfoFields')
            
            self.current_text.delete(1.0, tk.END)
            self.current_text.insert(tk.END, "Current Project Information:\n")
            self.current_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for field in response['fields']:
                self.current_text.insert(tk.END, f"ID: {field['projectInfoId']}\n")
                self.current_text.insert(tk.END, f"Name: {field['projectInfoName']}\n")
                self.current_text.insert(tk.END, f"Value: {field['projectInfoValue']}\n")
                self.current_text.insert(tk.END, "-" * 30 + "\n")
            
            self.status_var.set("Current project info loaded")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get current project info: {str(e)}")
            self.status_var.set("Error getting current info")
    
    def preview_changes(self):
        """Preview what changes will be made"""
        if not hasattr(self, 'project_data'):
            messagebox.showwarning("Warning", "Please load an XML file first")
            return
        
        try:
            current_response = aclib.RunTapirCommand('GetProjectInfoFields')
            current_fields = {field['projectInfoId']: field['projectInfoValue'] for field in current_response['fields']}
            
            changes = []
            for field_id, new_value in self.project_data.items():
                current_value = current_fields.get(field_id, '')
                if current_value != new_value:
                    changes.append({
                        'field_id': field_id,
                        'current_value': current_value,
                        'new_value': new_value
                    })
            
            if changes:
                preview_window = tk.Toplevel(self.window)
                preview_window.title("Preview Changes")
                preview_window.geometry("600x400")
                
                text_widget = tk.Text(preview_window, wrap="word")
                scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)
                
                text_widget.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                text_widget.insert(tk.END, "Changes to be made:\n")
                text_widget.insert(tk.END, "=" * 50 + "\n\n")
                
                for change in changes:
                    text_widget.insert(tk.END, f"Field: {change['field_id']}\n")
                    text_widget.insert(tk.END, f"Current: {change['current_value']}\n")
                    text_widget.insert(tk.END, f"New: {change['new_value']}\n")
                    text_widget.insert(tk.END, "-" * 30 + "\n")
                
                self.status_var.set(f"Preview shows {len(changes)} changes")
            else:
                messagebox.showinfo("Info", "No changes needed - all values are already up to date")
                self.status_var.set("No changes needed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview changes: {str(e)}")
            self.status_var.set("Error previewing changes")
    
    def import_all(self):
        """Import all project info from XML"""
        if not hasattr(self, 'project_data'):
            messagebox.showwarning("Warning", "Please load an XML file first")
            return
        
        # Confirm before importing
        result = messagebox.askyesno(
            "Confirm Import",
            f"This will update {len(self.project_data)} project info fields. Continue?"
        )
        
        if not result:
            return
        
        try:
            success_count = 0
            error_count = 0
            
            for field_id, value in self.project_data.items():
                try:
                    aclib.RunTapirCommand('SetProjectInfoField', {
                        'projectInfoId': field_id,
                        'projectInfoValue': value
                    })
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error setting {field_id}: {str(e)}")
            
            if error_count == 0:
                messagebox.showinfo("Success", f"Successfully imported {success_count} fields")
                self.status_var.set(f"Import completed: {success_count} fields updated")
            else:
                messagebox.showwarning("Partial Success", 
                    f"Import completed with {success_count} successes and {error_count} errors")
                self.status_var.set(f"Import completed with {error_count} errors")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {str(e)}")
            self.status_var.set("Error during import")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = XMLProjectInfoImporter()
    app.run() 