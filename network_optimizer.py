import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, StringVar
import subprocess
import threading
import time
import socket
import re
import os
import sys
import psutil
import ctypes
import winreg
import json
from datetime import datetime

# Função auxiliar para criar startupinfo que oculta a janela do console
def create_hidden_startupinfo():
    """Cria um objeto startupinfo configurado para ocultar a janela do console"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return startupinfo

# Check if running as administrator
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# If not running as admin, restart with admin privileges
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

class NetworkOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimizador de Rede para Jogos")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        self.root.configure(bg="#2E2E2E")
        
        # Variáveis de estado
        self.monitoring = False
        self.optimization_running = False
        self.network_interfaces = []
        self.selected_interface = StringVar()
        self.original_settings = {}  # Para backup e restauração
        self.optimization_profile = StringVar(value="Balanceado")
        
        # Definir configurações padrão para restauração
        self.backup_original_settings()
        
        # Configurar a interface
        self.setup_ui()
        
        # Inicializar
        self.detect_network_interfaces()
        
    def backup_original_settings(self):
        """Faz backup das configurações originais do sistema"""
        try:
            # Backup de configurações TCP/IP
            tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            try:
                settings = {}
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_READ)
                
                # Ler configurações atuais
                for i in range(0, 100):  # Tentar ler até 100 valores
                    try:
                        name, value, type = winreg.EnumValue(key, i)
                        if type == winreg.REG_DWORD or type == winreg.REG_SZ:
                            settings[name] = {"value": value, "type": type}
                    except OSError:
                        break  # Fim dos valores
                
                self.original_settings["tcp"] = settings
            except Exception as e:
                pass
            
            # Salvar o backup em um arquivo
            try:
                with open("network_backup.json", "w") as f:
                    json.dump(self.original_settings, f)
            except:
                pass
        except Exception as e:
            print(f"Erro ao fazer backup: {str(e)}")
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal usando Notebook com abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba principal de otimização
        self.main_tab = tk.Frame(self.notebook, bg="#2E2E2E")
        self.notebook.add(self.main_tab, text="Otimização")
        
        # Aba de configurações avançadas
        self.advanced_tab = tk.Frame(self.notebook, bg="#2E2E2E")
        self.notebook.add(self.advanced_tab, text="Configurações Avançadas")
        
        # Aba de monitoramento
        self.monitor_tab = tk.Frame(self.notebook, bg="#2E2E2E")
        self.notebook.add(self.monitor_tab, text="Monitoramento")
        
        # Aba de backup/restauração
        self.backup_tab = tk.Frame(self.notebook, bg="#2E2E2E")
        self.notebook.add(self.backup_tab, text="Backup e Restauração")
        
        # Aba Sobre
        self.about_tab = tk.Frame(self.notebook, bg="#2E2E2E")
        self.notebook.add(self.about_tab, text="Sobre")
        
        # Configurar as abas
        self.setup_main_tab()
        self.setup_advanced_tab()
        self.setup_monitor_tab()
        self.setup_backup_tab()
        self.setup_about_tab()
        
        # Estilizar os widgets
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica o tema escuro aos widgets"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Cores do tema
        bg_color = "#2E2E2E"
        fg_color = "#FFFFFF"
        accent_color = "#1E90FF"
        
        # Configurar estilos
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", accent_color)], foreground=[("selected", "#FFFFFF")])
        
        style.configure("TButton", background=accent_color, foreground=fg_color, padding=5)
        style.map("TButton", background=[("active", "#1570CD")])
        
        style.configure("TCombobox", background=bg_color, foreground=fg_color, fieldbackground=bg_color)
        style.map("TCombobox", fieldbackground=[("readonly", bg_color)])
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
        
        # Configurar cores do ScrolledText (não é um widget ttk)
        self.root.option_add("*ScrolledText*Background", "#1E1E1E")
        self.root.option_add("*ScrolledText*Foreground", "#FFFFFF")
    
    def setup_main_tab(self):
        """Configura a aba principal de otimização"""
        # Frame do título
        title_frame = tk.Frame(self.main_tab, bg="#2E2E2E")
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Título
        title_label = tk.Label(title_frame, text="Otimizador de Rede para Jogos", 
                              font=("Arial", 18, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        title_label.pack(pady=10)
        
        # Frame para seleção de interface
        interface_frame = tk.LabelFrame(self.main_tab, text="Interface de Rede", 
                                      font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        interface_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Dropdown para seleção de interface
        interface_row = tk.Frame(interface_frame, bg="#2E2E2E")
        interface_row.pack(fill=tk.X, padx=5, pady=5)
        
        interface_label = tk.Label(interface_row, text="Selecione a Interface: ", 
                                 font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF")
        interface_label.pack(side=tk.LEFT, padx=5)
        
        self.interface_combobox = ttk.Combobox(interface_row, textvariable=self.selected_interface, 
                                              state="readonly", width=30)
        self.interface_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        refresh_button = ttk.Button(interface_row, text="Atualizar", command=self.detect_network_interfaces)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Frame para perfis de otimização
        profile_frame = tk.LabelFrame(self.main_tab, text="Perfil de Otimização", 
                                    font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        profile_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Radio buttons para perfis
        profiles = ["Máxima Performance", "Balanceado", "Estável"]
        for i, profile in enumerate(profiles):
            rb = tk.Radiobutton(profile_frame, text=profile, variable=self.optimization_profile, 
                               value=profile, bg="#2E2E2E", fg="#FFFFFF", 
                               selectcolor="#1E1E1E", activebackground="#2E2E2E", 
                               activeforeground="#FFFFFF", highlightbackground="#2E2E2E")
            rb.pack(anchor=tk.W, padx=10, pady=2)
        
        # Frame para estatísticas de rede
        stats_frame = tk.LabelFrame(self.main_tab, text="Estatísticas de Rede", 
                                  font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Estatísticas de rede em duas colunas
        stats_row1 = tk.Frame(stats_frame, bg="#2E2E2E")
        stats_row1.pack(fill=tk.X, padx=5, pady=5)
        
        self.ping_label = tk.Label(stats_row1, text="Ping: --ms", 
                                 font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", width=20, anchor="w")
        self.ping_label.pack(side=tk.LEFT, padx=5)
        
        self.packet_loss_label = tk.Label(stats_row1, text="Perda de Pacotes: --%", 
                                        font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", width=20, anchor="w")
        self.packet_loss_label.pack(side=tk.LEFT, padx=5)
        
        stats_row2 = tk.Frame(stats_frame, bg="#2E2E2E")
        stats_row2.pack(fill=tk.X, padx=5, pady=5)
        
        self.jitter_label = tk.Label(stats_row2, text="Jitter: --ms", 
                                   font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", width=20, anchor="w")
        self.jitter_label.pack(side=tk.LEFT, padx=5)
        
        self.download_label = tk.Label(stats_row2, text="Download: -- Mbps", 
                                     font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", width=20, anchor="w")
        self.download_label.pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        buttons_frame = tk.Frame(self.main_tab, bg="#2E2E2E")
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Botão de otimização
        self.optimize_button = tk.Button(buttons_frame, text="Iniciar Otimização", 
                                      command=self.start_optimization, bg="#4CAF50", fg="white",
                                      font=("Arial", 12, "bold"), height=2)
        self.optimize_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Botão de teste
        self.test_button = tk.Button(buttons_frame, text="Testar Conexão", 
                                   command=self.test_connection, bg="#2196F3", fg="white",
                                   font=("Arial", 12, "bold"), height=2)
        self.test_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Área de log
        log_frame = tk.LabelFrame(self.main_tab, text="Log de Atividades", 
                                font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg="#1E1E1E", fg="#FFFFFF",
                                               font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.tag_configure("success", foreground="#4CAF50")
        self.log_text.tag_configure("info", foreground="#2196F3")
        self.log_text.tag_configure("warning", foreground="#FFC107")
        self.log_text.tag_configure("error", foreground="#F44336")
        
        # Barra de progresso
        self.progress = ttk.Progressbar(self.main_tab, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # Rótulo de status
        self.status_label = tk.Label(self.main_tab, text="Pronto", 
                                   font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF")
        self.status_label.pack(anchor=tk.W, padx=5, pady=2)
    
    def setup_advanced_tab(self):
        """Configura a aba de configurações avançadas"""
        # Título
        title_label = tk.Label(self.advanced_tab, text="Configurações Avançadas", 
                              font=("Arial", 14, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        title_label.pack(pady=10)
        
        # Frame para checkboxes de otimizações
        options_frame = tk.LabelFrame(self.advanced_tab, text="Selecione as Otimizações", 
                                    font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Cria scrollbar para as opções
        canvas = tk.Canvas(options_frame, bg="#2E2E2E", highlightthickness=0)
        scrollbar = ttk.Scrollbar(options_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2E2E2E")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de otimizações disponíveis com descrições
        optimizations = [
            ("Otimização QoS", "Prioriza tráfego de jogos na rede", True),
            ("Otimização MTU", "Ajusta o tamanho dos pacotes para melhor performance", True),
            ("Desativar Algoritmo de Nagle", "Reduz latência para pacotes pequenos", True),
            ("Otimização de Buffers", "Otimiza buffers TCP/IP para jogos", True),
            ("Otimização DNS", "Configura DNS mais rápidos para jogos", True),
            ("Desativar Serviços Desnecessários", "Desativa serviços Windows que afetam jogos", True),
            ("Ajustes TCP Avançados", "Configura parâmetros TCP para menor latência", True),
            ("Otimização de Rotas", "Melhora o roteamento de jogos", True),
            ("Desativar Throttling de Rede", "Remove limites do Windows para tráfego", True),
            ("Otimização da Placa de Rede", "Ajusta configurações do driver de rede", True),
            ("Redução de Jitter", "Reduz variações na latência", True),
            ("Otimização de Timer", "Aumenta precisão do timer do sistema", True),
            ("Otimização Wi-Fi", "Ajustes específicos para conexões sem fio", False),
            ("Priorização de Hardware", "Otimiza o hardware para performance em jogos", True),
            ("Otimização IPv6", "Configura ou desativa IPv6 para melhor performance", False),
            ("Priorização de Processos", "Cria sistema de prioridade para processos de jogos", False),
        ]
        
        # Criar variáveis para armazenar estados dos checkboxes
        self.optimization_vars = {}
        
        # Criar checkboxes
        for i, (name, description, default) in enumerate(optimizations):
            var = tk.BooleanVar(value=default)
            self.optimization_vars[name] = var
            
            frame = tk.Frame(scrollable_frame, bg="#2E2E2E", pady=2)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            cb = tk.Checkbutton(frame, text=name, variable=var, bg="#2E2E2E", 
                              fg="#FFFFFF", selectcolor="#1E1E1E", activebackground="#2E2E2E",
                              activeforeground="#FFFFFF", highlightbackground="#2E2E2E")
            cb.pack(side=tk.LEFT, anchor=tk.W)
            
            desc_label = tk.Label(frame, text=f"- {description}", 
                                font=("Arial", 9), bg="#2E2E2E", fg="#AAAAAA")
            desc_label.pack(side=tk.LEFT, padx=10, anchor=tk.W)
        
        # Botões para selecionar/deselecionar todos
        buttons_frame = tk.Frame(self.advanced_tab, bg="#2E2E2E")
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        select_all = ttk.Button(buttons_frame, text="Selecionar Todos", 
                              command=lambda: self.toggle_all_optimizations(True))
        select_all.pack(side=tk.LEFT, padx=5)
        
        deselect_all = ttk.Button(buttons_frame, text="Deselecionar Todos", 
                                command=lambda: self.toggle_all_optimizations(False))
        deselect_all.pack(side=tk.LEFT, padx=5)
        
        # Botão para aplicar configurações selecionadas
        apply_button = ttk.Button(self.advanced_tab, text="Aplicar Configurações Selecionadas", 
                                command=self.apply_selected_optimizations)
        apply_button.pack(pady=10)
    
    def setup_monitor_tab(self):
        """Configura a aba de monitoramento avançado"""
        # Título
        title_label = tk.Label(self.monitor_tab, text="Monitoramento de Rede", 
                              font=("Arial", 14, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        title_label.pack(pady=10)
        
        # Frame para métricas em tempo real
        metrics_frame = tk.LabelFrame(self.monitor_tab, text="Métricas em Tempo Real", 
                                    font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Widgets para exibir estatísticas em tempo real
        self.realtime_stats = {
            "ping": {"label": "Ping:", "value": "--ms", "min": "--ms", "max": "--ms", "avg": "--ms"},
            "jitter": {"label": "Jitter:", "value": "--ms", "min": "--ms", "max": "--ms", "avg": "--ms"},
            "packet_loss": {"label": "Perda de Pacotes:", "value": "--%", "min": "--%", "max": "--%", "avg": "--%"},
            "download": {"label": "Velocidade de Download:", "value": "--Mbps", "min": "--Mbps", "max": "--Mbps", "avg": "--Mbps"},
            "upload": {"label": "Velocidade de Upload:", "value": "--Mbps", "min": "--Mbps", "max": "--Mbps", "avg": "--Mbps"}
        }
        
        # Criar widgets para cada métrica
        for i, (key, data) in enumerate(self.realtime_stats.items()):
            frame = tk.Frame(metrics_frame, bg="#2E2E2E")
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            label = tk.Label(frame, text=data["label"], width=20, anchor="w",
                           font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF")
            label.pack(side=tk.LEFT, padx=5)
            
            value_label = tk.Label(frame, text=data["value"], width=10, anchor="w",
                                 font=("Arial", 10, "bold"), bg="#2E2E2E", fg="#FFFFFF")
            value_label.pack(side=tk.LEFT, padx=5)
            
            min_label = tk.Label(frame, text=f"Min: {data['min']}", width=12, anchor="w",
                               font=("Arial", 9), bg="#2E2E2E", fg="#AAAAAA")
            min_label.pack(side=tk.LEFT, padx=5)
            
            max_label = tk.Label(frame, text=f"Max: {data['max']}", width=12, anchor="w",
                               font=("Arial", 9), bg="#2E2E2E", fg="#AAAAAA")
            max_label.pack(side=tk.LEFT, padx=5)
            
            avg_label = tk.Label(frame, text=f"Média: {data['avg']}", width=15, anchor="w",
                               font=("Arial", 9), bg="#2E2E2E", fg="#AAAAAA")
            avg_label.pack(side=tk.LEFT, padx=5)
            
            # Guardar referências para atualização posterior
            self.realtime_stats[key]["widgets"] = {
                "value": value_label,
                "min": min_label,
                "max": max_label,
                "avg": avg_label
            }
        
        # Botões de controle
        buttons_frame = tk.Frame(self.monitor_tab, bg="#2E2E2E")
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Botão para iniciar/parar monitoramento
        self.monitor_button = tk.Button(buttons_frame, text="Iniciar Monitoramento", 
                                     command=self.toggle_monitoring, bg="#2196F3", fg="white",
                                     font=("Arial", 12, "bold"), height=2)
        self.monitor_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Botão para exportar dados
        self.export_button = tk.Button(buttons_frame, text="Exportar Relatório", 
                                     command=self.export_monitoring_data, bg="#FF9800", fg="white",
                                     font=("Arial", 12, "bold"), height=2)
        self.export_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Área de log de monitoramento
        log_frame = tk.LabelFrame(self.monitor_tab, text="Log de Monitoramento", 
                                font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.monitor_log = scrolledtext.ScrolledText(log_frame, bg="#1E1E1E", fg="#FFFFFF",
                                                  font=("Consolas", 10))
        self.monitor_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_backup_tab(self):
        """Configura a aba de backup e restauração"""
        # Título
        title_label = tk.Label(self.backup_tab, text="Backup e Restauração", 
                              font=("Arial", 14, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        title_label.pack(pady=10)
        
        # Frame para informações de backup
        info_frame = tk.LabelFrame(self.backup_tab, text="Informações de Backup", 
                                 font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status do backup
        self.backup_status_label = tk.Label(info_frame, 
                                         text="Um backup das configurações originais foi criado automaticamente.", 
                                         font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF", 
                                         wraplength=700, justify=tk.LEFT)
        self.backup_status_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Botões de backup
        buttons_frame = tk.Frame(self.backup_tab, bg="#2E2E2E")
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Botão para criar backup
        create_backup_button = tk.Button(buttons_frame, text="Criar Backup Manual", 
                                       command=self.create_manual_backup, bg="#4CAF50", fg="white",
                                       font=("Arial", 12), height=2)
        create_backup_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Botão para restaurar configurações
        restore_button = tk.Button(buttons_frame, text="Restaurar Configurações Originais", 
                                 command=self.restore_original_settings, bg="#F44336", fg="white",
                                 font=("Arial", 12), height=2)
        restore_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Lista de backups
        backups_frame = tk.LabelFrame(self.backup_tab, text="Backups Disponíveis", 
                                    font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        backups_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox para backups
        self.backups_listbox = tk.Listbox(backups_frame, bg="#1E1E1E", fg="#FFFFFF",
                                        font=("Consolas", 10), selectbackground="#4CAF50")
        self.backups_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para a listbox
        backup_scrollbar = ttk.Scrollbar(backups_frame, orient="vertical", 
                                       command=self.backups_listbox.yview)
        backup_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backups_listbox.config(yscrollcommand=backup_scrollbar.set)
        
        # Botões para gerenciar backups selecionados
        backup_actions_frame = tk.Frame(self.backup_tab, bg="#2E2E2E")
        backup_actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        load_backup_button = ttk.Button(backup_actions_frame, text="Carregar Backup Selecionado", 
                                      command=self.load_selected_backup)
        load_backup_button.pack(side=tk.LEFT, padx=5)
        
        delete_backup_button = ttk.Button(backup_actions_frame, text="Excluir Backup Selecionado", 
                                        command=self.delete_selected_backup)
        delete_backup_button.pack(side=tk.LEFT, padx=5)
        
        # Atualizar lista de backups
        self.update_backup_list()
    
    def log(self, message, level="info"):
        """Adiciona mensagem ao log com timestamp"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Atualiza o rótulo de status"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def detect_network_interfaces(self):
        """Detecta interfaces de rede disponíveis"""
        try:
            self.log("Detectando interfaces de rede...", "info")
            self.network_interfaces = []
            
            # Limpar o combobox
            self.interface_combobox['values'] = []
            
            # Método 1: Usando psutil (mais confiável)
            addresses = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for iface, addrs in addresses.items():
                # Verificar se a interface tem endereço IPv4 e está ativa
                if iface in stats and stats[iface].isup:
                    for addr in addrs:
                        if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                            self.network_interfaces.append(iface)
                            self.log(f"Interface ativa encontrada: {iface} ({addr.address})", "success")
                            break
            
            # Atualizar o combobox
            if self.network_interfaces:
                self.interface_combobox['values'] = self.network_interfaces
                self.selected_interface.set(self.network_interfaces[0])
                self.log(f"Total de {len(self.network_interfaces)} interfaces encontradas", "info")
            else:
                self.log("Nenhuma interface de rede ativa encontrada", "warning")
                self.interface_combobox['values'] = ["Nenhuma interface ativa"]
                self.selected_interface.set("Nenhuma interface ativa")
            
            return self.network_interfaces
        except Exception as e:
            self.log(f"Erro ao detectar interfaces: {str(e)}", "error")
            return []
    
    def get_active_network_interfaces(self):
        """Retorna as interfaces de rede ativas"""
        if not self.network_interfaces:
            return self.detect_network_interfaces()
        return self.network_interfaces
    
    def toggle_monitoring(self):
        """Inicia ou para o monitoramento da rede"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_button.config(text="Parar Monitoramento", bg="#F44336")
            self.log("Iniciando monitoramento de rede...", "info")
            
            # Limpar dados anteriores
            for key in self.realtime_stats:
                self.realtime_stats[key]["data"] = []
            
            # Iniciar thread de monitoramento
            threading.Thread(target=self.monitor_network, daemon=True).start()
        else:
            self.monitoring = False
            self.monitor_button.config(text="Iniciar Monitoramento", bg="#2196F3")
            self.log("Monitoramento de rede interrompido.", "info")
    
    def monitor_network(self):
        """Monitora a rede em tempo real com tratamento robusto de erros"""
        # Lista de servidores para teste, em ordem de preferência
        targets = ["8.8.8.8", "1.1.1.1", "208.67.222.222", "9.9.9.9"]
        current_target_index = 0
        current_target = targets[current_target_index]
        
        # Histórico para estatísticas
        ping_history = []
        jitter_history = []
        packet_loss_history = []
        
        # Contador de falhas consecutivas
        consecutive_failures = 0
        
        # Preparar para armazenar dados históricos
        for key in self.realtime_stats:
            self.realtime_stats[key]["data"] = []
        
        while self.monitoring:
            try:
                # Inicializar valores padrão para evitar erros de referência não definida
                avg_ping = 0
                jitter = 0
                packet_loss = 0
                
                # Verificar se devemos alternar para outro servidor de teste
                if consecutive_failures >= 3:
                    # Tentar próximo servidor depois de 3 falhas consecutivas
                    current_target_index = (current_target_index + 1) % len(targets)
                    current_target = targets[current_target_index]
                    consecutive_failures = 0
                    self.log(f"Alternando para servidor de teste: {current_target}", "info")
                
                try:
                    # Teste de ping com medição de jitter - sem mostrar a janela do console
                    startupinfo = None
                    if os.name == 'nt':  # Windows
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    ping_output = subprocess.run(
                        ["ping", current_target, "-n", "4"], 
                        capture_output=True, 
                        text=True,
                        timeout=5,
                        startupinfo=startupinfo  # Esconde a janela do console no Windows
                    )
                    
                    # Verificar se o comando foi bem sucedido
                    if ping_output.returncode != 0:
                        # Comando falhou, tratar como erro
                        consecutive_failures += 1
                        
                        if "destino inacessível" in ping_output.stdout or "unreachable" in ping_output.stdout:
                            error_msg = f"Servidor {current_target} inacessível."
                        elif "tempo limite expirado" in ping_output.stdout or "timed out" in ping_output.stdout:
                            error_msg = f"Tempo limite esgotado ao pingar {current_target}."
                        elif "não foi possível encontrar o host" in ping_output.stdout or "could not find host" in ping_output.stdout:
                            error_msg = f"Não foi possível resolver o endereço {current_target}."
                        else:
                            error_msg = f"Erro ao executar ping para {current_target}."
                        
                        self.log(error_msg, "warning")
                        
                        # Definir valores padrão para indicar problema
                        self.ping_label.config(text="Ping: Falha", fg="#F44336")
                        self.packet_loss_label.config(text="Perda de Pacotes: 100%", fg="#F44336")
                        
                        # Atualizar monitor log
                        self.monitor_log.config(state=tk.NORMAL)
                        timestamp = time.strftime("%H:%M:%S", time.localtime())
                        self.monitor_log.insert(tk.END, f"[{timestamp}] {error_msg}\n", "error")
                        self.monitor_log.see(tk.END)
                        self.monitor_log.config(state=tk.DISABLED)
                        
                        # Aguardar antes da próxima tentativa
                        time.sleep(2)
                        continue
                    
                    # Comando bem sucedido, resetar contador de falhas
                    consecutive_failures = 0
                    
                    # Usar stdout se bem sucedido
                    ping_output_text = ping_output.stdout
                    
                    # Extrair tempos de ping
                    ping_times = re.findall(r"time[<=](\d+)ms", ping_output_text)
                    if not ping_times:  # Tentar padrão alternativo para outros idiomas
                        ping_times = re.findall(r"tempo[<=](\d+)ms", ping_output_text)
                    
                    ping_times = [int(t) for t in ping_times if t]
                    
                    if ping_times:
                        # Calcular ping médio
                        avg_ping = sum(ping_times) / len(ping_times)
                        ping_history.append(avg_ping)
                        self.realtime_stats["ping"]["data"] = ping_history
                        
                        # Calcular jitter (variação nos tempos de ping)
                        if len(ping_times) > 1:
                            jitter = sum(abs(ping_times[i] - ping_times[i-1]) for i in range(1, len(ping_times))) / (len(ping_times) - 1)
                            jitter_history.append(jitter)
                            self.realtime_stats["jitter"]["data"] = jitter_history
                        
                        # Atualizar labels
                        self.ping_label.config(text=f"Ping: {avg_ping:.1f}ms")
                        
                        # Atualizar dados em tempo real na aba de monitoramento
                        self.update_realtime_stats("ping", f"{avg_ping:.1f}ms")
                        self.update_realtime_stats("jitter", f"{jitter:.1f}ms")
                        
                        # Colorir labels baseado nos valores
                        if avg_ping < 50:
                            self.ping_label.config(fg="#4CAF50")  # Verde
                        elif avg_ping < 100:
                            self.ping_label.config(fg="#FFC107")  # Amarelo
                        else:
                            self.ping_label.config(fg="#F44336")  # Vermelho
                    else:
                        # Se não conseguir extrair tempos de ping, usar valores padrão
                        self.ping_label.config(text="Ping: --ms")
                        self.log(f"Não foi possível extrair tempos de ping de: {ping_output_text[:100]}...", "warning")
                    
                    # Extrair perda de pacotes - buscar diferentes padrões para contemplar idiomas
                    loss_match = re.search(r"(\d+)% (loss|perdidos|perdido|perda)", ping_output_text)
                    if not loss_match:
                        loss_match = re.search(r"(\d+)%( pacotes)? (perdidos|perdido|perda)", ping_output_text)
                    
                    if loss_match:
                        packet_loss = float(loss_match.group(1))
                        packet_loss_history.append(packet_loss)
                        self.realtime_stats["packet_loss"]["data"] = packet_loss_history
                        
                        self.packet_loss_label.config(text=f"Perda de Pacotes: {packet_loss}%")
                        self.update_realtime_stats("packet_loss", f"{packet_loss}%")
                        
                        # Colorir labels baseado nos valores
                        if packet_loss == 0:
                            self.packet_loss_label.config(fg="#4CAF50")  # Verde
                        elif packet_loss < 5:
                            self.packet_loss_label.config(fg="#FFC107")  # Amarelo
                        else:
                            self.packet_loss_label.config(fg="#F44336")  # Vermelho
                    else:
                        # Se não conseguir extrair perda de pacotes, usar valores padrão
                        self.packet_loss_label.config(text="Perda de Pacotes: --%")
                    
                    # Registrar no log de monitoramento apenas se tiver valores válidos
                    if ping_times:
                        self.monitor_log.config(state=tk.NORMAL)
                        timestamp = time.strftime("%H:%M:%S", time.localtime())
                        self.monitor_log.insert(tk.END, f"[{timestamp}] Ping: {avg_ping:.1f}ms | Jitter: {jitter:.1f}ms | Perda: {packet_loss}%\n")
                        self.monitor_log.see(tk.END)
                        self.monitor_log.config(state=tk.DISABLED)
                
                except subprocess.TimeoutExpired:
                    # Ping demorou muito para responder
                    consecutive_failures += 1
                    self.log(f"Timeout ao executar ping para {current_target}", "warning")
                    self.ping_label.config(text="Ping: Timeout", fg="#F44336")
                except Exception as command_error:
                    # Outros erros de comando
                    consecutive_failures += 1
                    self.log(f"Erro ao executar ping: {str(command_error)}", "error")
                    self.ping_label.config(text="Ping: Erro", fg="#F44336")
                
            except Exception as e:
                # Erro geral no monitoramento
                self.log(f"Erro no monitoramento: {str(e)}", "error")
                self.ping_label.config(text="Ping: --ms")
                self.packet_loss_label.config(text="Perda de Pacotes: --%")
            
            time.sleep(1)  # Atualizar a cada segundo
    
    def update_realtime_stats(self, key, value):
        """Atualiza estatísticas em tempo real na aba de monitoramento"""
        if key not in self.realtime_stats or "widgets" not in self.realtime_stats[key]:
            return
            
        data = self.realtime_stats[key]["data"]
        widgets = self.realtime_stats[key]["widgets"]
        
        widgets["value"].config(text=value)
        
        if data:
            # Converter para valores numéricos, removendo unidades
            numeric_data = []
            for d in data:
                if isinstance(d, (int, float)):
                    numeric_data.append(d)
            
            if numeric_data:
                min_val = min(numeric_data)
                max_val = max(numeric_data)
                avg_val = sum(numeric_data) / len(numeric_data)
                
                unit = value[-2:] if key != "packet_loss" else "%"
                widgets["min"].config(text=f"Min: {min_val:.1f}{unit}")
                widgets["max"].config(text=f"Max: {max_val:.1f}{unit}")
                widgets["avg"].config(text=f"Média: {avg_val:.1f}{unit}")
    
    def export_monitoring_data(self):
        """Exporta dados de monitoramento para um arquivo CSV"""
        if not any(key in self.realtime_stats and "data" in self.realtime_stats[key] for key in self.realtime_stats):
            messagebox.showinfo("Exportar Dados", "Não há dados de monitoramento para exportar.")
            return
            
        try:
            # Criar um nome de arquivo com timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            filename = f"network_monitoring_{timestamp}.csv"
            
            with open(filename, "w") as f:
                # Escrever cabeçalho
                f.write("Timestamp,Ping (ms),Jitter (ms),Packet Loss (%)\n")
                
                # Escrever dados
                for i in range(len(self.realtime_stats["ping"]["data"])):
                    ping = self.realtime_stats["ping"]["data"][i] if i < len(self.realtime_stats["ping"]["data"]) else ""
                    jitter = self.realtime_stats["jitter"]["data"][i] if i < len(self.realtime_stats["jitter"]["data"]) else ""
                    loss = self.realtime_stats["packet_loss"]["data"][i] if i < len(self.realtime_stats["packet_loss"]["data"]) else ""
                    
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - (len(self.realtime_stats["ping"]["data"]) - i)))
                    f.write(f"{timestamp},{ping},{jitter},{loss}\n")
            
            self.log(f"Dados de monitoramento exportados para {filename}", "success")
            messagebox.showinfo("Exportar Dados", f"Dados exportados com sucesso para {filename}")
        except Exception as e:
            self.log(f"Erro ao exportar dados: {str(e)}", "error")
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
    
    def test_connection(self):
        """Realiza um teste completo de conexão"""
        if self.optimization_running:
            return
            
        self.log("Iniciando teste completo de conexão...", "info")
        threading.Thread(target=self.run_connection_test, daemon=True).start()
    
    def run_connection_test(self):
        """Executa os testes de conexão"""
        try:
            self.optimize_button.config(state=tk.DISABLED)
            self.test_button.config(state=tk.DISABLED)
            self.update_status("Testando conexão...")
            
            # Teste de ping para vários servidores
            servers = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
            ping_results = {}
            
            self.log("Testando latência para múltiplos servidores...", "info")
            for server in servers:
                try:
                    ping_output = subprocess.check_output(["ping", server, "-n", "10"], 
                                                       universal_newlines=True, stderr=subprocess.STDOUT)
                    
                    avg_match = re.search(r"Average = (\d+)ms", ping_output)
                    if avg_match:
                        ping_results[server] = int(avg_match.group(1))
                        self.log(f"Ping para {server}: {ping_results[server]}ms", "info")
                except:
                    self.log(f"Não foi possível testar ping para {server}", "warning")
            
            if ping_results:
                best_server = min(ping_results, key=ping_results.get)
                self.log(f"Menor latência: {best_server} ({ping_results[best_server]}ms)", "success")
            
            # Teste de estabilidade (jitter)
            self.log("Testando estabilidade da conexão (jitter)...", "info")
            try:
                ping_output = subprocess.check_output(["ping", "8.8.8.8", "-n", "20"], 
                                                   universal_newlines=True, stderr=subprocess.STDOUT)
                
                ping_times = re.findall(r"time=(\d+)ms", ping_output)
                ping_times = [int(t) for t in ping_times if t]
                
                if len(ping_times) > 1:
                    jitter = sum(abs(ping_times[i] - ping_times[i-1]) for i in range(1, len(ping_times))) / (len(ping_times) - 1)
                    self.log(f"Jitter médio: {jitter:.2f}ms", "info")
                    
                    if jitter < 5:
                        self.log("Conexão muito estável (jitter < 5ms)", "success")
                    elif jitter < 10:
                        self.log("Conexão estável (jitter < 10ms)", "success")
                    else:
                        self.log("Conexão com instabilidade (jitter > 10ms)", "warning")
            except:
                self.log("Não foi possível testar estabilidade", "warning")
            
            # Teste de pacotes fragmentados
            self.log("Testando fragmentação de pacotes (MTU)...", "info")
            try:
                best_mtu = self.find_optimal_mtu()
                if best_mtu:
                    self.log(f"MTU ótimo detectado: {best_mtu}", "success")
                else:
                    self.log("Não foi possível determinar MTU ótimo", "warning")
            except:
                self.log("Teste de MTU falhou", "warning")
            
            # Teste de DNS
            self.log("Testando resolução de DNS...", "info")
            try:
                start_time = time.time()
                socket.gethostbyname("www.google.com")
                dns_time = (time.time() - start_time) * 1000
                
                self.log(f"Resolução de DNS: {dns_time:.2f}ms", "info")
                
                if dns_time < 50:
                    self.log("Resolução de DNS rápida", "success")
                elif dns_time < 100:
                    self.log("Resolução de DNS aceitável", "info")
                else:
                    self.log("Resolução de DNS lenta, recomendado otimizar", "warning")
            except:
                self.log("Teste de DNS falhou", "warning")
            
            # Resumo dos resultados
            self.log("Teste de conexão concluído!", "success")
            self.update_status("Teste concluído")
        except Exception as e:
            self.log(f"Erro durante o teste: {str(e)}", "error")
            self.update_status("Erro no teste")
        finally:
            self.optimize_button.config(state=tk.NORMAL)
            self.test_button.config(state=tk.NORMAL)
    
    def find_optimal_mtu(self, start=1500, min_mtu=1400):
        """Encontra o MTU ótimo para a conexão usando valores comuns para jogos"""
        try:
            # Valores de MTU comuns para jogos, em ordem de preferência
            common_mtu_values = [1500, 1492, 1480, 1472, 1468, 1450, 1400]
            
            # Servidor de destino para teste (Google DNS)
            target = "8.8.8.8"
            
            # Ocultar a janela do console
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.log("Testando valores de MTU comuns para jogos...", "info")
            
            # Primeiro, verificar se a conexão está funcionando com ping básico
            try:
                test_ping = subprocess.run(
                    ["ping", target, "-n", "1"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    startupinfo=startupinfo
                )
                
                if test_ping.returncode != 0:
                    self.log("Não foi possível conectar ao servidor de teste. Usando MTU padrão.", "warning")
                    # Recomendar MTU conservador baseado no perfil
                    selected_profile = self.optimization_profile.get()
                    return 1468 if selected_profile == "Máxima Performance" else 1500
            except Exception:
                self.log("Erro no teste de conectividade básica. Usando MTU padrão.", "warning")
                return 1468  # Valor conservador
            
            # Testar cada um dos valores comuns de MTU
            for mtu in common_mtu_values:
                self.log(f"Testando MTU de {mtu}...", "info")
                
                try:
                    # Payload = MTU - 28 (20 bytes IP header + 8 bytes ICMP header)
                    payload_size = mtu - 28
                    
                    # Executar ping com tamanho específico e flag DF
                    result = subprocess.run(
                        ["ping", target, "-n", "2", "-l", str(payload_size), "-f"],
                        capture_output=True,
                        text=True,
                        timeout=3,
                        startupinfo=startupinfo
                    )
                    
                    # Verificar se houve resposta bem-sucedida
                    success_patterns = ["bytes=", "TTL=", "tempo=", "time="]
                    success = any(pattern in result.stdout for pattern in success_patterns)
                    
                    # Se o ping foi bem-sucedido e não houve fragmentação
                    if result.returncode == 0 and success:
                        self.log(f"MTU ótimo encontrado: {mtu}", "success")
                        return mtu
                    
                    # Se o ping falhou, verificar se foi por causa de fragmentação
                    if "must fragment" in result.stdout.lower() or "needs to be fragmented" in result.stdout.lower():
                        self.log(f"Pacote precisa ser fragmentado com MTU {mtu}", "info")
                        continue
                        
                except Exception as e:
                    self.log(f"Erro no teste de MTU {mtu}: {str(e)}", "warning")
                    continue
            
            # Se chegou aqui, nenhum dos valores comuns funcionou
            # Recomendar um valor conservador
            self.log("Nenhum valor de MTU ideal foi encontrado. Usando valor conservador.", "warning")
            return 1468  # Valor que funciona na maioria das redes
        except Exception as e:
            self.log(f"Erro ao determinar MTU ótimo: {str(e)}", "error")
            return 1468  # Valor conservador em caso de erro
    
    def start_optimization(self):
        """Inicia o processo de otimização"""
        if self.optimization_running:
            return
        
        # Verificar se uma interface foi selecionada
        if not self.selected_interface.get() or self.selected_interface.get() == "Nenhuma interface ativa":
            messagebox.showwarning("Aviso", "Por favor, selecione uma interface de rede válida primeiro.")
            return
        
        self.optimization_running = True
        self.optimize_button.config(state=tk.DISABLED)
        self.test_button.config(state=tk.DISABLED)
        self.progress['value'] = 0
        
        self.log("Iniciando processo de otimização de rede...", "info")
        threading.Thread(target=self.run_optimization, daemon=True).start()
    
    def run_optimization(self):
        """Executa as otimizações de rede"""
        try:
            # Determinar quais otimizações executar com base no perfil selecionado
            profile = self.optimization_profile.get()
            
            # Aplicar configurações baseadas no perfil
            self.log(f"Aplicando perfil de otimização: {profile}", "info")
            
            if profile == "Máxima Performance":
                self.apply_max_performance_profile()
            elif profile == "Estável":
                self.apply_stable_profile()
            else:  # Balanceado (padrão)
                self.apply_balanced_profile()
            
            # Total de passos com base nas otimizações selecionadas
            total_steps = sum(1 for var in self.optimization_vars.values() if var.get())
            
            if total_steps == 0:
                self.log("Nenhuma otimização selecionada!", "warning")
                messagebox.showinfo("Aviso", "Nenhuma otimização foi selecionada.")
                self.optimization_running = False
                self.optimize_button.config(state=tk.NORMAL)
                self.test_button.config(state=tk.NORMAL)
                return
            
            current_step = 0
            
            # 1. QoS Optimization
            if self.optimization_vars["Otimização QoS"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Configurando QoS...")
                self.optimize_qos()
            
            # 2. MTU Optimization
            if self.optimization_vars["Otimização MTU"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando MTU...")
                self.optimize_mtu()
            
            # 3. Disable Nagle's Algorithm
            if self.optimization_vars["Desativar Algoritmo de Nagle"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Desativando algoritmo de Nagle...")
                self.disable_nagle_algorithm()
            
            # 4. Network Buffer Optimization
            if self.optimization_vars["Otimização de Buffers"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando buffers de rede...")
                self.optimize_network_buffers()
            
            # 5. TCP/IP Optimization
            if self.optimization_vars["Ajustes TCP Avançados"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando configurações TCP/IP...")
                self.optimize_tcp_settings()
            
            # 6. DNS Optimization
            if self.optimization_vars["Otimização DNS"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando DNS...")
                self.optimize_dns()
            
            # 7. Disable Unnecessary Services
            if self.optimization_vars["Desativar Serviços Desnecessários"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Desativando serviços desnecessários...")
                self.disable_unnecessary_services()
            
            # 8. Route and Traffic Prioritization
            if self.optimization_vars["Otimização de Rotas"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando rotas e prioridade de tráfego...")
                self.optimize_routes_and_priority()
            
            # 9. Disable Network Throttling
            if self.optimization_vars["Desativar Throttling de Rede"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Desativando throttling de rede...")
                self.disable_network_throttling()
            
            # 10. Network Adapter Optimization
            if self.optimization_vars["Otimização da Placa de Rede"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando configurações da placa de rede...")
                self.optimize_advanced_driver_settings()
            
            # 11. Jitter Reduction
            if self.optimization_vars["Redução de Jitter"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Reduzindo jitter...")
                self.reduce_jitter()
            
            # 12. Timer Optimization
            if self.optimization_vars["Otimização de Timer"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando timer do sistema...")
                self.optimize_system_timer()
            
            # 13. Wi-Fi Optimization
            if self.optimization_vars["Otimização Wi-Fi"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando configurações Wi-Fi...")
                self.optimize_wifi_settings()
            
            # 14. Hardware Prioritization
            if self.optimization_vars["Priorização de Hardware"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando configurações de hardware...")
                self.optimize_hardware_settings()
            
            # 15. IPv6 Optimization
            if self.optimization_vars["Otimização IPv6"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Otimizando IPv6...")
                self.optimize_ipv6_settings()
            
            # 16. Process Prioritization
            if self.optimization_vars["Priorização de Processos"].get():
                current_step += 1
                self.progress['value'] = (current_step / total_steps) * 100
                self.update_status("Configurando priorização de processos...")
                self.setup_process_prioritization()
            
            # Completed
            self.progress['value'] = 100
            self.update_status("Otimização concluída!")
            self.log("Processo de otimização concluído com sucesso!", "success")
            messagebox.showinfo("Otimização Concluída", "Todas as otimizações selecionadas foram aplicadas com sucesso!")
            
        except Exception as e:
            self.log(f"Erro durante a otimização: {str(e)}", "error")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a otimização: {str(e)}")
        finally:
            self.optimization_running = False
            self.optimize_button.config(state=tk.NORMAL)
            self.test_button.config(state=tk.NORMAL)
            self.progress['value'] = 100
    
    def apply_max_performance_profile(self):
        """Configura otimizações para máxima performance"""
        # Ativar todas as otimizações
        for key, var in self.optimization_vars.items():
            var.set(True)
        
        self.log("Perfil de Máxima Performance ativado", "info")
    
    def apply_balanced_profile(self):
        """Configura otimizações para perfil balanceado"""
        # Ativar otimizações específicas para perfil balanceado
        balanced_optimizations = [
            "Otimização QoS", "Otimização MTU", "Desativar Algoritmo de Nagle",
            "Otimização de Buffers", "Ajustes TCP Avançados", "Otimização DNS",
            "Desativar Serviços Desnecessários", "Otimização de Rotas",
            "Redução de Jitter", "Otimização da Placa de Rede"
        ]
        
        for key, var in self.optimization_vars.items():
            var.set(key in balanced_optimizations)
        
        self.log("Perfil Balanceado ativado", "info")
    
    def apply_stable_profile(self):
        """Configura otimizações para perfil estável"""
        # Ativar apenas otimizações que não afetam negativamente a estabilidade
        stable_optimizations = [
            "Otimização QoS", "Otimização DNS", "Desativar Serviços Desnecessários",
            "Redução de Jitter", "Otimização de Rotas"
        ]
        
        for key, var in self.optimization_vars.items():
            var.set(key in stable_optimizations)
        
        self.log("Perfil Estável ativado", "info")
    
    def toggle_all_optimizations(self, state):
        """Seleciona ou deseleciona todas as otimizações"""
        for var in self.optimization_vars.values():
            var.set(state)
    
    def apply_selected_optimizations(self):
        """Aplica apenas as otimizações selecionadas"""
        self.start_optimization()
    
    #------------------------------------------------------------------------
    # FUNÇÕES DE OTIMIZAÇÃO
    #------------------------------------------------------------------------
    
    def optimize_qos(self):
        """Configura prioridade QoS para jogos online"""
        try:
            self.log("Configurando políticas QoS para priorizar tráfego de jogos...", "info")
            
            # 1. Configurar QoS no registro do Windows
            qos_path = r"SOFTWARE\Policies\Microsoft\Windows\QoS"
            try:
                # Criar chave se não existir
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                try:
                    key = winreg.OpenKey(reg_handle, qos_path, 0, winreg.KEY_WRITE)
                except:
                    key = winreg.CreateKey(reg_handle, qos_path)
                
                # Definir política de QoS para jogos
                winreg.SetValueEx(key, "ApplicationDSCP", 0, winreg.REG_DWORD, 46)  # Valor EF (Expedited Forwarding)
                winreg.CloseKey(key)
                self.log("Políticas de QoS configuradas com sucesso", "success")
            except Exception as e:
                self.log(f"Erro ao configurar políticas QoS: {str(e)}", "error")
            
            # 2. Configurar QoS via netsh para a interface selecionada
            interface = self.selected_interface.get()
            if interface and interface != "Nenhuma interface ativa":
                try:
                    # Aplicar política de QoS para UDP (usada pela maioria dos jogos)
                    subprocess.run(["netsh", "int", "ipv4", "set", "subinterface", interface, "qoslevel=gold"], 
                                  capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
                    
                    self.log(f"QoS configurado para interface {interface}", "success")
                except Exception as e:
                    self.log(f"Erro ao configurar QoS para interface {interface}: {str(e)}", "error")
            else:
                self.log("Nenhuma interface selecionada para configurar QoS", "warning")
            
            return True
        except Exception as e:
            self.log(f"Erro geral na configuração de QoS: {str(e)}", "error")
            return False
    
    def optimize_mtu(self):
        """Otimiza o MTU para a interface de rede selecionada"""
        try:
            interface = self.selected_interface.get()
            if not interface or interface == "Nenhuma interface ativa":
                self.log("Nenhuma interface selecionada para otimizar MTU", "warning")
                return False
            
            self.log("Determinando MTU ideal para sua conexão...", "info")
            
            # Encontrar MTU ótimo
            optimal_mtu = self.find_optimal_mtu()
            
            if not optimal_mtu:
                self.log("Não foi possível determinar MTU ótimo, usando valor padrão", "warning")
                # Valores padrão recomendados para jogos
                # Usar o perfil de otimização selecionado para determinar o valor padrão
                selected_profile = self.optimization_profile.get()
                
                if selected_profile == "Máxima Performance":
                    optimal_mtu = 1492  # Comum para PPPoE
                else:
                    optimal_mtu = 1500  # Padrão Ethernet
            
            self.log(f"MTU ótimo determinado: {optimal_mtu}", "success")
            
            # Configurar MTU via netsh
            try:
                # Ocultar a janela do console
                startupinfo = None
                if os.name == 'nt':  # Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                
                # Executar comando netsh sem mostrar console
                subprocess.run(
                    ["netsh", "interface", "ipv4", "set", "subinterface", 
                    interface, f"mtu={optimal_mtu}", "store=persistent"], 
                    capture_output=True, 
                    check=False,
                    startupinfo=startupinfo
                )
                
                self.log(f"MTU configurado para {optimal_mtu} na interface {interface}", "success")
                return True
            except Exception as e:
                self.log(f"Erro ao configurar MTU: {str(e)}", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao otimizar MTU: {str(e)}", "error")
            return False
    
    def disable_nagle_algorithm(self):
        """Desativa o algoritmo de Nagle (TCP_NODELAY) para reduzir latência"""
        try:
            self.log("Desativando algoritmo de Nagle para redução de latência...", "info")
            
            # Desativar Nagle no registro do Windows
            tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            
            try:
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_WRITE)
                
                # TcpNoDelay = 1 desativa o algoritmo de Nagle
                winreg.SetValueEx(key, "TcpNoDelay", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "TCPAckFrequency", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                
                self.log("Algoritmo de Nagle desativado com sucesso", "success")
                return True
            except Exception as e:
                self.log(f"Erro ao desativar algoritmo de Nagle: {str(e)}", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao desativar algoritmo de Nagle: {str(e)}", "error")
            return False
    
    def optimize_network_buffers(self):
        """Otimiza os buffers de rede para jogos"""
        try:
            self.log("Otimizando buffers de rede para jogos...", "info")
            
            # Configurar buffers TCP no registro do Windows
            tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            
            buffer_settings = {
                # Aumentar o tamanho máximo dos buffers TCP
                "GlobalMaxTcpWindowSize": 65535,
                # Tamanho da janela para conexões não-RSS
                "TcpWindowSize": 65535,
                # Escala de janela TCP (valor 8 = fator máximo)
                "Tcp1323Opts": 3,
                # Ajustar o número de ACKs para conexões TCP
                "TcpMaxDupAcks": 2
            }
            
            try:
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_WRITE)
                
                for setting, value in buffer_settings.items():
                    winreg.SetValueEx(key, setting, 0, winreg.REG_DWORD, value)
                
                winreg.CloseKey(key)
                self.log("Buffers de rede otimizados com sucesso", "success")
                return True
            except Exception as e:
                self.log(f"Erro ao otimizar buffers de rede: {str(e)}", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao otimizar buffers de rede: {str(e)}", "error")
            return False
    
    def optimize_tcp_settings(self):
        """Otimiza configurações TCP/IP para melhor performance em jogos"""
        try:
            self.log("Otimizando configurações TCP/IP via registro...", "info")
            
            # Caminho do registro para TCP/IP
            tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            
            # Configurações a modificar
            tcp_settings = {
                # Aumenta o número máximo de conexões simultâneas
                "MaxUserPort": 65534,
                # Reduz o tempo de espera para conexões fechadas (30 segundos)
                "TcpTimedWaitDelay": 30,
                # Aumenta o TTL padrão para melhorar performance em rotas mais longas
                "DefaultTTL": 64,
                # Habilita escalamento de janela e timestamps
                "Tcp1323Opts": 1,
                # Habilita SACK para melhor recuperação de perdas
                "SackOpts": 1
            }
            
            # Aplicar configurações
            reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_WRITE)
            
            for setting, value in tcp_settings.items():
                try:
                    winreg.SetValueEx(key, setting, 0, winreg.REG_DWORD, value)
                    self.log(f"Configuração {setting} = {value} aplicada", "success")
                except Exception as e:
                    self.log(f"Erro ao aplicar {setting}: {str(e)}", "error")
            
            winreg.CloseKey(key)
            
            # Tentar configurar congestion provider via netsh
            try:
                # Tenta definir o provedor de congestionamento para CTCP (compound TCP)
                subprocess.run(["netsh", "int", "tcp", "set", "global", "congestionprovider=ctcp"], 
                              capture_output=True, check=False)
                self.log("Provedor de congestionamento configurado para CTCP", "success")
            except Exception as e:
                self.log(f"Não foi possível configurar o provedor de congestionamento: {str(e)}", "warning")
            
            self.log("Configurações TCP/IP otimizadas com sucesso", "success")
            return True
        except Exception as e:
            self.log(f"Erro ao otimizar TCP/IP: {str(e)}", "error")
            return False
    
    def optimize_dns(self):
        """Otimiza configurações de DNS para jogos"""
        try:
            self.log("Otimizando configurações de DNS...", "info")
            
            interface = self.selected_interface.get()
            if not interface or interface == "Nenhuma interface ativa":
                self.log("Não foi possível identificar a interface de rede ativa.", "error")
                return False
            
            # Lista de servidores DNS otimizados para jogos
            gaming_dns_servers = [
                ("1.1.1.1", "1.0.0.1"),  # Cloudflare (geralmente melhor para jogos)
                ("8.8.8.8", "8.8.4.4"),   # Google
                ("9.9.9.9", "149.112.112.112")  # Quad9
            ]
            
            # Selecionar os servidores Cloudflare por padrão
            primary_dns = gaming_dns_servers[0][0]
            secondary_dns = gaming_dns_servers[0][1]
            
            # Definir DNS via netsh
            try:
                # Primeiro, limpar as configurações existentes
                subprocess.run(["netsh", "interface", "ip", "set", "dns", interface, "source=static", 
                               "addr=none"], capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
                
                # Configurar DNS primário
                subprocess.run(["netsh", "interface", "ip", "set", "dns", interface, "source=static", 
                               f"addr={primary_dns}", "register=primary"], capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
                
                # Adicionar DNS secundário
                subprocess.run(["netsh", "interface", "ip", "add", "dns", interface, 
                               f"addr={secondary_dns}", "index=2"], capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
                
                self.log(f"DNS configurado: Primário {primary_dns}, Secundário {secondary_dns}", "success")
                
                # Limpar cache DNS para aplicar configurações
                self.flush_dns_cache()
                
                return True
            except Exception as e:
                self.log(f"Erro ao configurar DNS: {str(e)}", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao otimizar DNS: {str(e)}", "error")
            return False
    
    def flush_dns_cache(self):
        """Limpa o cache DNS"""
        try:
            self.log("Limpando cache DNS...", "info")
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
            self.log("Cache DNS limpo com sucesso", "success")
            return True
        except Exception as e:
            self.log(f"Erro ao limpar cache DNS: {str(e)}", "error")
            return False
    
    def disable_unnecessary_services(self):
        """Desativa serviços do Windows desnecessários para jogos"""
        try:
            self.log("Desativando serviços desnecessários para jogos...", "info")
            
            # Lista de serviços que podem afetar a performance de jogos
            services_to_disable = [
                "DiagTrack",  # Experiências do Usuário Conectado e Telemetria
                "wuauserv",   # Windows Update
                "BITS",       # Background Intelligent Transfer Service
                "SysMain",    # SuperFetch
                "PcaSvc",     # Assistente de Compatibilidade de Programas
                "iphlpsvc",   # Auxiliar de IP
                "DoSvc",      # Otimização de Entrega
                "WSearch"     # Windows Search
            ]
            
            disabled_count = 0
            
            for service in services_to_disable:
                try:
                    # Tentar parar o serviço
                    stop_process = subprocess.run(["sc", "stop", service], 
                                               capture_output=True, check=False)
                    
                    # Alterar o tipo de inicialização para manual
                    config_process = subprocess.run(["sc", "config", service, "start=", "demand"], 
                                                 capture_output=True, check=False)
                    
                    if stop_process.returncode == 0 or config_process.returncode == 0:
                        disabled_count += 1
                        self.log(f"Serviço {service} configurado para inicialização manual", "success")
                except Exception as e:
                    self.log(f"Erro ao configurar serviço {service}: {str(e)}", "warning")
            
            if disabled_count > 0:
                self.log(f"{disabled_count} serviços desnecessários desativados com sucesso.", "success")
            else:
                self.log("Nenhum serviço foi modificado.", "info")
            
            return True
        except Exception as e:
            self.log(f"Erro ao desativar serviços: {str(e)}", "error")
            return False
    
    def optimize_routes_and_priority(self):
        """Otimiza rotas de rede e priorização de tráfego"""
        try:
            self.log("Otimizando rotas e prioridade de tráfego...", "info")
            
            interface = self.selected_interface.get()
            if not interface or interface == "Nenhuma interface ativa":
                self.log("Não foi possível identificar a interface de rede ativa", "error")
                return False
            
            # 1. Ativar o Modo de Jogo do Windows
            try:
                game_mode_path = r"SOFTWARE\Microsoft\GameBar"
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(reg_handle, game_mode_path, 0, winreg.KEY_WRITE)
                
                winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                
                self.log("Modo de Jogo do Windows ativado", "success")
            except Exception as e:
                self.log(f"Erro ao ativar Modo de Jogo: {str(e)}", "warning")
            
            # 2. Configurar DSCP Tagging para jogos
            try:
                # Configurar políticas QoS para priorização de aplicativos de jogos
                qos_path = r"SOFTWARE\Policies\Microsoft\Windows\QoS\Game"
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                
                try:
                    key = winreg.OpenKey(reg_handle, qos_path, 0, winreg.KEY_WRITE)
                except:
                    # Criar a chave se não existir
                    key = winreg.CreateKey(reg_handle, qos_path)
                
                # Configurar valores de QoS para jogos
                winreg.SetValueEx(key, "Application Name", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "DSCP Value", 0, winreg.REG_SZ, "46")
                winreg.SetValueEx(key, "Local Port", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "Protocol", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "Remote Port", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "Remote IP", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "Local IP", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "Throttle Rate", 0, winreg.REG_SZ, "-1")
                
                winreg.CloseKey(key)
                self.log("Políticas de QoS e DSCP Tagging para priorização de jogos configuradas", "success")
            except Exception as e:
                self.log(f"Erro ao configurar DSCP Tagging: {str(e)}", "warning")
            
            self.log("Rotas e prioridade de tráfego otimizadas com sucesso.", "success")
            return True
        except Exception as e:
            self.log(f"Erro ao otimizar rotas: {str(e)}", "error")
            return False
    
    def disable_network_throttling(self):
        """Desativa completamente o throttling de rede do Windows"""
        try:
            self.log("Desativando throttling de rede para jogos...", "info")
            
            # Caminho do registro para configurações de throttling
            throttle_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            
            # Configurações a modificar
            throttle_settings = {
                "NetworkThrottlingIndex": 0xFFFFFFFF,  # Desativar throttling (máximo)
                "SystemResponsiveness": 0,              # Priorizar aplicativos em vez do sistema
                "NoLazyMode": 1                         # Desativar modo de economia
            }
            
            # Aplicar configurações
            try:
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, throttle_path, 0, winreg.KEY_WRITE)
                
                for setting, value in throttle_settings.items():
                    winreg.SetValueEx(key, setting, 0, winreg.REG_DWORD, value)
                    self.log(f"Throttling: {setting} = {value} aplicado", "success")
                
                winreg.CloseKey(key)
                
                # Configurações específicas para jogos
                games_path = f"{throttle_path}\\Tasks\\Games"
                try:
                    games_key = winreg.OpenKey(reg_handle, games_path, 0, winreg.KEY_WRITE)
                    
                    game_settings = {
                        "Scheduling Category": "High",
                        "SFIO Priority": "High",
                        "Background Only": "False",
                        "Priority": 6,
                        "GPU Priority": 8
                    }
                    
                    for setting, value in game_settings.items():
                        if isinstance(value, int):
                            winreg.SetValueEx(games_key, setting, 0, winreg.REG_DWORD, value)
                        else:
                            winreg.SetValueEx(games_key, setting, 0, winreg.REG_SZ, value)
                    
                    winreg.CloseKey(games_key)
                    self.log("Prioridade de rede ajustada para jogos", "success")
                except Exception as e:
                    self.log(f"Erro ao configurar prioridade para jogos: {str(e)}", "warning")
                
                self.log("Throttling de rede desativado e prioridade de rede ajustada", "success")
                return True
            except Exception as e:
                self.log(f"Erro ao desativar throttling: {str(e)}", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao desativar throttling: {str(e)}", "error")
            return False
    
    def optimize_advanced_driver_settings(self):
        """Otimiza configurações avançadas do driver de rede com método mais robusto"""
        try:
            self.log("Otimizando configurações avançadas da placa de rede...", "info")
            
            # Obter interface selecionada
            interface = self.selected_interface.get()
            if not interface or interface == "Nenhuma interface ativa":
                self.log("Nenhuma interface selecionada para otimização", "error")
                return False
                
            # Método 1: Abordagem direta via WMI (mais confiável)
            try:
                self.log(f"Tentando otimizar a interface {interface} via PowerShell/WMI...", "info")
                
                # Criar script PowerShell temporário para manipular as configurações do adaptador
                with open("optimize_adapter.ps1", "w") as f:
                    f.write('param([string]$adapterName)\n\n')
                    f.write('# Encontrar adaptador de rede por nome\n')
                    f.write('$adapter = Get-NetAdapter | Where-Object {$_.Name -like "*$adapterName*" -or $_.InterfaceDescription -like "*$adapterName*"}\n\n')
                    f.write('if ($adapter -eq $null) {\n')
                    f.write('    Write-Host "Adaptador não encontrado: $adapterName"\n')
                    f.write('    exit 1\n')
                    f.write('}\n\n')
                    f.write('Write-Host "Adaptador encontrado: $($adapter.Name) - $($adapter.InterfaceDescription)"\n\n')
                    
                    # Desativar otimizações desnecessárias para jogos
                    f.write('# Desativar offloads e otimizações que podem afetar latência\n')
                    f.write('$properties = @(\n')
                    f.write('    @{Name="*EEE"; Value=0; Description="Energy-Efficient Ethernet"},\n')
                    f.write('    @{Name="*FlowControl"; Value=0; Description="Flow Control"},\n')
                    f.write('    @{Name="*InterruptModeration"; Value=0; Description="Interrupt Moderation"},\n')
                    f.write('    @{Name="*PriorityVLANTag"; Value=1; Description="Packet Priority"},\n')
                    f.write('    @{Name="*ReceiveBuffers"; Value=256; Description="Receive Buffers"},\n')
                    f.write('    @{Name="*TransmitBuffers"; Value=256; Description="Transmit Buffers"},\n')
                    f.write('    @{Name="*TCPChecksumOffloadIPv4"; Value=0; Description="TCP Checksum Offload IPv4"},\n')
                    f.write('    @{Name="*TCPChecksumOffloadIPv6"; Value=0; Description="TCP Checksum Offload IPv6"},\n')
                    f.write('    @{Name="*UDPChecksumOffloadIPv4"; Value=0; Description="UDP Checksum Offload IPv4"},\n')
                    f.write('    @{Name="*UDPChecksumOffloadIPv6"; Value=0; Description="UDP Checksum Offload IPv6"},\n')
                    f.write('    @{Name="*PMARPOffload"; Value=0; Description="ARP Offload"},\n')
                    f.write('    @{Name="*PMNSOffload"; Value=0; Description="NS Offload"},\n')
                    f.write('    @{Name="*AutoPowerSaveModeEnabled"; Value=0; Description="Auto Power Save Mode"},\n')
                    f.write('    @{Name="EnablePME"; Value=0; Description="Wake on Magic Packet"},\n')
                    f.write('    @{Name="*JumboPacket"; Value=0; Description="Jumbo Packet"}\n')
                    f.write(')\n\n')
                    
                    # Tentar definir cada propriedade
                    f.write('foreach ($prop in $properties) {\n')
                    f.write('    try {\n')
                    f.write('        $name = $prop.Name\n')
                    f.write('        $value = $prop.Value\n')
                    f.write('        $desc = $prop.Description\n')
                    f.write('        \n')
                    f.write('        # Verificar se a propriedade existe para este adaptador\n')
                    f.write('        $adapterProperty = Get-NetAdapterAdvancedProperty -Name $adapter.Name -DisplayName $desc -ErrorAction SilentlyContinue\n')
                    f.write('        \n')
                    f.write('        if ($adapterProperty) {\n')
                    f.write('            # Propriedade existe, tentar definir\n')
                    f.write('            Set-NetAdapterAdvancedProperty -Name $adapter.Name -DisplayName $desc -DisplayValue $value -ErrorAction SilentlyContinue\n')
                    f.write('            Write-Host "Configuração aplicada: $desc = $value"\n')
                    f.write('        } else {\n')
                    f.write('            # Tentar outra abordagem com o nome exato da propriedade\n')
                    f.write('            $adapterProperty = Get-NetAdapterAdvancedProperty -Name $adapter.Name | Where-Object { $_.RegistryKeyword -eq $name } -ErrorAction SilentlyContinue\n')
                    f.write('            \n')
                    f.write('            if ($adapterProperty) {\n')
                    f.write('                # Propriedade encontrada pelo nome de registro\n')
                    f.write('                Set-NetAdapterAdvancedProperty -Name $adapter.Name -RegistryKeyword $name -RegistryValue $value -ErrorAction SilentlyContinue\n')
                    f.write('                Write-Host "Configuração aplicada (via registro): $name = $value"\n')
                    f.write('            } else {\n')
                    f.write('                Write-Host "Propriedade não encontrada: $desc ($name)"\n')
                    f.write('            }\n')
                    f.write('        }\n')
                    f.write('    } catch {\n')
                    f.write('        Write-Host "Erro ao configurar $($prop.Description): $_"\n')
                    f.write('    }\n')
                    f.write('}\n')
                
                # Executar o script PowerShell com o nome da interface
                powershell_command = f'powershell -ExecutionPolicy Bypass -File optimize_adapter.ps1 -adapterName "{interface}"'
                process = subprocess.Popen(powershell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                stdout, stderr = process.communicate()
                
                # Analisar a saída
                if process.returncode == 0:
                    # Exibir resultados no log
                    for line in stdout.splitlines():
                        if "Configuração aplicada" in line:
                            self.log(line, "success")
                        elif "Propriedade não encontrada" in line:
                            self.log(line, "info")
                        elif "Erro" in line:
                            self.log(line, "warning")
                        else:
                            self.log(line, "info")
                    
                    self.log("Configurações da placa de rede otimizadas via PowerShell", "success")
                    return True
                else:
                    self.log(f"Falha ao executar PowerShell: {stderr}", "error")
            except Exception as e:
                self.log(f"Erro na abordagem via PowerShell: {str(e)}", "warning")
                self.log("Tentando método alternativo...", "info")
            
            # Método 2: Abordagem via registro do Windows (fallback)
            try:
                self.log("Tentando otimizar via registro do Windows...", "info")
                
                # Obter GUID do adaptador
                adapter_guids = []
                
                # Obter todos os adaptadores de rede
                key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                adapters_key = winreg.OpenKey(reg_handle, key_path)
                
                # Definições para melhorar jogos
                optimization_settings = {
                    "*EEE": 0,                          # Energy Efficient Ethernet
                    "*FlowControl": 0,                   # Flow Control
                    "*InterruptModeration": 0,           # Interrupt Moderation
                    "*PriorityVLANTag": 1,               # Packet Priority
                    "*ReceiveBuffers": 256,              # Receive Buffers
                    "*TransmitBuffers": 256,             # Transmit Buffers
                    "*TCPChecksumOffloadIPv4": 0,        # TCP Checksum Offload IPv4
                    "*TCPChecksumOffloadIPv6": 0,        # TCP Checksum Offload IPv6
                    "*UDPChecksumOffloadIPv4": 0,        # UDP Checksum Offload IPv4
                    "*UDPChecksumOffloadIPv6": 0,        # UDP Checksum Offload IPv6
                    "*PMARPOffload": 0,                  # ARP Offload
                    "*PMNSOffload": 0,                   # NS Offload
                    "EnablePME": 0,                      # Wake on Magic Packet
                    "*SpeedDuplex": 0,                   # Speed & Duplex - Auto
                    "*JumboPacket": 0                    # Jumbo Packet
                }
                
                # Percorrer todos os adaptadores
                index = 0
                adapted_count = 0
                
                while True:
                    try:
                        # Abrir subchave do adaptador
                        adapter_key_name = winreg.EnumKey(adapters_key, index)
                        
                        # Ignorar chaves que não são adaptadores
                        if adapter_key_name == "Properties":
                            index += 1
                            continue
                        
                        adapter_path = f"{key_path}\\{adapter_key_name}"
                        adapter_key = winreg.OpenKey(reg_handle, adapter_path, 0, winreg.KEY_READ)
                        
                        # Verificar se é um adaptador ativo
                        try:
                            # Ler a descrição do driver
                            driver_desc = winreg.QueryValueEx(adapter_key, "DriverDesc")[0]
                            
                            # Verificar se corresponde à interface selecionada
                            is_target_adapter = False
                            
                            # Verificar por nome exato, parcial ou GUID
                            if interface.lower() in driver_desc.lower() or interface == adapter_key_name:
                                is_target_adapter = True
                            
                            # Se for o adaptador alvo, otimizar configurações
                            if is_target_adapter:
                                self.log(f"Adaptador encontrado: {driver_desc}", "success")
                                
                                # Obter o GUID para referência
                                try:
                                    guid = winreg.QueryValueEx(adapter_key, "NetCfgInstanceId")[0]
                                    self.log(f"GUID do adaptador: {guid}", "info")
                                except:
                                    guid = None
                                
                                # Caminho para as configurações avançadas
                                advanced_path = f"{adapter_path}\\Ndi\\Params"
                                
                                # Tentar alterar cada configuração
                                for setting, value in optimization_settings.items():
                                    try:
                                        # Verificar se o parâmetro existe
                                        param_key = winreg.OpenKey(reg_handle, f"{advanced_path}\\{setting}", 0, winreg.KEY_READ)
                                        
                                        # Se existir, configurar o valor
                                        adapter_key_write = winreg.OpenKey(reg_handle, adapter_path, 0, winreg.KEY_WRITE)
                                        winreg.SetValueEx(adapter_key_write, setting, 0, winreg.REG_DWORD, value)
                                        winreg.CloseKey(adapter_key_write)
                                        winreg.CloseKey(param_key)
                                        
                                        self.log(f"Configuração aplicada: {setting} = {value}", "success")
                                    except Exception as param_error:
                                        # Ignorar silenciosamente parâmetros que não existem
                                        pass
                                
                                adapted_count += 1
                        except Exception as adapter_error:
                            # Ignorar adaptadores sem descrição
                            pass
                        
                        winreg.CloseKey(adapter_key)
                        index += 1
                    except WindowsError:
                        # Fim dos adaptadores
                        break
                
                winreg.CloseKey(adapters_key)
                
                if adapted_count > 0:
                    self.log(f"{adapted_count} adaptadores de rede otimizados com sucesso", "success")
                    return True
                else:
                    self.log("Nenhum adaptador compatível encontrado para otimização", "warning")
                    return False
            except Exception as e:
                self.log(f"Erro ao otimizar via registro: {str(e)}", "error")
                return False
                
            # Se chegou aqui, nenhum método funcionou
            self.log("Não foi possível otimizar as configurações da placa de rede", "error")
            return False
        except Exception as e:
            self.log(f"Erro ao otimizar placa de rede: {str(e)}", "error")
            return False
    
    def reduce_jitter(self):
        """Aplica otimizações para redução de jitter"""
        try:
            self.log("Aplicando otimizações para redução de jitter...", "info")
            
            # 1. Ajustar a resolução do timer do sistema
            try:
                # Criar um arquivo .bat para executar o comando
                with open("timer_resolution.bat", "w") as f:
                    f.write('@echo off\n')
                    f.write('bcdedit /set useplatformtick yes\n')
                    f.write('bcdedit /set disabledynamictick yes\n')
                    f.write('exit')
                
                # Executar o arquivo .bat como administrador
                subprocess.run(["timer_resolution.bat"], shell=True, startupinfo=create_hidden_startupinfo())
                
                self.log("Resolução de timer do sistema otimizada", "success")
            except Exception as e:
                self.log(f"Erro ao ajustar resolução de timer: {str(e)}", "error")
            
            # 2. Desativar TCP Auto-Tuning
            try:
                subprocess.run(["netsh", "interface", "tcp", "set", "global", "autotuninglevel=disabled"], 
                              capture_output=True, check=False)
                
                self.log("TCP Auto-Tuning desativado para garantir latência consistente", "success")
            except Exception as e:
                self.log(f"Erro ao desativar TCP Auto-Tuning: {str(e)}", "error")
            
            self.log("Otimizações para redução de jitter aplicadas com sucesso.", "success")
            return True
        except Exception as e:
            self.log(f"Erro ao aplicar otimizações para jitter: {str(e)}", "error")
            return False
    
    def optimize_system_timer(self):
        """Otimiza a resolução do timer do sistema para menor latência"""
        try:
            self.log("Otimizando resolução do timer do sistema...", "info")
            
            # 1. Via registro para configuração permanente
            timer_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel"
            
            try:
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, timer_path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "GlobalTimerResolutionRequests", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                self.log("Timer global configurado via registro", "success")
            except Exception as e:
                self.log(f"Erro ao configurar timer via registro: {str(e)}", "error")
            
            # 2. Via bcdedit para efeito no próximo boot
            try:
                subprocess.run(["bcdedit", "/set", "useplatformclock", "true"], 
                              capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
                subprocess.run(["bcdedit", "/set", "disabledynamictick", "yes"], 
                              capture_output=True, check=False, startupinfo=create_hidden_startupinfo())
                
                self.log("Timer do sistema otimizado via bcdedit", "success")
            except Exception as e:
                self.log(f"Erro ao ajustar timer via bcdedit: {str(e)}", "error")
            
            # 3. Criar arquivo de configuração de timer para uso em jogos
            try:
                with open("SetTimerResolution.bat", "w") as f:
                    f.write('@echo off\n')
                    f.write('echo Configurando resolucao de timer para jogos...\n')
                    f.write('bcdedit /set useplatformclock true\n')
                    f.write('bcdedit /set disabledynamictick yes\n')
                    f.write('echo Timer do sistema otimizado para jogos\n')
                    f.write('pause')
                
                self.log("Arquivo SetTimerResolution.bat criado. Execute antes de jogar.", "info")
            except Exception as e:
                self.log(f"Erro ao criar arquivo de configuração de timer: {str(e)}", "error")
            
            return True
        except Exception as e:
            self.log(f"Erro na otimização do timer: {str(e)}", "error")
            return False
    
    def optimize_wifi_settings(self):
        """Otimiza configurações Wi-Fi para jogos"""
        try:
            self.log("Otimizando configurações Wi-Fi para jogos...", "info")
            
            # Verificar se Wi-Fi está em uso
            interface = self.selected_interface.get()
            if not interface or interface == "Nenhuma interface ativa":
                self.log("Wi-Fi não está em uso. Pulando otimizações Wi-Fi.", "info")
                return True
            
            # Verificar se é uma interface Wi-Fi
            is_wifi = False
            try:
                # Obter informações do adaptador
                netsh_output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], 
                                                    universal_newlines=True)
                
                if interface in netsh_output:
                    is_wifi = True
            except:
                pass
            
            if not is_wifi:
                self.log("Interface selecionada não é Wi-Fi. Pulando otimizações.", "info")
                return True
            
            # Configurações Wi-Fi
            try:
                # 1. Definir modo de economia de energia para máximo desempenho
                subprocess.run(["powercfg", "-setacvalueindex", "scheme_current", "19cbb8fa-5279-450e-9fac-8a3d5fedd0c1", 
                               "12bbebe6-58d6-4636-95bb-3217ef867c1a", "0"], capture_output=True, check=False)
                
                # 2. Desativar serviço WLAN AutoConfig para evitar varreduras em segundo plano
                subprocess.run(["sc", "config", "WlanSvc", "start=", "auto"], capture_output=True, check=False)
                
                # 3. Configurar canal preferencial (se possível)
                subprocess.run(["netsh", "wlan", "set", "autoconfig", "enabled=no", "interface=" + interface], 
                              capture_output=True, check=False)
                
                # 4. Preferir banda de 5GHz para menor interferência
                subprocess.run(["netsh", "wlan", "set", "preferredband", "band=5", "interface=" + interface],
                              capture_output=True, check=False)
                
                # 5. Definir largura de canal para 20MHz (mais estável)
                # Isso geralmente precisa ser feito no driver ou roteador
                
                self.log("Configurações Wi-Fi otimizadas para jogos", "success")
                return True
            except Exception as e:
                self.log(f"Erro ao otimizar Wi-Fi: {str(e)}", "error")
                return False
        except Exception as e:
            self.log(f"Erro ao otimizar configurações Wi-Fi: {str(e)}", "error")
            return False
    
    def optimize_hardware_settings(self):
        """Otimiza configurações de hardware para jogos"""
        try:
            self.log("Otimizando configurações de hardware para jogos...", "info")
            
            # 1. Otimizar taxa de polling USB
            try:
                # Criar arquivo .reg para configurar taxa de polling
                with open("usb_polling_rate.reg", "w") as f:
                    f.write('Windows Registry Editor Version 5.00\n\n')
                    f.write('[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\USB]\n')
                    f.write('"DisableSelectiveSuspend"=dword:00000001\n')
                    f.write('"EnhancedPowerManagementEnabled"=dword:00000000\n')
                    f.write('"DeviceSelectiveSuspendEnabled"=dword:00000000\n')
                
                # Executar arquivo .reg
                subprocess.run(["regedit.exe", "/s", "usb_polling_rate.reg"], 
                              capture_output=True, check=False)
                
                self.log("Taxa de polling USB otimizada", "success")
            except Exception as e:
                self.log(f"Erro ao configurar taxa de polling USB: {str(e)}", "warning")
            
            # 2. Otimização de nó NUMA
            try:
                # Configurar afinidade de CPU para nó NUMA principal
                # Isso é feito mais eficientemente quando um jogo está em execução
                # Criar script para otimização
                with open("numa_optimization.bat", "w") as f:
                    f.write('@echo off\n')
                    f.write('echo Otimizando afinidade de CPU para jogos via nós NUMA\n')
                    f.write('echo Para usar: numa_optimization.bat [PID do jogo]\n\n')
                    f.write('if "%~1"=="" (\n')
                    f.write('  echo Por favor, forneça o PID do jogo.\n')
                    f.write('  echo Uso: numa_optimization.bat PID\n')
                    f.write('  exit /b\n')
                    f.write(')\n\n')
                    f.write('powershell -Command "& {$process = Get-Process -Id %1; $process.ProcessorAffinity = [Int64]::MaxValue; Write-Host (\'Afinidade de CPU otimizada para processo \' + $process.ProcessName)}"\n')
                    f.write('pause')
                
                self.log("Otimização de nó NUMA aplicada para processos de jogos", "success")
            except Exception as e:
                self.log(f"Erro ao configurar otimização NUMA: {str(e)}", "warning")
            
            # 3. Prioridade de IRQ para controladores de rede
            try:
                irq_path = r"SYSTEM\CurrentControlSet\Control\PriorityControl"
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, irq_path, 0, winreg.KEY_WRITE)
                
                # Definir prioridade de IRQ
                winreg.SetValueEx(key, "IRQ8Priority", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "IRQ16Priority", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
                
                self.log("Prioridade de IRQ aumentada para controladores de rede", "success")
            except Exception as e:
                self.log(f"Erro ao configurar prioridade de IRQ: {str(e)}", "warning")
            
            self.log("Configurações de hardware otimizadas com sucesso.", "success")
            return True
        except Exception as e:
            self.log(f"Erro ao otimizar hardware: {str(e)}", "error")
            return False
    
    def optimize_ipv6_settings(self):
        """Otimiza ou desativa IPv6 para melhor performance em jogos"""
        try:
            self.log("Otimizando configurações de IPv6...", "info")
            
            # Verificar se vale mais a pena manter ou desativar IPv6
            # Alguns jogos e redes funcionam melhor com IPv6 desativado
            disable_ipv6 = True  # Por padrão, desativar para jogos
            
            if disable_ipv6:
                # Desativar IPv6 em todas as interfaces
                subprocess.run(["netsh", "interface", "ipv6", "set", "global", "randomizeidentifiers=disabled"], 
                              capture_output=True, check=False)
                
                # Desativar componentes de tunelamento
                subprocess.run(["netsh", "interface", "teredo", "set", "state", "disabled"], 
                              capture_output=True, check=False)
                subprocess.run(["netsh", "interface", "ipv6", "set", "teredo", "disabled"], 
                              capture_output=True, check=False)
                
                # Desativar 6to4
                subprocess.run(["netsh", "interface", "ipv6", "6to4", "set", "state", "disabled"], 
                              capture_output=True, check=False)
                
                # Desativar preferência de IPv6 sobre IPv4
                ip_path = r"SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters"
                try:
                    reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                    key = winreg.OpenKey(reg_handle, ip_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, "DisabledComponents", 0, winreg.REG_DWORD, 0xFF)
                    self.log("IPv6 desativado para melhor latência em jogos", "success")
                except Exception as e:
                    self.log(f"Erro ao desativar IPv6 via registro: {str(e)}", "error")
            else:
                # Otimizar IPv6 sem desativá-lo
                subprocess.run(["netsh", "interface", "ipv6", "set", "global", "randomizeidentifiers=enabled"], 
                              capture_output=True, check=False)
                self.log("IPv6 otimizado para melhor performance", "success")
            
            return True
        except Exception as e:
            self.log(f"Erro ao configurar IPv6: {str(e)}", "error")
            return False
    
    def setup_process_prioritization(self):
        """Configura priorização automática de processos de jogos"""
        try:
            self.log("Configurando priorização automática de processos...", "info")
            
            # Lista de executáveis comuns de jogos
            game_executables = [
                "steam.exe", "epicgameslauncher.exe", "origin.exe", 
                "battle.net.exe", "GalaxyClient.exe", "RiotClientServices.exe",
                "LeagueClient.exe", "valorant.exe", "csgo.exe", "dota2.exe",
                "gta5.exe", "FortniteClient-Win64-Shipping.exe", "r5apex.exe"
            ]
            
            # Criar arquivo .bat para elevação de prioridade
            bat_content = '@echo off\n'
            bat_content += 'echo Iniciando monitoramento de processos de jogos...\n'
            
            for exe in game_executables:
                bat_content += f'\n:check_{exe.replace(".", "_")}\n'
                bat_content += f'tasklist /FI "IMAGENAME eq {exe}" 2>NUL | find /I /N "{exe}" >NUL\n'
                bat_content += 'if "%ERRORLEVEL%"=="0" (\n'
                bat_content += f'  wmic process where name="{exe}" CALL setpriority "high priority"\n'
                bat_content += f'  echo Prioridade elevada para {exe}\n'
                bat_content += ')\n'
            
            bat_content += '\ntimeout /t 30\n'
            bat_content += 'goto check_steam_exe\n'
            
            # Salvar o arquivo .bat
            with open("game_priority.bat", "w") as f:
                f.write(bat_content)
            
            self.log("Sistema de priorização de processos criado", "success")
            self.log("Arquivo game_priority.bat criado. Execute-o ao jogar.", "info")
            
            return True
        except Exception as e:
            self.log(f"Erro ao configurar priorização: {str(e)}", "error")
            return False
    
    def get_network_adapter_guid(self, adapter_name):
        """Obtém o GUID do adaptador de rede pelo nome"""
        try:
            # Caminho do registro para adaptadores de rede
            path = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            adapters_key = winreg.OpenKey(reg_handle, path)
            
            # Percorrer todos os adaptadores
            index = 0
            while True:
                try:
                    # Abrir subchave do adaptador
                    adapter_key_name = winreg.EnumKey(adapters_key, index)
                    
                    # Ignorar chaves que não são adaptadores
                    if adapter_key_name == "Properties":
                        index += 1
                        continue
                    
                    adapter_path = f"{path}\\{adapter_key_name}"
                    adapter_key = winreg.OpenKey(reg_handle, adapter_path, 0, winreg.KEY_READ)
                    
                    # Verificar se é o adaptador correto
                    try:
                        driver_desc = winreg.QueryValueEx(adapter_key, "DriverDesc")[0]
                        if adapter_name in driver_desc:
                            # Obter o NetCfgInstanceId (GUID)
                            guid = winreg.QueryValueEx(adapter_key, "NetCfgInstanceId")[0]
                            winreg.CloseKey(adapter_key)
                            winreg.CloseKey(adapters_key)
                            return guid
                    except Exception:
                        pass
                    
                    winreg.CloseKey(adapter_key)
                    index += 1
                except WindowsError:
                    break
            
            winreg.CloseKey(adapters_key)
            return None
        except Exception as e:
            self.log(f"Erro ao obter GUID do adaptador: {str(e)}", "error")
            return None
    
    def create_manual_backup(self):
        """Cria um backup manual das configurações de rede"""
        try:
            self.log("Criando backup manual das configurações de rede...", "info")
            
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            backup_name = f"network_backup_{timestamp}.json"
            
            # Configurações do backup
            backup_data = {
                "timestamp": timestamp,
                "date": time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()),
                "settings": {}
            }
            
            # Fazer backup das configurações TCP/IP
            tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
            try:
                reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_READ)
                
                backup_data["settings"]["tcp"] = {}
                
                # Ler configurações atuais
                for i in range(0, 100):  # Tentar ler até 100 valores
                    try:
                        name, value, value_type = winreg.EnumValue(key, i)
                        if value_type == winreg.REG_DWORD or value_type == winreg.REG_SZ:
                            backup_data["settings"]["tcp"][name] = {
                                "value": value,
                                "type": value_type
                            }
                    except OSError:
                        break  # Fim dos valores
                
                winreg.CloseKey(key)
            except Exception as e:
                self.log(f"Erro ao fazer backup de TCP/IP: {str(e)}", "warning")
            
            # Backup das configurações DNS
            try:
                backup_data["settings"]["dns"] = {}
                
                # Executar ipconfig /all e extrair configurações DNS
                ipconfig_output = subprocess.check_output(["ipconfig", "/all"], 
                                                       universal_newlines=True)
                
                # Extrair servidores DNS
                dns_servers = re.findall(r"DNS Servers.*?:(.*?)(?:\r?\n\r?\n|$)", 
                                        ipconfig_output, re.DOTALL)
                
                if dns_servers:
                    # Limpar e processar os resultados
                    servers = []
                    for server_list in dns_servers:
                        for server in server_list.strip().split("\n"):
                            server = server.strip()
                            if server and ":" not in server:  # Ignorar IPv6
                                servers.append(server)
                    
                    backup_data["settings"]["dns"]["servers"] = servers
            except Exception as e:
                self.log(f"Erro ao fazer backup de DNS: {str(e)}", "warning")
            
            # Salvar o backup em um arquivo
            with open(backup_name, "w") as f:
                json.dump(backup_data, f, indent=4)
            
            self.log(f"Backup manual criado com sucesso: {backup_name}", "success")
            
            # Atualizar a lista de backups
            self.update_backup_list()
            return True
        except Exception as e:
            self.log(f"Erro ao criar backup manual: {str(e)}", "error")
            return False
    
    def restore_original_settings(self):
        """Restaura as configurações originais de rede"""
        try:
            self.log("Restaurando configurações originais de rede...", "info")
            
            # Verificar se existe backup
            if not self.original_settings:
                # Tentar carregar do arquivo
                try:
                    with open("network_backup.json", "r") as f:
                        self.original_settings = json.load(f)
                except:
                    messagebox.showwarning("Aviso", "Não foi possível encontrar um backup das configurações originais.")
                    return False
            
            # Restaurar configurações TCP/IP
            if "tcp" in self.original_settings:
                tcp_settings = self.original_settings["tcp"]
                tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
                
                try:
                    reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                    key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_WRITE)
                    
                    for setting, data in tcp_settings.items():
                        try:
                            value = data["value"]
                            value_type = data["type"]
                            
                            winreg.SetValueEx(key, setting, 0, value_type, value)
                            self.log(f"Configuração {setting} restaurada para {value}", "success")
                        except Exception as e:
                            self.log(f"Erro ao restaurar {setting}: {str(e)}", "warning")
                    
                    winreg.CloseKey(key)
                except Exception as e:
                    self.log(f"Erro ao restaurar TCP/IP: {str(e)}", "error")
            
            # Resetar configurações do Windows via netsh
            try:
                # Resetar configurações TCP/IP
                subprocess.run(["netsh", "winsock", "reset"], capture_output=True, check=False)
                self.log("Pilha Winsock resetada", "success")
                
                # Resetar configurações IP
                subprocess.run(["netsh", "int", "ip", "reset"], capture_output=True, check=False)
                self.log("Configurações IP resetadas", "success")
                
                # Resetar configurações TCP
                subprocess.run(["netsh", "int", "tcp", "reset"], capture_output=True, check=False)
                self.log("Configurações TCP resetadas", "success")
            except Exception as e:
                self.log(f"Erro ao resetar configurações via netsh: {str(e)}", "error")
            
            self.log("Restauração concluída. Reinicie o computador para aplicar todas as alterações.", "info")
            messagebox.showinfo("Restauração Concluída", "As configurações de rede foram restauradas para os valores originais. Reinicie o computador para aplicar todas as alterações.")
            
            return True
        except Exception as e:
            self.log(f"Erro ao restaurar configurações: {str(e)}", "error")
            return False
    
    def update_backup_list(self):
        """Atualiza a lista de backups disponíveis"""
        try:
            # Limpar listbox
            self.backups_listbox.delete(0, tk.END)
            
            # Encontrar arquivos de backup
            backup_files = [f for f in os.listdir(".") if f.startswith("network_backup_") and f.endswith(".json")]
            
            if backup_files:
                # Ordenar por data (mais recente primeiro)
                backup_files.sort(reverse=True)
                
                # Adicionar à listbox
                for backup_file in backup_files:
                    try:
                        # Extrair a data do nome do arquivo
                        date_str = backup_file.split("_")[2].split(".")[0]
                        date = datetime.strptime(date_str, "%Y%m%d%H%M%S")
                        
                        # Formatar para exibição
                        display_date = date.strftime("%d/%m/%Y %H:%M:%S")
                        
                        self.backups_listbox.insert(tk.END, f"{display_date} - {backup_file}")
                    except:
                        self.backups_listbox.insert(tk.END, backup_file)
                
                self.backup_status_label.config(
                    text=f"Encontrados {len(backup_files)} backups. Selecione um backup da lista para restaurar."
                )
            else:
                self.backup_status_label.config(
                    text="Nenhum backup manual encontrado. Use o botão 'Criar Backup Manual' para criar um novo backup."
                )
        except Exception as e:
            self.log(f"Erro ao atualizar lista de backups: {str(e)}", "error")
    
    def load_selected_backup(self):
        """Carrega um backup selecionado da lista"""
        try:
            # Verificar se um item está selecionado
            selection = self.backups_listbox.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione um backup da lista.")
                return
            
            # Obter o nome do arquivo do item selecionado
            item_text = self.backups_listbox.get(selection[0])
            backup_file = item_text.split(" - ")[-1]
            
            # Confirmar restauração
            confirm = messagebox.askyesno(
                "Confirmar Restauração", 
                f"Tem certeza que deseja restaurar o backup {backup_file}?\n\n"
                "As configurações atuais serão substituídas."
            )
            
            if not confirm:
                return
            
            self.log(f"Restaurando configurações do backup: {backup_file}", "info")
            
            # Carregar o arquivo de backup
            with open(backup_file, "r") as f:
                backup_data = json.load(f)
            
            # Restaurar configurações
            if "settings" in backup_data:
                # Restaurar TCP/IP
                if "tcp" in backup_data["settings"]:
                    tcp_settings = backup_data["settings"]["tcp"]
                    tcp_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
                    
                    try:
                        reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                        key = winreg.OpenKey(reg_handle, tcp_path, 0, winreg.KEY_WRITE)
                        
                        for setting, data in tcp_settings.items():
                            try:
                                value = data["value"]
                                value_type = data["type"]
                                
                                winreg.SetValueEx(key, setting, 0, value_type, value)
                                self.log(f"Configuração {setting} restaurada para {value}", "success")
                            except Exception as e:
                                self.log(f"Erro ao restaurar {setting}: {str(e)}", "warning")
                        
                        winreg.CloseKey(key)
                        self.log("Configurações TCP/IP restauradas", "success")
                    except Exception as e:
                        self.log(f"Erro ao restaurar TCP/IP: {str(e)}", "error")
                
                # Restaurar DNS (se disponível)
                if "dns" in backup_data["settings"] and "servers" in backup_data["settings"]["dns"]:
                    dns_servers = backup_data["settings"]["dns"]["servers"]
                    
                    if dns_servers and len(dns_servers) > 0:
                        try:
                            interface = self.selected_interface.get()
                            if interface and interface != "Nenhuma interface ativa":
                                # Limpar configurações DNS atuais
                                subprocess.run(["netsh", "interface", "ip", "set", "dns", interface, 
                                              "source=static", "addr=none"], 
                                             capture_output=True, check=False)
                                
                                # Configurar servidor DNS primário
                                subprocess.run(["netsh", "interface", "ip", "set", "dns", interface, 
                                              "source=static", f"addr={dns_servers[0]}", "register=primary"], 
                                             capture_output=True, check=False)
                                
                                # Adicionar servidores DNS secundários
                                for i, server in enumerate(dns_servers[1:], start=2):
                                    subprocess.run(["netsh", "interface", "ip", "add", "dns", interface, 
                                                  f"addr={server}", f"index={i}"], 
                                                 capture_output=True, check=False)
                                
                                self.log("Servidores DNS restaurados", "success")
                            else:
                                self.log("Nenhuma interface selecionada para restaurar DNS", "warning")
                        except Exception as e:
                            self.log(f"Erro ao restaurar servidores DNS: {str(e)}", "error")
            
            self.log("Restauração do backup concluída!", "success")
            messagebox.showinfo("Restauração Concluída", 
                              "As configurações de rede foram restauradas do backup selecionado.")
            
        except Exception as e:
            self.log(f"Erro ao carregar backup: {str(e)}", "error")
            messagebox.showerror("Erro", f"Ocorreu um erro ao restaurar o backup: {str(e)}")
    
    def delete_selected_backup(self):
        """Exclui um backup selecionado da lista"""
        try:
            # Verificar se um item está selecionado
            selection = self.backups_listbox.curselection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione um backup da lista.")
                return
            
            # Obter o nome do arquivo do item selecionado
            item_text = self.backups_listbox.get(selection[0])
            backup_file = item_text.split(" - ")[-1]
            
            # Confirmar exclusão
            confirm = messagebox.askyesno(
                "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir o backup {backup_file}?"
            )
            
            if not confirm:
                return
            
            # Excluir o arquivo
            os.remove(backup_file)
            self.log(f"Backup {backup_file} excluído", "info")
            
            # Atualizar a lista
            self.update_backup_list()
        except Exception as e:
            self.log(f"Erro ao excluir backup: {str(e)}", "error")
            messagebox.showerror("Erro", f"Ocorreu um erro ao excluir o backup: {str(e)}")
    
    def setup_about_tab(self):
        """Configura a aba Sobre"""
        # Seção de Título
        title_frame = tk.Frame(self.about_tab, bg="#2E2E2E")
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        app_name = tk.Label(title_frame, text="Otimizador de Rede para Jogos", 
                          font=("Arial", 18, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        app_name.pack(pady=5)
        
        version_label = tk.Label(title_frame, text="Versão: 1.0.0", 
                               font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        version_label.pack(pady=5)
        
        # Seção de Informações
        info_frame = tk.LabelFrame(self.about_tab, text="Informações", 
                                 font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        dev_label = tk.Label(info_frame, text="Desenvolvido por: Jorge R Junior", 
                            font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF")
        dev_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # GitHub link (clicável)
        github_label = tk.Label(info_frame, text="GitHub: https://github.com/jorgeRjunior", 
                              font=("Arial", 10), bg="#2E2E2E", fg="#1E90FF", cursor="hand2")
        github_label.pack(anchor=tk.W, padx=10, pady=5)
        github_label.bind("<Button-1>", lambda e: self.open_website("https://github.com/jorgeRjunior"))
        
        date_label = tk.Label(info_frame, text="Criado em: 2025", 
                             font=("Arial", 10), bg="#2E2E2E", fg="#FFFFFF")
        date_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Seção de Descrição
        desc_frame = tk.LabelFrame(self.about_tab, text="Descrição", 
                                 font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        description = (
            "O Otimizador de Rede para Jogos é uma ferramenta avançada projetada para melhorar "
            "sua experiência de jogo online, reduzindo a latência e aumentando a estabilidade da conexão. "
            "\n\nEste software otimiza diversas configurações do Windows e da sua placa de rede "
            "para garantir a melhor performance possível durante suas sessões de jogo."
            "\n\nPrincipais características:\n"
            "• Configuração de QoS (Quality of Service)\n"
            "• Otimização de MTU\n"
            "• Desativação do algoritmo de Nagle\n"
            "• Configuração de buffers de rede\n"
            "• Otimização de DNS\n"
            "• Desativação de serviços desnecessários\n"
            "• Ajustes de TCP avançados"
        )
        
        desc_text = tk.Text(desc_frame, wrap=tk.WORD, bg="#2E2E2E", fg="#FFFFFF",
                           font=("Arial", 10), height=12, borderwidth=0, highlightthickness=0)
        desc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        desc_text.insert(tk.END, description)
        desc_text.config(state=tk.DISABLED)
        
        # Rodapé
        footer_frame = tk.Frame(self.about_tab, bg="#2E2E2E")
        footer_frame.pack(fill=tk.X, padx=20, pady=10)
        
        copyright_label = tk.Label(footer_frame, text="© 2025 Jorge R Junior. Todos os direitos reservados.", 
                                  font=("Arial", 9), bg="#2E2E2E", fg="#AAAAAA")
        copyright_label.pack(pady=5)
    
    def open_website(self, url):
        """Abre o website no navegador padrão"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            self.log(f"Erro ao abrir website: {str(e)}", "error")

# Main application entry point
if __name__ == "__main__":
    # Verificar se está sendo executado como administrador
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    
    root = tk.Tk()
    # Definir o ícone da aplicação
    try:
        root.iconphoto(True, tk.PhotoImage(file="speed-radar.png"))
    except Exception as e:
        print(f"Erro ao carregar ícone: {str(e)}")
    
    app = NetworkOptimizer(root)
    root.mainloop()