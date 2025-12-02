#!/usr/bin/env python3
"""
NetCat File Transfer - Simple GUI application for transferring files using netcat
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import socket
import subprocess
import threading
import os
import random
import string
from pathlib import Path


class NetcatTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetCat File Transfer")
        self.root.geometry("700x700")
        
        # Apple-like color scheme
        self.colors = {
            'bg': '#F5F5F7',  # Light gray background
            'card_bg': '#FFFFFF',  # White cards
            'text': '#1D1D1F',  # Dark text
            'text_secondary': '#6E6E73',  # Secondary text
            'accent': '#007AFF',  # Apple blue
            'accent_green': '#34C759',  # Apple green
            'accent_red': '#FF3B30',  # Apple red
            'border': '#D2D2D7',  # Light border
            'button_bg': '#007AFF',
            'button_hover': '#0051D5',
            'button_text': '#FFFFFF',
            'input_bg': '#F5F5F7',
            'input_border': '#D2D2D7',
        }
        
        # Font fallbacks (try SF Pro, fallback to system fonts)
        import platform
        if platform.system() == "Darwin":  # macOS
            self.fonts = {
                'title': ("SF Pro Display", 28),
                'heading': ("SF Pro Text", 15),
                'body': ("SF Pro Text", 12),
                'body_small': ("SF Pro Text", 11),
                'body_tiny': ("SF Pro Text", 10),
                'mono': ("SF Mono", 16),
                'mono_small': ("SF Mono", 10),
            }
        else:
            # Fallback fonts for other systems
            self.fonts = {
                'title': ("Helvetica", 28),
                'heading': ("Helvetica", 15),
                'body': ("Helvetica", 12),
                'body_small': ("Helvetica", 11),
                'body_tiny': ("Helvetica", 10),
                'mono': ("Courier", 16),
                'mono_small': ("Courier", 10),
            }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Get local IP address
        self.local_ip = self.get_local_ip()
        
        # Generate a random pin code for this session
        self.pin_code = self.generate_pin()
        
        # Setup UI
        self.setup_ui()
        
        # Start network discovery listener in background
        self.discovery_running = True
        self.discovered_peers = {}
        threading.Thread(target=self.start_discovery_listener, daemon=True).start()
        
    def get_local_ip(self):
        """Get the local IP address of the machine"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            # Fallback: try to get IP from network interfaces
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                if ip.startswith("127."):
                    # Try alternative method
                    import platform
                    if platform.system() == "Darwin":  # macOS
                        result = subprocess.run(
                            ["ipconfig", "getifaddr", "en0"],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            ip = result.stdout.strip()
                return ip
            except Exception:
                return "127.0.0.1"
    
    def generate_pin(self):
        """Generate a random 6-digit PIN code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def create_modern_entry(self, parent, width=20):
        """Create a modern text entry field"""
        entry = tk.Entry(
            parent,
            font=self.fonts['body'],
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['input_border'],
            highlightcolor=self.colors['accent'],
            insertbackground=self.colors['text'],
            width=width
        )
        return entry
    
    def create_modern_button(self, parent, text, command, size="medium", color="blue"):
        """Create a modern button with Apple-like styling"""
        if size == "small":
            font = self.fonts['body_small']
            padx, pady = 12, 6
        elif size == "medium":
            font = self.fonts['body']
            padx, pady = 16, 8
        else:  # large
            font = (self.fonts['body'][0], 14, "bold")
            padx, pady = 20, 12
        
        if color == "green":
            bg_color = self.colors['accent_green']
            hover_color = "#30B04F"
            text_color = self.colors['button_text']  # White text
        elif color == "blue":
            bg_color = self.colors['accent']
            hover_color = self.colors['button_hover']
            text_color = self.colors['button_text']  # White text
        elif color == "secondary":
            # Secondary button style - light background, dark text
            bg_color = self.colors['input_bg']
            hover_color = "#E5E5EA"
            text_color = self.colors['text']  # Dark text
        else:
            bg_color = self.colors['button_bg']
            hover_color = self.colors['button_hover']
            text_color = self.colors['button_text']  # White text
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=font,
            bg=bg_color,
            fg=text_color,
            activebackground=hover_color,
            activeforeground=text_color,
            relief=tk.FLAT,
            borderwidth=0,
            padx=padx,
            pady=pady,
            cursor="hand2"
        )
        
        # Add hover effect
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with Apple-like typography
        title_label = tk.Label(
            main_frame,
            text="NetCat File Transfer",
            font=self.fonts['title'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(pady=(0, 30))
        
        # Info card - IP and PIN
        info_card = tk.Frame(
            main_frame,
            bg=self.colors['card_bg'],
            relief=tk.FLAT,
            padx=20,
            pady=20
        )
        info_card.pack(fill=tk.X, pady=(0, 20))
        
        # IP Address section
        ip_section = tk.Frame(info_card, bg=self.colors['card_bg'])
        ip_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            ip_section,
            text="Your IP Address",
            font=self.fonts['body_small'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W)
        
        ip_value_frame = tk.Frame(ip_section, bg=self.colors['card_bg'])
        ip_value_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.ip_label = tk.Label(
            ip_value_frame,
            text=self.local_ip,
            font=self.fonts['mono'],
            bg=self.colors['card_bg'],
            fg=self.colors['accent_green'],
            anchor=tk.W
        )
        self.ip_label.pack(side=tk.LEFT)
        
        # PIN Code section
        pin_section = tk.Frame(info_card, bg=self.colors['card_bg'])
        pin_section.pack(fill=tk.X)
        
        pin_header = tk.Frame(pin_section, bg=self.colors['card_bg'])
        pin_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            pin_header,
            text="PIN Code",
            font=self.fonts['body_small'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(side=tk.LEFT)
        
        pin_value_frame = tk.Frame(pin_section, bg=self.colors['card_bg'])
        pin_value_frame.pack(fill=tk.X)
        
        self.pin_label = tk.Label(
            pin_value_frame,
            text=self.pin_code,
            font=self.fonts['mono'],
            bg=self.colors['card_bg'],
            fg=self.colors['accent'],
            anchor=tk.W
        )
        self.pin_label.pack(side=tk.LEFT)
        
        # Action buttons for PIN
        pin_buttons = tk.Frame(pin_value_frame, bg=self.colors['card_bg'])
        pin_buttons.pack(side=tk.RIGHT)
        
        refresh_pin_btn = self.create_modern_button(
            pin_buttons,
            text="New PIN",
            command=self.refresh_pin,
            size="small",
            color="secondary"
        )
        refresh_pin_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        discover_btn = self.create_modern_button(
            pin_buttons,
            text="Broadcast",
            command=self.broadcast_discovery,
            size="small",
            color="secondary"
        )
        discover_btn.pack(side=tk.LEFT)
        
        # Send File Section - Modern Card
        send_card = tk.Frame(
            main_frame,
            bg=self.colors['card_bg'],
            relief=tk.FLAT,
            padx=20,
            pady=20
        )
        send_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            send_card,
            text="Send File",
            font=self.fonts['heading'],
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # File selection
        file_section = tk.Frame(send_card, bg=self.colors['card_bg'])
        file_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            file_section,
            text="File",
            font=self.fonts['body_small'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        file_input_frame = tk.Frame(file_section, bg=self.colors['card_bg'])
        file_input_frame.pack(fill=tk.X)
        
        self.file_path_var = tk.StringVar(value="No file selected")
        file_label = tk.Label(
            file_input_frame,
            textvariable=self.file_path_var,
            font=self.fonts['body'],
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            anchor="w",
            padx=12,
            pady=10,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['input_border'],
            highlightcolor=self.colors['accent'],
            wraplength=400
        )
        file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        select_file_btn = self.create_modern_button(
            file_input_frame,
            text="Choose File",
            command=self.select_file,
            size="medium",
            color="secondary"
        )
        select_file_btn.pack(side=tk.RIGHT)
        
        # Receiver IP and PIN
        receiver_section = tk.Frame(send_card, bg=self.colors['card_bg'])
        receiver_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            receiver_section,
            text="Receiver",
            font=self.fonts['body_small'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        receiver_inputs = tk.Frame(receiver_section, bg=self.colors['card_bg'])
        receiver_inputs.pack(fill=tk.X)
        
        ip_label_frame = tk.Frame(receiver_inputs, bg=self.colors['card_bg'])
        ip_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(
            ip_label_frame,
            text="IP Address",
            font=self.fonts['body_tiny'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 3))
        
        self.receiver_ip_entry = self.create_modern_entry(ip_label_frame)
        self.receiver_ip_entry.pack(fill=tk.X)
        self.receiver_ip_entry.insert(0, "192.168.")
        
        pin_label_frame = tk.Frame(receiver_inputs, bg=self.colors['card_bg'])
        pin_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=(0, 10))
        
        tk.Label(
            pin_label_frame,
            text="PIN Code",
            font=self.fonts['body_tiny'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 3))
        
        self.receiver_pin_entry = self.create_modern_entry(pin_label_frame, width=12)
        self.receiver_pin_entry.pack(fill=tk.X)
        
        # Send button
        send_btn = self.create_modern_button(
            send_card,
            text="Send File",
            command=self.send_file,
            size="large",
            color="green"
        )
        send_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Receive File Section - Modern Card
        receive_card = tk.Frame(
            main_frame,
            bg=self.colors['card_bg'],
            relief=tk.FLAT,
            padx=20,
            pady=20
        )
        receive_card.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            receive_card,
            text="Receive File",
            font=self.fonts['heading'],
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Expected PIN
        pin_input_section = tk.Frame(receive_card, bg=self.colors['card_bg'])
        pin_input_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            pin_input_section,
            text="Expected PIN Code",
            font=self.fonts['body_small'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.expected_pin_entry = self.create_modern_entry(pin_input_section, width=15)
        self.expected_pin_entry.pack(anchor=tk.W)
        
        # Save location
        save_section = tk.Frame(receive_card, bg=self.colors['card_bg'])
        save_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            save_section,
            text="Save Location",
            font=self.fonts['body_small'],
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        save_input_frame = tk.Frame(save_section, bg=self.colors['card_bg'])
        save_input_frame.pack(fill=tk.X)
        
        self.save_path_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        save_label = tk.Label(
            save_input_frame,
            textvariable=self.save_path_var,
            font=self.fonts['body'],
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            anchor="w",
            padx=12,
            pady=10,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['input_border'],
            highlightcolor=self.colors['accent'],
            wraplength=400
        )
        save_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        select_save_btn = self.create_modern_button(
            save_input_frame,
            text="Choose",
            command=self.select_save_folder,
            size="medium",
            color="secondary"
        )
        select_save_btn.pack(side=tk.RIGHT)
        
        # Receive button
        receive_btn = self.create_modern_button(
            receive_card,
            text="Start Listening",
            command=self.start_receiving,
            size="large",
            color="blue"
        )
        receive_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Status/Log area - Modern Card
        log_card = tk.Frame(
            main_frame,
            bg=self.colors['card_bg'],
            relief=tk.FLAT,
            padx=20,
            pady=20
        )
        log_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_card,
            text="Status",
            font=self.fonts['heading'],
            bg=self.colors['card_bg'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_card,
            height=5,
            font=self.fonts['mono_small'],
            wrap=tk.WORD,
            bg=self.colors['input_bg'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors['input_border'],
            padx=12,
            pady=10,
            insertbackground=self.colors['text']
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text widget colors
        self.log_text.config(
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['button_text']
        )
        
        self.log("Application started")
        self.log(f"Local IP: {self.local_ip}")
        self.log(f"PIN Code: {self.pin_code}")
        self.log("Ready to send or receive files")
    
    def refresh_pin(self):
        """Generate a new PIN code"""
        self.pin_code = self.generate_pin()
        self.pin_label.config(text=self.pin_code)
        self.log(f"New PIN code generated: {self.pin_code}")
    
    def select_file(self):
        """Open file dialog to select a file to send"""
        filename = filedialog.askopenfilename(
            title="Select file to send",
            initialdir=os.path.expanduser("~")
        )
        if filename:
            self.file_path_var.set(filename)
            self.log(f"File selected: {os.path.basename(filename)}")
    
    def select_save_folder(self):
        """Open folder dialog to select save location"""
        folder = filedialog.askdirectory(
            title="Select folder to save received files",
            initialdir=os.path.expanduser("~/Downloads")
        )
        if folder:
            self.save_path_var.set(folder)
            self.log(f"Save location: {folder}")
    
    def log(self, message):
        """Add a message to the log area"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def send_file(self):
        """Send file to receiver using netcat"""
        file_path = self.file_path_var.get()
        if file_path == "No file selected" or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file to send")
            return
        
        receiver_ip = self.receiver_ip_entry.get().strip()
        if not receiver_ip:
            messagebox.showerror("Error", "Please enter receiver IP address")
            return
        
        receiver_pin = self.receiver_pin_entry.get().strip()
        if not receiver_pin:
            messagebox.showerror("Error", "Please enter receiver PIN code")
            return
        
        # Run netcat in a separate thread
        def send_thread():
            try:
                self.log(f"Sending file to {receiver_ip}...")
                self.log(f"File: {os.path.basename(file_path)}")
                
                # Use netcat to send file
                # Try different netcat flags for compatibility
                port = 12345
                import platform
                if platform.system() == "Darwin":  # macOS
                    # macOS netcat uses -N for immediate close
                    cmd = f"nc -N {receiver_ip} {port} < '{file_path}'"
                else:
                    # Linux netcat typically uses -w for timeout
                    cmd = f"nc -w 3 {receiver_ip} {port} < '{file_path}'"
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.log("File sent successfully!")
                    messagebox.showinfo("Success", "File sent successfully!")
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.log(f"Error sending file: {error_msg}")
                    messagebox.showerror("Error", f"Failed to send file:\n{error_msg}")
            except subprocess.TimeoutExpired:
                self.log("Error: Transfer timed out")
                messagebox.showerror("Error", "Transfer timed out")
            except Exception as e:
                self.log(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to send file:\n{str(e)}")
        
        threading.Thread(target=send_thread, daemon=True).start()
    
    def start_receiving(self):
        """Start listening for incoming file"""
        expected_pin = self.expected_pin_entry.get().strip()
        if not expected_pin:
            messagebox.showerror("Error", "Please enter expected PIN code")
            return
        
        save_folder = self.save_path_var.get()
        if not os.path.exists(save_folder):
            try:
                os.makedirs(save_folder, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create save folder:\n{str(e)}")
                return
        
        # Run netcat receiver in a separate thread
        def receive_thread():
            try:
                port = 12345
                self.log(f"Listening on port {port}...")
                self.log(f"Expected PIN: {expected_pin}")
                self.log("Waiting for file transfer...")
                
                # Use netcat to receive file
                # We'll save with a timestamp to avoid overwrites
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"received_file_{timestamp}"
                save_path = os.path.join(save_folder, filename)
                
                # Use netcat to listen and receive file
                import platform
                if platform.system() == "Darwin":  # macOS
                    # macOS netcat uses -l for listen
                    cmd = f"nc -l {port} > '{save_path}'"
                else:
                    # Linux netcat typically uses -l -p for listen on port
                    cmd = f"nc -l -p {port} > '{save_path}'"
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.log(f"File received and saved to: {save_path}")
                    messagebox.showinfo("Success", f"File received!\nSaved to: {save_path}")
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.log(f"Error receiving file: {error_msg}")
                    messagebox.showerror("Error", f"Failed to receive file:\n{error_msg}")
            except subprocess.TimeoutExpired:
                self.log("Error: Transfer timed out")
                messagebox.showerror("Error", "Transfer timed out")
            except Exception as e:
                self.log(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Failed to receive file:\n{str(e)}")
        
        threading.Thread(target=receive_thread, daemon=True).start()
    
    def start_discovery_listener(self):
        """Listen for network discovery broadcasts"""
        try:
            # Create UDP socket for discovery
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 12346))  # Use different port for discovery
            
            while self.discovery_running:
                try:
                    data, addr = sock.recvfrom(1024)
                    # Handle discovery message
                    # Format: "DISCOVERY:IP:PIN"
                    message = data.decode('utf-8')
                    if message.startswith("DISCOVERY:"):
                        parts = message.split(":")
                        if len(parts) >= 3:
                            peer_ip = parts[1]
                            peer_pin = parts[2]
                            self.discovered_peers[peer_ip] = peer_pin
                            self.log(f"Discovered peer: {peer_ip} (PIN: {peer_pin})")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.discovery_running:
                        self.log(f"Discovery error: {str(e)}")
        except Exception as e:
            self.log(f"Failed to start discovery: {str(e)}")
    
    def broadcast_discovery(self):
        """Broadcast this instance on the network"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            message = f"DISCOVERY:{self.local_ip}:{self.pin_code}"
            # Get broadcast address
            ip_parts = self.local_ip.split('.')
            broadcast_ip = '.'.join(ip_parts[:-1]) + '.255'
            sock.sendto(message.encode('utf-8'), (broadcast_ip, 12346))
            sock.close()
            self.log(f"Discovery broadcast sent (IP: {self.local_ip}, PIN: {self.pin_code})")
        except Exception as e:
            self.log(f"Discovery broadcast failed: {str(e)}")


def main():
    root = tk.Tk()
    app = NetcatTransferApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

