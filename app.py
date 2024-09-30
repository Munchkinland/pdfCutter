import os
import PyPDF2
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Importa ttk para la barra de progreso
import logging
import shutil

# Configuración del logging
logging.basicConfig(filename='pdf_splitter.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

MAX_SIZE_MB = 9.00 * 1024 * 1024  # Tamaño máximo en bytes (ajustado a 9 MB)
pdf_path = None  # Ruta del PDF
output_dir = None  # Directorio de salida

def select_output_folder():
    """Permite al usuario seleccionar la carpeta de destino."""
    global output_dir
    output_dir = filedialog.askdirectory()
    if output_dir:
        logging.info(f"Carpeta seleccionada para guardar los fragmentos: {output_dir}")
        messagebox.showinfo("Carpeta seleccionada", f"Se guardarán en: {output_dir}")
    else:
        messagebox.showwarning("No seleccionada", "No se ha seleccionado una carpeta.")

def split_pdf(progress_bar):
    """Divide el PDF en partes de máximo 9 MB."""
    global pdf_path, output_dir
    if not pdf_path:
        messagebox.showerror("Error", "Por favor, seleccione un archivo PDF.")
        return
    if not output_dir:
        messagebox.showerror("Error", "Por favor, seleccione una carpeta de destino.")
        return

    try:
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(pdf_reader.pages)
        current_part = 1
        current_writer = PyPDF2.PdfWriter()
        current_size = 0
        part_files = []

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        temp_output_dir = os.path.join(output_dir, f"{base_name}_temp_splits")
        
        if not os.path.exists(temp_output_dir):
            os.makedirs(temp_output_dir)

        # Configura la barra de progreso
        progress_bar['maximum'] = total_pages
        progress_bar['value'] = 0

        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            current_writer.add_page(page)

            # Guardar en un archivo temporal para calcular el tamaño
            temp_file_path = os.path.join(temp_output_dir, f"temp_part_{current_part}.pdf")
            with open(temp_file_path, 'wb') as temp_file:
                current_writer.write(temp_file)

            current_size = os.path.getsize(temp_file_path)

            if current_size >= MAX_SIZE_MB:
                # Guardar el archivo actual ya que ha alcanzado el tamaño máximo permitido
                part_file_path = os.path.join(output_dir, f"{base_name}_part_{current_part}.pdf")
                with open(part_file_path, 'wb') as output_pdf:
                    current_writer.write(output_pdf)

                logging.info(f"Parte {current_part} creada con éxito, tamaño: {current_size / (1024 * 1024):.2f} MB")
                part_files.append(part_file_path)

                # Reiniciar para la siguiente parte
                current_part += 1
                current_writer = PyPDF2.PdfWriter()  # Reiniciar el escritor
                current_writer.add_page(page)  # Agregar la página actual a la nueva parte
                current_size = os.path.getsize(temp_file_path)  # Actualizar el tamaño

            os.remove(temp_file_path)  # Borrar el archivo temporal

            # Actualizar la barra de progreso
            progress_bar['value'] += 1
            progress_bar.update()

        # Guardar la última parte si quedó incompleta
        if len(current_writer.pages) > 0:
            part_file_path = os.path.join(output_dir, f"{base_name}_part_{current_part}.pdf")
            with open(part_file_path, 'wb') as output_pdf:
                current_writer.write(output_pdf)
            part_files.append(part_file_path)
            logging.info(f"Parte {current_part} final creada con éxito.")

        # Mover los archivos generados a la carpeta final seleccionada
        messagebox.showinfo("Éxito", "El PDF ha sido dividido con éxito.")
        logging.info(f"El PDF {pdf_path} ha sido dividido en {current_part} partes.")

    except Exception as e:
        logging.error(f"Error al dividir el PDF: {str(e)}")
        messagebox.showerror("Error", f"Ha ocurrido un error al dividir el PDF: {str(e)}")

def upload_file():
    """Abre un cuadro de diálogo para cargar un archivo PDF."""
    global pdf_path
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if pdf_path:
        messagebox.showinfo("Archivo cargado", f"Archivo seleccionado: {pdf_path}")
        logging.info(f"Archivo PDF cargado: {pdf_path}")

def create_gui():
    """Crea la interfaz gráfica (GUI) con botones para cargar PDF y seleccionar carpeta."""
    window = tk.Tk()
    window.title("Divisor de PDFs")
    window.geometry("400x300")

    label = tk.Label(window, text="Seleccione el archivo PDF para dividir")
    label.pack(pady=10)

    btn_upload = tk.Button(window, text="Cargar PDF", command=upload_file)
    btn_upload.pack(pady=5)

    btn_select_folder = tk.Button(window, text="Seleccionar carpeta de destino", command=select_output_folder)
    btn_select_folder.pack(pady=5)

    progress_bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    btn_start = tk.Button(window, text="Iniciar proceso", command=lambda: split_pdf(progress_bar))
    btn_start.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
