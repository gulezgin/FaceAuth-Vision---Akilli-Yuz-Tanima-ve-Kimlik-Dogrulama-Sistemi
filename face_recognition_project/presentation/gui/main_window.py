import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from application.services.recognition_service import RecognitionService

class MainWindow:
    def __init__(self, recognition_service: RecognitionService):
        self.recognition_service = recognition_service
        self.logger = logging.getLogger(__name__)
        
        # Ana pencere ayarları
        self.root = tk.Tk()
        self.root.title("Yüz Tanıma Sistemi")
        self.root.geometry("1200x800")
        
        # Kamera değişkenleri
        self.camera_active = False
        self.cap: Optional[cv2.VideoCapture] = None
        
        self.setup_gui()
        
    def setup_gui(self):
        """GUI bileşenlerini oluşturur."""
        # Ana frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Kamera görüntüsü
        self.camera_frame = ttk.LabelFrame(self.main_frame, text="Kamera Görüntüsü")
        self.camera_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Kontrol butonları
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Kontroller")
        self.control_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(self.control_frame, text="Kamera Başlat/Durdur", 
                  command=self.toggle_camera).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Kişi Ekle",
                  command=self.show_add_person_dialog).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Rapor Oluştur",
                  command=self.show_report_dialog).grid(row=0, column=2, padx=5, pady=5)
        
        # Tanıma sonuçları
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Tanıma Sonuçları")
        self.results_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.N, tk.S))
        
        self.results_text = tk.Text(self.results_frame, width=40, height=20)
        self.results_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Durum çubuğu
        self.status_var = tk.StringVar(value="Hazır")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def toggle_camera(self):
        """Kamerayı açıp kapatır."""
        if not self.camera_active:
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise RuntimeError("Kamera açılamadı!")
                
                self.camera_active = True
                self.status_var.set("Kamera aktif")
                self.update_camera()
            except Exception as e:
                self.logger.error(f"Kamera başlatılırken hata: {str(e)}")
                messagebox.showerror("Hata", str(e))
        else:
            self.camera_active = False
            if self.cap:
                self.cap.release()
            self.status_var.set("Kamera kapalı")
            
    def update_camera(self):
        """Kamera görüntüsünü günceller ve yüz tanıma yapar."""
        if self.camera_active:
            try:
                ret, frame = self.cap.read()
                if ret:
                    # Yüz tanıma yap
                    results = self.recognition_service.recognize_face(frame)
                    
                    # Sonuçları görüntüle
                    self.display_results(results)
                    
                    # Yüzleri çerçevele
                    for result in results:
                        top, right, bottom, left = result['location']
                        name = result['name']
                        confidence = result['confidence']
                        
                        # Renk seçimi (tanınan/tanınmayan)
                        color = (0, 255, 0) if result['person_id'] else (0, 0, 255)
                        
                        # Çerçeve ve isim
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        cv2.putText(frame, f"{name} ({confidence:.2f})",
                                  (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                  0.75, color, 2)
                    
                    # Görüntüyü göster
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    photo = ImageTk.PhotoImage(image=image)
                    self.camera_label.configure(image=photo)
                    self.camera_label.image = photo
                
                self.root.after(10, self.update_camera)
                
            except Exception as e:
                self.logger.error(f"Kamera güncellenirken hata: {str(e)}")
                self.camera_active = False
                if self.cap:
                    self.cap.release()
                self.status_var.set(f"Hata: {str(e)}")
                
    def display_results(self, results: list):
        """Tanıma sonuçlarını gösterir."""
        self.results_text.delete(1.0, tk.END)
        for result in results:
            if result['person_id']:
                self.results_text.insert(tk.END,
                    f"İsim: {result['name']}\n"
                    f"Güven: {result['confidence']:.2f}\n"
                    f"Zaman: {datetime.now().strftime('%H:%M:%S')}\n"
                    f"-------------------\n"
                )
            else:
                self.results_text.insert(tk.END,
                    f"Tanınmayan Yüz\n"
                    f"Zaman: {datetime.now().strftime('%H:%M:%S')}\n"
                    f"-------------------\n"
                )
                
    def show_add_person_dialog(self):
        """Kişi ekleme penceresini gösterir."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Kişi Ekle")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        # Form
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # İsim
        ttk.Label(form_frame, text="İsim:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Departman
        ttk.Label(form_frame, text="Departman:").grid(row=1, column=0, sticky=tk.W, pady=5)
        dept_var = tk.StringVar()
        dept_entry = ttk.Entry(form_frame, textvariable=dept_var)
        dept_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=email_var)
        email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Fotoğraf
        photo_path_var = tk.StringVar()
        ttk.Label(form_frame, text="Fotoğraf:").grid(row=3, column=0, sticky=tk.W, pady=5)
        photo_label = ttk.Label(form_frame, textvariable=photo_path_var)
        photo_label.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        def select_photo():
            file_path = filedialog.askopenfilename(
                title="Fotoğraf Seç",
                filetypes=[
                    ("Resim Dosyaları", "*.jpg *.jpeg *.png"),
                    ("Tüm Dosyalar", "*.*")
                ]
            )
            if file_path:
                photo_path_var.set(file_path)
                return file_path
            return None
        
        def save_person():
            try:
                name = name_var.get().strip()
                dept = dept_var.get().strip()
                email = email_var.get().strip()
                photo = photo_path_var.get()
                
                if not all([name, dept, email, photo]):
                    messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
                    return
                
                details = {
                    'department': dept,
                    'email': email
                }
                
                person_id = self.recognition_service.add_person(photo, name, details)
                messagebox.showinfo("Başarılı", f"{name} başarıyla eklendi!")
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Kişi eklenirken hata: {str(e)}")
                messagebox.showerror("Hata", str(e))
        
        # Butonlar
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Fotoğraf Seç",
                  command=select_photo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Kaydet",
                  command=save_person).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İptal",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.grab_set()
        name_entry.focus()
        
    def show_report_dialog(self):
        """Rapor oluşturma penceresini gösterir."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Rapor Oluştur")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Rapor türü seçimi
        ttk.Label(frame, text="Rapor Türü:").grid(row=0, column=0, pady=10)
        report_type = tk.StringVar(value="daily")
        ttk.Radiobutton(frame, text="Günlük", variable=report_type,
                       value="daily").grid(row=1, column=0)
        ttk.Radiobutton(frame, text="Haftalık", variable=report_type,
                       value="weekly").grid(row=2, column=0)
        ttk.Radiobutton(frame, text="Aylık", variable=report_type,
                       value="monthly").grid(row=3, column=0)
        
        def generate_report():
            try:
                now = datetime.now()
                if report_type.get() == "daily":
                    start_date = now - timedelta(days=1)
                elif report_type.get() == "weekly":
                    start_date = now - timedelta(weeks=1)
                else:  # monthly
                    start_date = now - timedelta(days=30)
                
                logs = self.recognition_service.get_recognition_logs(start_date, now)
                
                # Rapor penceresini göster
                self.show_report_results(logs, report_type.get())
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Rapor oluşturulurken hata: {str(e)}")
                messagebox.showerror("Hata", str(e))
        
        ttk.Button(frame, text="Oluştur",
                  command=generate_report).grid(row=4, column=0, pady=20)
        
    def show_report_results(self, logs: List[Dict[str, Any]], report_type: str):
        """Rapor sonuçlarını gösterir."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Rapor Sonuçları")
        dialog.geometry("600x400")
        
        text = tk.Text(dialog, wrap=tk.WORD, width=70, height=20)
        text.pack(padx=10, pady=10)
        
        # Başlık
        text.insert(tk.END, f"Yüz Tanıma Raporu ({report_type})\n")
        text.insert(tk.END, f"Oluşturulma Tarihi: {datetime.now()}\n\n")
        
        # İstatistikler
        total = len(logs)
        success = len([log for log in logs if log['confidence_score'] > 0.8])
        
        text.insert(tk.END, f"Toplam Tanıma: {total}\n")
        text.insert(tk.END, f"Başarılı Tanıma: {success}\n")
        if total > 0:
            text.insert(tk.END, f"Başarı Oranı: %{(success/total*100):.1f}\n\n")
        
        # Detaylı log
        text.insert(tk.END, "Detaylı Kayıtlar:\n")
        text.insert(tk.END, "-" * 50 + "\n")
        
        for log in logs:
            text.insert(tk.END,
                f"Tarih: {log['timestamp']}\n"
                f"Kişi ID: {log['person_id']}\n"
                f"Güven Skoru: {log['confidence_score']:.2f}\n"
                f"-" * 50 + "\n"
            )
        
        text.configure(state="disabled")
        
    def run(self):
        """Uygulamayı başlatır."""
        self.root.mainloop() 