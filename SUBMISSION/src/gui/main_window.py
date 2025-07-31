"""
Main GUI window for the electoral roll extractor
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from typing import Optional, List

from ..core.extractor import ElectoralRollExtractor
from ..utils.file_handler import FileHandler
from ..utils.logger import Logger


class MainWindow:
    """Main GUI window for the electoral roll extractor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Electoral Roll Data Extractor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize components
        self.extractor = ElectoralRollExtractor()
        self.logger = Logger.get_logger(__name__)
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.processing = False
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.center_window()
    
    def setup_styles(self):
        """Setup custom styles for the GUI"""
        style = ttk.Style()
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Electoral Roll Data Extractor", 
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Extract structured voter data from PDF electoral rolls",
            font=('Arial', 10)
        )
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        ttk.Label(main_frame, text="Input Path:", style='Heading.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        
        input_entry = ttk.Entry(main_frame, textvariable=self.input_path, width=60)
        input_entry.grid(row=2, column=1, pady=5, padx=(10, 5), sticky=(tk.W, tk.E))
        
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(
            row=2, column=2, pady=5, padx=(5, 0)
        )
        
        # Output section
        ttk.Label(main_frame, text="Output Path:", style='Heading.TLabel').grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path, width=60)
        output_entry.grid(row=3, column=1, pady=5, padx=(10, 5), sticky=(tk.W, tk.E))
        
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(
            row=3, column=2, pady=5, padx=(5, 0)
        )
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.extract_button = ttk.Button(
            button_frame, 
            text="Extract Data", 
            command=self.start_extraction,
            style='Action.TButton'
        )
        self.extract_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(
            side=tk.LEFT, padx=5
        )
        
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(
            side=tk.LEFT, padx=5
        )
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, pady=5)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, height=12, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def browse_input(self):
        """Browse for input files or folder"""
        choice = messagebox.askyesnocancel(
            "Input Selection", 
            "Select input type:\n\nYes - Select folder containing PDFs\nNo - Select individual PDF files\nCancel - Cancel selection"
        )
        
        if choice is None:  # Cancel
            return
        elif choice:  # Yes - folder
            path = filedialog.askdirectory(title="Select Input Folder")
        else:  # No - files
            path = filedialog.askopenfilenames(
                title="Select PDF Files", 
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if path:
                path = ';'.join(path)  # Join multiple files with semicolon
        
        if path:
            self.input_path.set(path)
            self.log_message(f"Input path selected: {path}")
    
    def browse_output(self):
        """Browse for output folder"""
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_path.set(path)
            self.log_message(f"Output path selected: {path}")
    
    def clear_fields(self):
        """Clear all input fields and log"""
        self.input_path.set("")
        self.output_path.set("")
        self.log_text.delete(1.0, tk.END)
        self.status_label.config(text="Ready")
    
    def log_message(self, message: str):
        """Add message to log text widget"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, status: str):
        """Update status label"""
        self.status_label.config(text=status)
        self.root.update_idletasks()
    
    def start_extraction(self):
        """Start the extraction process in a separate thread"""
        if self.processing:
            messagebox.showwarning("Warning", "Extraction is already in progress")
            return
        
        input_path = self.input_path.get().strip()
        output_path = self.output_path.get().strip()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output paths")
            return
        
        # Validate paths
        if not FileHandler.validate_input_path(input_path.split(';')[0]):
            messagebox.showerror("Error", "Invalid input path or no PDF files found")
            return
        
        if not FileHandler.validate_output_path(output_path):
            messagebox.showerror("Error", "Invalid output path or insufficient permissions")
            return
        
        # Start extraction in separate thread
        self.processing = True
        self.extract_button.config(state='disabled')
        self.progress.start()
        
        thread = threading.Thread(target=self.extract_data, daemon=True)
        thread.start()
    
    def extract_data(self):
        """Extract data from PDFs (runs in separate thread)"""
        try:
            input_path = self.input_path.get().strip()
            output_path = self.output_path.get().strip()
            
            self.update_status("Starting extraction...")
            self.log_message("=" * 50)
            self.log_message("Starting Electoral Roll Data Extraction")
            self.log_message("=" * 50)
            
            # Process files
            if ';' in input_path:  # Multiple files
                files = [f.strip() for f in input_path.split(';')]
                all_voters = []
                
                for i, file_path in enumerate(files, 1):
                    self.update_status(f"Processing file {i}/{len(files)}")
                    self.log_message(f"Processing: {os.path.basename(file_path)}")
                    
                    voters = self.extractor.process_single_pdf(file_path)
                    all_voters.extend(voters)
                    
                    self.log_message(f"Extracted {len(voters)} records from {os.path.basename(file_path)}")
                
                self.extractor.extracted_data = all_voters
            else:
                self.update_status("Processing files...")
                self.extractor.process_directory(input_path)
            
            # Save to Excel
            self.update_status("Saving to Excel...")
            self.log_message("Saving data to Excel file...")
            
            result = FileHandler.save_to_excel(self.extractor.extracted_data, output_path)
            
            if result:
                self.log_message(f"SUCCESS: Data saved to {result}")
                self.log_message(f"Total records extracted: {len(self.extractor.extracted_data)}")
                self.update_status("Extraction completed successfully")
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Data extracted and saved successfully!\n\n"
                    f"Records: {len(self.extractor.extracted_data)}\n"
                    f"File: {os.path.basename(result)}"
                ))
            else:
                self.log_message("ERROR: Failed to save data to Excel")
                self.update_status("Extraction failed")
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to save data to Excel"))
        
        except Exception as e:
            error_msg = f"Error during extraction: {str(e)}"
            self.log_message(f"ERROR: {error_msg}")
            self.update_status("Extraction failed")
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            # Reset UI state
            self.processing = False
            self.progress.stop()
            self.extract_button.config(state='normal')
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()