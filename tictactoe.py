import sys
import time
import os
import socket
import json
import threading
from random import randint, choice
import tkinter as tk
from tkinter import messagebox, ttk

# Couleurs ANSI
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.score_x = 0
        self.score_o = 0
        self.difficulty = "facile"
    
    def display_board(self):
        print(f"\n{Colors.BLUE}╔═══╦═══╦═══╗")
        for i in range(0, 9, 3):
            print(f"║ {self.board[i]} ║ {self.board[i+1]} ║ {self.board[i+2]} ║")
            if i < 6:
                print("╠═══╬═══╬═══╣")
        # fix: use f-string so {Colors.ENDC} is expanded
        print(f"╚═══╩═══╩═══╝{Colors.ENDC}")

    def make_move(self, position, player):
        if self.board[position] == " ":
            self.board[position] = player
            return True
        return False

    def get_empty_spaces(self):
        return [i for i, x in enumerate(self.board) if x == " "]

    def ai_move(self):
        # Pourcentages de chance d'utiliser la stratégie intelligente:
        # Facile: 0% (toujours aléatoire)
        # Medium: 50% (moitié aléatoire, moitié intelligent)
        # Difficile: 75% (majoritairement intelligent)
        
        random_number = randint(1, 100)
        
        if self.difficulty == "facile":
            return choice(self.get_empty_spaces())
        elif self.difficulty == "medium":
            if random_number <= 50:  # 50% de chance
                return self.get_strategic_move()
            return choice(self.get_empty_spaces())
        else:  # difficile
            if random_number <= 75:  # 75% de chance
                return self.get_strategic_move()
            return choice(self.get_empty_spaces())

    def get_strategic_move(self):
        # Vérifie d'abord si l'IA peut gagner
        for pos in self.get_empty_spaces():
            self.board[pos] = "O"
            if self.check_winner("O"):
                self.board[pos] = " "
                return pos
            self.board[pos] = " "

        # Bloque le joueur s'il peut gagner
        for pos in self.get_empty_spaces():
            self.board[pos] = "X"
            if self.check_winner("X"):
                self.board[pos] = " "
                return pos
            self.board[pos] = " "

        # Sinon, choix aléatoire
        return choice(self.get_empty_spaces())

    def check_winner(self, player):
        # Lignes horizontales, verticales et diagonales
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), 
                (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(all(self.board[i] == player for i in win) for win in wins)

class NetworkManager:
    def __init__(self, host='localhost', port=5000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.timeout = 5.0  # Timeout de 5 secondes
        self.is_connected = False
        self._lock = threading.Lock()
        
    def connect(self):
        try:
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            return True
        except socket.timeout:
            messagebox.showerror("Erreur", "Connexion au serveur trop longue")
            return False
        except ConnectionRefusedError:
            messagebox.showerror("Erreur", "Serveur non disponible")
            return False
            
    def send_move(self, position):
        if not self.is_connected:
            return False
        with self._lock:
            try:
                message = {
                    "type": "move",
                    "position": position,
                    "timestamp": time.time()
                }
                self.socket.send(json.dumps(message).encode())
                return True
            except:
                self.is_connected = False
                return False

    def receive_data(self):
        return self.socket.recv(1024).decode()

class TicTacToeGUI:
    def __init__(self):
        self.game = TicTacToe()
        self.network = NetworkManager()
        self.window = tk.Tk()
        self.window.title("TicTacToeFuture")
        self.window.configure(bg='#2C3E50')  # Fond bleu foncé moderne
        
        # Configuration du style
        style = ttk.Style()
        style.configure('Game.TButton', 
                       font=('Helvetica', 24, 'bold'),
                       padding=20,
                       background='#34495E',
                       foreground='#ECF0F1')
        
        # Titre du jeu
        title_frame = tk.Frame(self.window, bg='#2C3E50')
        title_frame.grid(row=0, column=0, columnspan=3, pady=10)
        title_label = tk.Label(title_frame,
                             text="TicTacToeFuture",
                             font=('Helvetica', 20, 'bold'),
                             fg='#E74C3C',
                             bg='#2C3E50')
        title_label.pack()
        
        # Indicateur de tour
        self.turn_label = tk.Label(title_frame,
                                 text="Tour: Joueur X",
                                 font=('Helvetica', 14),
                                 fg='#ECF0F1',
                                 bg='#2C3E50')
        self.turn_label.pack(pady=5)
        
        # Grille de jeu avec bordures et effets
        game_frame = tk.Frame(self.window, bg='#34495E', padx=10, pady=10)
        game_frame.grid(row=1, column=0, columnspan=3)
        
        self.buttons = []
        # Style des cases
        for i in range(3):
            for j in range(3):
                button = tk.Button(
                    game_frame,
                    text="",
                    font=('Helvetica', 32, 'bold'),
                    width=3,
                    height=1,
                    bg='#ECF0F1',
                    activebackground='#3498DB',  # Effet hover
                    relief=tk.RAISED,
                    bd=5,  # Bordure 3D
                    command=lambda x=i, y=j: self.make_move(x*3 + y)
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                button.bind('<Enter>', lambda e, btn=button: self.on_hover(btn, True))
                button.bind('<Leave>', lambda e, btn=button: self.on_hover(btn, False))
                self.buttons.append(button)
        
        # Panel de contrôle
        control_frame = tk.Frame(self.window, bg='#2C3E50')
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Sélecteur de difficulté stylisé
        diff_label = tk.Label(control_frame,
                            text="Difficulté:",
                            font=('Helvetica', 12),
                            fg='#ECF0F1',
                            bg='#2C3E50')
        diff_label.pack(pady=5)
        
        # Boutons de difficulté avec couleurs
        difficulties = [
            ("Facile", "facile", '#2ECC71'),
            ("Medium", "medium", '#F1C40F'),
            ("Difficile", "difficile", '#E74C3C')
        ]
        
        diff_buttons_frame = tk.Frame(control_frame, bg='#2C3E50')
        diff_buttons_frame.pack()
        
        for text, value, color in difficulties:
            btn = tk.Button(
                diff_buttons_frame,
                text=text,
                command=lambda v=value: self.set_difficulty(v),
                bg=color,
                fg='white',
                font=('Helvetica', 10, 'bold'),
                width=10,
                relief=tk.RAISED
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Score
        self.score_label = tk.Label(control_frame,
                                  text="Score - Joueur: 0  IA: 0",
                                  font=('Helvetica', 12),
                                  fg='#ECF0F1',
                                  bg='#2C3E50')
        self.score_label.pack(pady=10)
        
        # Boutons de contrôle
        control_buttons_frame = tk.Frame(control_frame, bg='#2C3E50')
        control_buttons_frame.pack(pady=5)
        
        # Bouton Reset
        reset_button = tk.Button(
            control_buttons_frame,
            text="Reset (R)",
            command=self.reset_game,
            bg='#3498DB',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            width=10
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton Quitter
        quit_button = tk.Button(
            control_buttons_frame,
            text="Quitter (ESC)",
            command=self.quit_game,
            bg='#E74C3C',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            width=10
        )
        quit_button.pack(side=tk.LEFT, padx=5)

        # Mode toggle button (VS IA / 2 joueurs)
        self.mode = 'pve'  # 'pve' = player vs AI, 'pvp' = local 2 players
        self.current_player = 'X'  # used in pvp mode
        self.mode_button = tk.Button(
            control_buttons_frame,
            text="Mode: VS IA",
            command=self.toggle_mode,
            bg='#9B59B6',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            width=12
        )
        self.mode_button.pack(side=tk.LEFT, padx=5)

        # Bind keyboard shortcuts (normalized indentation)
        self.window.bind('<Escape>', lambda e: self.quit_game())
        self.window.bind('r', lambda e: self.reset_game())

        # Initialisation des variables manquantes
        self._last_move = time.time()
        self._move_delay = 0.3
        self.animate_victory = False
        self.update_score_label()

    def connect_to_server(self):
        if self.network.connect():
            messagebox.showinfo("Connexion", "Connecté au serveur!")
        else:
            messagebox.showerror("Erreur", "Impossible de se connecter au serveur")

    def set_difficulty(self, difficulty):
        self.game.difficulty = difficulty
        messagebox.showinfo("Difficulté", f"Niveau: {difficulty}")
        self.reset_game()

    def on_hover(self, button, entering):
        if entering and button['text'] == "":
            button.config(bg='#BDC3C7')
        else:
            button.config(bg='#ECF0F1')

    def toggle_mode(self):
        """Basculer entre VS IA et 2 joueurs locaux."""
        if self.mode == 'pve':
            self.mode = 'pvp'
            self.mode_button.config(text="Mode: 2 joueurs")
            self.current_player = 'X'
            self.turn_label.config(text="Tour: Joueur X")
        else:
            self.mode = 'pve'
            self.mode_button.config(text="Mode: VS IA")
            self.current_player = 'X'
            self.turn_label.config(text="Tour: Joueur X")
        self.reset_game()

    def make_move(self, position):
        # refuse input during victory animation
        if hasattr(self, 'animate_victory') and self.animate_victory:
            return

        current_time = time.time()
        if current_time - self._last_move < self._move_delay:
            return

        self._last_move = current_time

        try:
            # Determine player based on mode
            if self.mode == 'pve':
                player = 'X'  # human always X
            else:  # pvp local
                player = self.current_player

            # Only allow move on empty cell
            if not self.game.make_move(position, player):
                return

            # Update UI for the placed symbol
            color = '#E74C3C' if player == 'X' else '#2ECC71'
            self.buttons[position].configure(text=player, fg=color, state=tk.DISABLED)

            # Update turn label
            if self.mode == 'pvp':
                # switch turns for local players
                if self.game.check_winner(player):
                    # score and victory
                    if player == 'X':
                        self.game.score_x += 1
                    else:
                        self.game.score_o += 1
                    self.update_score_label()
                    self.animate_victory_line(player)
                    return
                # check draw
                if not self.game.get_empty_spaces():
                    messagebox.showinfo("Match nul", "Match nul!")
                    self.reset_game()
                    return
                # switch current player for next click
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.turn_label.config(text=f"Tour: Joueur {self.current_player}")
                # enable only empty spots
                self.enable_board()
            else:
                # PV E mode: after player X move, check win, then AI move
                # disable board while AI thinks
                self.disable_board()

                if self.game.check_winner('X'):
                    self.game.score_x += 1
                    self.update_score_label()
                    self.animate_victory_line('X')
                    return

                # start AI in background
                threading.Thread(target=self._handle_ai_move, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def animate_symbol(self, button, symbol):
        # Animation d'apparition du symbole
        for size in range(10, 32, 2):
            button.config(font=('Helvetica', size, 'bold'))
            button.config(text=symbol)
            self.window.update()
            time.sleep(0.01)

    def animate_victory_line(self, winner):
        self.animate_victory = True
        win_color = '#E74C3C' if winner == "X" else '#2ECC71'
        
        # Faire clignoter les cases gagnantes
        winning_positions = self.get_winning_line()
        for _ in range(5):
            for pos in winning_positions:
                self.buttons[pos].config(bg=win_color)
            self.window.update()
            time.sleep(0.2)
            for pos in winning_positions:
                self.buttons[pos].config(bg='#ECF0F1')
            self.window.update()
            time.sleep(0.2)
        
        messagebox.showinfo("Fin", f"{'Vous avez' if winner == 'X' else 'L\'IA a'} gagné!")
        self.animate_victory = False
        self.reset_game()

    def get_winning_line(self):
        # Retourne les positions de la ligne gagnante
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), 
                (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        board = self.game.board
        for win in wins:
            if board[win[0]] != " " and all(board[win[0]] == board[i] for i in win):
                return win
        return []

    def _handle_ai_move(self):
        # small think delay to improve UX
        time.sleep(0.25)
        # compute AI move (no UI here)
        if not self.game.get_empty_spaces():
            self.window.after(0, self.enable_board)
            return
        ai_pos = self.game.ai_move()
        # schedule UI update on main thread
        self.window.after(0, self._update_ai_move, ai_pos)

    def _update_ai_move(self, ai_pos):
        try:
            # if AI couldn't find a pos (safety)
            if ai_pos is None:
                self.enable_board()
                return

            self.game.make_move(ai_pos, "O")
            self.buttons[ai_pos].config(text="O", fg='#2ECC71', state=tk.DISABLED)
            self.turn_label.config(text="Tour: Joueur X")

            if self.game.check_winner("O"):
                self.game.score_o += 1
                self.update_score_label()
                self.animate_victory_line("O")
                return

            # enable board so player can move
            self.enable_board()

            # if board full => draw
            if not self.game.get_empty_spaces():
                messagebox.showinfo("Match nul", "Match nul!")
                self.reset_game()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur IA: {str(e)}")
            self.enable_board()

    def reset_game(self):
        # Animation of reset simplified to avoid blocking
        for i, btn in enumerate(self.buttons):
            btn.config(bg='#ECF0F1', text="", state=tk.NORMAL, fg='black')
        self.game.board = [" " for _ in range(9)]
        self.turn_label.config(text="Tour: Joueur X")
        self.animate_victory = False
        self.current_player = 'X'
        self.enable_board()
        self.update_score_label()

    def update_score_label(self):
        try:
            self.score_label.config(text=f"Score - Joueur: {self.game.score_x}  IA: {self.game.score_o}")
        except Exception:
            # score label may not exist in some flows; ignore
            pass

    # Disable / enable board to prevent clicks while AI is thinking
    def disable_board(self):
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)

    def enable_board(self):
        for i, btn in enumerate(self.buttons):
            # only enable empty spots
            if self.game.board[i] == " ":
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED)

    def quit_game(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter le jeu?"):
            self.window.quit()
            sys.exit(0)

    def run(self):
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("Erreur Critique", f"Erreur: {str(e)}")
            sys.exit(1)

# Visual Studio Debug Configuration
if __debug__:
    # Enable VS Debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

def display_title_animation():
    title = "TICTACTOEFUTURE"
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        for i in range(len(title)):
            print(f"\r{Colors.GREEN}{title[:i+1]}{Colors.ENDC}", end="", flush=True)
            time.sleep(0.05)  # Réduit le délai d'animation
        print("\n")
    except:
        print(title)  # Fallback si l'animation échoue

def select_difficulty():
    print(f"\n{Colors.BLUE}╔════════════════───────╗")
    print("║ Choisir la difficulté ║")
    print("╠═══════════════════════╣")
    print("║ 1. Facile             ║")
    print("║ 2. Medium             ║")  # Changed from "Moyen"
    print("║ 3. Difficile          ║")
    # fix: f-string here too
    print(f"╚═══════════════════════╝{Colors.ENDC}")
    
    while True:
        choice = input(f"{Colors.GREEN}Entrez votre choix > {Colors.ENDC}")
        if choice == "1":
            return "facile"
        elif choice == "2":
            return "medium"    # Changed from "moyen"
        elif choice == "3":
            return "difficile"
        print(f"{Colors.RED}❌ Choix invalide{Colors.ENDC}")

def play_against_ai(game):
    game.difficulty = select_difficulty()
    print(f"\n{Colors.GREEN}Difficulté: {game.difficulty}{Colors.ENDC}")
    
    while True:
        game.display_board()
        # Tour du joueur
        while True:
            try:
                pos = int(input(f"{Colors.BLUE}Entrez une position (1-9): {Colors.ENDC}")) - 1
                if 0 <= pos <= 8 and game.make_move(pos, "X"):
                    break
                print(f"{Colors.RED}Position invalide!{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Entrez un nombre valide!{Colors.ENDC}")
        
        if game.check_winner("X"):
            game.display_board()
            print(f"{Colors.GREEN}🎉 Vous avez gagné!{Colors.ENDC}")
            break
        
        if not game.get_empty_spaces():
            game.display_board()
            print(f"{Colors.BLUE}Match nul!{Colors.ENDC}")
            break
            
        # Tour de l'IA
        ai_pos = game.ai_move()
        game.make_move(ai_pos, "O")
        
        if game.check_winner("O"):
            game.display_board()
            print(f"{Colors.RED}L'IA a gagné!{Colors.ENDC}")
            break

def display_menu():
    # open GUI by default for visual game window
    try:
        gui = TicTacToeGUI()
        gui.run()
    except Exception as e:
        # fallback to console if GUI fails
        print(f"Unable to start GUI: {e}")
        display_title_animation()
        print(f"{Colors.RED}     VK Sega Genesis Game Systems")
        print(f"     © 1988 SEGA{Colors.ENDC}\n")

        while True:
            print(f"{Colors.BLUE}╔════════════════════╗")
            print("║      MENU        ║")
            print("╠════════════════════╣")
            print("║ 1. VS BOT         ║")
            print("║ 2. VS PLAYER      ║")
            print("║ 3. Options        ║")
            print("║ 4. Exit           ║")
            # fix: make this an f-string
            print(f"╚════════════════════╝{Colors.ENDC}\n")

            choice = input(f"{Colors.GREEN}Entrez votre choix > {Colors.ENDC}")

            if choice == "4":
                print("\n*beep* *boop* Au revoir!")
                time.sleep(1)
                sys.exit(0)
            elif choice == "3":
                print(f"{Colors.BLUE}⚙️  Menu options... à venir{Colors.ENDC}")
            elif choice == "1":
                game = TicTacToe()
                play_against_ai(game)
            elif choice == "2":
                game = TicTacToe()
                print(f"{Colors.RED}🎮 Mode 2 joueurs pas encore implémenté{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Choix invalide{Colors.ENDC}")

if __name__ == "__main__":
    # launch the visual game window by default
    try:
        display_menu()
    except Exception as e:
        print(f"Erreur lors du lancement du jeu: {e}")
        sys.exit(1)
