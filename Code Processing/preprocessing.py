import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import os

class ExcelToCSVConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel/CSV to CSV Converter")
        self.root.geometry("600x400")
        
        # Setup style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input file section
        ttk.Label(main_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_path, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # Process button
        ttk.Button(main_frame, text="Convert to CSV", command=self.process_file).grid(row=1, column=1, pady=20)
        
        # Results section
        ttk.Label(main_frame, text="Processing Results:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.result_text = tk.Text(main_frame, height=10, width=60)
        self.result_text.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def browse_input(self):
        filetypes = (
            ('Excel files', '*.xlsx *.xls *.xlsm *.xlsb'),
            ('CSV files', '*.csv'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(
            title='Select Input File',
            filetypes=filetypes
        )
        if filename:
            self.input_path.set(filename)

    def process_file(self):
        input_file = self.input_path.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
        
        try:
            # Read the input file (Excel or CSV)
            if input_file.endswith('.csv'):
                df = pd.read_csv(input_file)
            else:
                df = pd.read_excel(input_file)

            # Sort the columns by the number of unique values
            unique_counts = df.nunique()
            sorted_cols = unique_counts[unique_counts > 2].sort_values().index.tolist() + \
                          unique_counts[unique_counts <= 2].sort_values().index.tolist()
            df = df[sorted_cols]

            # Choose output file location
            output_file = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv')],
                title='Save CSV file as'
            )
            
            if not output_file:
                return
            
            # Save to CSV
            df.to_csv(output_file, index=False, encoding='utf-8')
            
            # Display results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Conversion completed successfully!\n\n")
            self.result_text.insert(tk.END, f"Input file: {input_file}\n")
            self.result_text.insert(tk.END, f"Output CSV file: {output_file}\n")
            self.result_text.insert(tk.END, f"\nRows processed: {len(df)}")
            self.result_text.insert(tk.END, f"\nColumns processed: {len(df.columns)}")
            
            messagebox.showinfo("Success", "File converted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = ExcelToCSVConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()