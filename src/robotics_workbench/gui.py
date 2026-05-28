import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Any, List, Tuple
from robotics_workbench.environment import GridEnvironment
from robotics_workbench.agent import BaseAgent

class GUIRunner:
    """
    A premium Tkinter-based GUI simulation runner for the Robotics Workbench.
    Visualizes the 2D grid, robot path trace, and real-time dashboard metrics.
    """
    def __init__(self, env: GridEnvironment, agent: BaseAgent, max_steps: int = 50, initial_delay: float = 0.2):
        self.env = env
        self.agent = agent
        self.max_steps = max_steps
        
        # State variables
        self.is_running = False
        self.step_count = 0
        self.total_reward = 0.0
        self.last_action = "N/A"
        self.last_reward = 0.0
        self.delay_ms = int(initial_delay * 1000)
        self.path_history: List[Tuple[int, int]] = []
        self.observation = self.env.reset()
        
        # Color Palette (Dark Theme / Slate & Sky Blue)
        self.colors = {
            "bg": "#0f172a",          # Slate 900
            "sidebar": "#1e293b",     # Slate 800
            "grid_bg": "#1e293b",     # Slate 800
            "grid_lines": "#334155",  # Slate 700
            "text": "#f8fafc",        # Slate 50
            "text_muted": "#94a3b8",  # Slate 400
            "robot": "#38bdf8",       # Sky 400 (Cyan)
            "target": "#f43f5e",      # Rose 500 (Red/Pink)
            "path": "#0ea5e9",        # Sky 500
            "success": "#10b981",     # Emerald 500 (Green)
            "danger": "#ef4444",      # Red 500
            "button_bg": "#475569",   # Slate 600
            "button_active": "#64748b" # Slate 500
        }
        
        self._setup_window()
        self._reset_simulation_state()

    def _setup_window(self) -> None:
        """Configures the Tkinter root window and widget layouts."""
        self.root = tk.Tk()
        self.root.title("Robotics Simulation Workbench")
        self.root.geometry("900x650")
        self.root.configure(bg=self.colors["bg"])
        
        # Configure grid expansion
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=300)
        self.root.rowconfigure(0, weight=1)
        
        # --- Left Area: Canvas Grid ---
        self.canvas_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=20, pady=20)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg=self.colors["grid_bg"], 
            highlightthickness=2, 
            highlightbackground=self.colors["grid_lines"]
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Bind resize event to automatically scale the grid dynamically
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # --- Right Area: Sidebar Control Dashboard ---
        self.sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], padx=25, pady=25)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        
        # Header title
        title_label = tk.Label(
            self.sidebar, 
            text="ROBOTICS WORKBENCH", 
            font=("Segoe UI", 16, "bold"), 
            bg=self.colors["sidebar"], 
            fg=self.colors["robot"]
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        subtitle_label = tk.Label(
            self.sidebar, 
            text="2D Grid Agent Controller Simulator", 
            font=("Segoe UI", 9, "italic"), 
            bg=self.colors["sidebar"], 
            fg=self.colors["text_muted"]
        )
        subtitle_label.pack(anchor="w", pady=(0, 25))
        
        # --- Metrics Dashboard Section ---
        metrics_group = tk.LabelFrame(
            self.sidebar, 
            text="Live Statistics", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.colors["sidebar"], 
            fg=self.colors["text"],
            padx=15, 
            pady=15,
            bd=1,
            relief="solid",
            highlightbackground=self.colors["grid_lines"]
        )
        metrics_group.pack(fill="x", pady=(0, 20))
        
        # We will keep dictionary of labels to update dynamically
        self.metrics_labels = {}
        metrics_to_create = [
            ("Grid Size", "grid_size", "10 x 10"),
            ("Robot Position", "robot_pos", "(0, 0)"),
            ("Target Position", "target_pos", "(0, 0)"),
            ("Steps Taken", "steps", "0 / 50"),
            ("Cumulative Reward", "reward", "0.00"),
            ("Last Action Taken", "last_action", "N/A"),
        ]
        
        for index, (label_text, key, initial_val) in enumerate(metrics_to_create):
            frame = tk.Frame(metrics_group, bg=self.colors["sidebar"])
            frame.pack(fill="x", pady=4)
            
            lbl = tk.Label(
                frame, 
                text=label_text + ":", 
                font=("Segoe UI", 9), 
                bg=self.colors["sidebar"], 
                fg=self.colors["text_muted"]
            )
            lbl.pack(side="left")
            
            val_lbl = tk.Label(
                frame, 
                text=initial_val, 
                font=("Segoe UI", 9, "bold"), 
                bg=self.colors["sidebar"], 
                fg=self.colors["text"]
            )
            val_lbl.pack(side="right")
            self.metrics_labels[key] = val_lbl
            
        # --- Status Box ---
        self.status_frame = tk.Frame(self.sidebar, bg=self.colors["bg"], height=40, bd=1, relief="solid")
        self.status_frame.pack(fill="x", pady=(0, 25))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="Status: Idle", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.colors["bg"], 
            fg=self.colors["text_muted"]
        )
        self.status_label.pack(expand=True)
        
        # --- Control Sliders and Buttons Section ---
        controls_group = tk.LabelFrame(
            self.sidebar, 
            text="Simulation Controls", 
            font=("Segoe UI", 10, "bold"), 
            bg=self.colors["sidebar"], 
            fg=self.colors["text"],
            padx=15, 
            pady=15,
            bd=1,
            relief="solid"
        )
        controls_group.pack(fill="x", pady=(0, 10))
        
        # Speed slider frame
        slider_frame = tk.Frame(controls_group, bg=self.colors["sidebar"])
        slider_frame.pack(fill="x", pady=(0, 15))
        
        slider_lbl = tk.Label(
            slider_frame, 
            text="Step Delay (seconds):", 
            font=("Segoe UI", 9), 
            bg=self.colors["sidebar"], 
            fg=self.colors["text_muted"]
        )
        slider_lbl.pack(anchor="w")
        
        # Custom styling for scale widget
        self.speed_scale = tk.Scale(
            slider_frame, 
            from_=0.02, 
            to=1.5, 
            resolution=0.01, 
            orient="horizontal", 
            bg=self.colors["sidebar"], 
            fg=self.colors["text"], 
            troughcolor=self.colors["bg"], 
            activebackground=self.colors["robot"],
            highlightthickness=0,
            command=self._on_speed_change
        )
        self.speed_scale.set(self.delay_ms / 1000.0)
        self.speed_scale.pack(fill="x", pady=(5, 0))
        
        # Buttons Row 1: Play/Pause and Step
        btn_frame1 = tk.Frame(controls_group, bg=self.colors["sidebar"])
        btn_frame1.pack(fill="x", pady=(0, 10))
        
        self.play_btn = tk.Button(
            btn_frame1, 
            text="▶ Play Simulation", 
            font=("Segoe UI", 9, "bold"), 
            bg=self.colors["robot"], 
            fg=self.colors["bg"], 
            activebackground=self.colors["button_active"], 
            activeforeground=self.colors["text"], 
            bd=0, 
            cursor="hand2",
            padx=10, 
            pady=6,
            command=self.toggle_play
        )
        self.play_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.step_btn = tk.Button(
            btn_frame1, 
            text="⏭ Step", 
            font=("Segoe UI", 9, "bold"), 
            bg=self.colors["button_bg"], 
            fg=self.colors["text"], 
            activebackground=self.colors["button_active"], 
            activeforeground=self.colors["text"], 
            bd=0, 
            cursor="hand2",
            padx=10, 
            pady=6,
            command=self.step_simulation_once
        )
        self.step_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Buttons Row 2: Reset
        self.reset_btn = tk.Button(
            controls_group, 
            text="🔄 Restart Simulation", 
            font=("Segoe UI", 9, "bold"), 
            bg=self.colors["button_bg"], 
            fg=self.colors["text"], 
            activebackground=self.colors["button_active"], 
            activeforeground=self.colors["text"], 
            bd=0, 
            cursor="hand2",
            padx=10, 
            pady=6,
            command=self.reset_simulation
        )
        self.reset_btn.pack(fill="x")

    def _reset_simulation_state(self) -> None:
        """Resets the core simulation data without rebuilding widgets."""
        self.observation = self.env.reset()
        self.step_count = 0
        self.total_reward = 0.0
        self.last_action = "N/A"
        self.last_reward = 0.0
        self.path_history = [self.observation["robot_position"]]
        self._update_metrics_view()
        self._set_status("Initialized & Ready", self.colors["text_muted"])
        self.draw_grid()

    def _on_canvas_resize(self, event) -> None:
        """Triggered when window/canvas is resized to scale elements."""
        self.draw_grid()

    def _on_speed_change(self, val: str) -> None:
        """Updates delay when slider moves."""
        self.delay_ms = int(float(val) * 1000)

    def draw_grid(self) -> None:
        """Draws the grid board, grid cells, trace paths, target, and robot."""
        self.canvas.delete("all")
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        # If not fully rendered yet, wait
        if canvas_w < 10 or canvas_h < 10:
            return
            
        grid_w, grid_h = self.env.width, self.env.height
        
        # Find cell scale factor to fit canvas symmetrically
        cell_size = min(canvas_w // grid_w, canvas_h // grid_h)
        offset_x = (canvas_w - (cell_size * grid_w)) // 2
        offset_y = (canvas_h - (cell_size * grid_h)) // 2
        
        # Draw background grid grid cells
        for r in range(grid_h):
            for c in range(grid_w):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=self.colors["grid_bg"], 
                    outline=self.colors["grid_lines"], 
                    width=1
                )
        
        # Draw trace path history
        if len(self.path_history) > 1:
            for idx in range(len(self.path_history) - 1):
                c1, r1 = self.path_history[idx]
                c2, r2 = self.path_history[idx + 1]
                
                # Coordinate center of starting and ending cell
                start_x = offset_x + c1 * cell_size + cell_size // 2
                start_y = offset_y + r1 * cell_size + cell_size // 2
                end_x = offset_x + c2 * cell_size + cell_size // 2
                end_y = offset_y + r2 * cell_size + cell_size // 2
                
                self.canvas.create_line(
                    start_x, start_y, end_x, end_y, 
                    fill=self.colors["path"], 
                    width=3, 
                    dash=(4, 2),
                    arrow="last",
                    arrowshape=(8, 10, 3)
                )

        # Draw Target ('T') - Rose color glowing node
        tx, ty = self.observation["target_position"]
        tx1 = offset_x + tx * cell_size + int(cell_size * 0.15)
        ty1 = offset_y + ty * cell_size + int(cell_size * 0.15)
        tx2 = tx1 + int(cell_size * 0.7)
        ty2 = ty1 + int(cell_size * 0.7)
        
        # Pulse/Glow outline
        self.canvas.create_oval(
            tx1 - 2, ty1 - 2, tx2 + 2, ty2 + 2, 
            fill="", 
            outline=self.colors["target"], 
            width=1
        )
        self.canvas.create_oval(
            tx1, ty1, tx2, ty2, 
            fill=self.colors["target"], 
            outline="#ffffff", 
            width=2
        )
        # Inner target core dot
        self.canvas.create_oval(
            tx1 + int(cell_size * 0.2), ty1 + int(cell_size * 0.2), 
            tx2 - int(cell_size * 0.2), ty2 - int(cell_size * 0.2), 
            fill="#ffffff", 
            outline=""
        )

        # Draw Robot ('R') - Glowing sky blue node
        rx, ry = self.observation["robot_position"]
        rx1 = offset_x + rx * cell_size + int(cell_size * 0.15)
        ry1 = offset_y + ry * cell_size + int(cell_size * 0.15)
        rx2 = rx1 + int(cell_size * 0.7)
        ry2 = ry1 + int(cell_size * 0.7)
        
        self.canvas.create_oval(
            rx1 - 2, ry1 - 2, rx2 + 2, ry2 + 2, 
            fill="", 
            outline=self.colors["robot"], 
            width=1
        )
        self.canvas.create_oval(
            rx1, ry1, rx2, ry2, 
            fill=self.colors["robot"], 
            outline="#ffffff", 
            width=2
        )
        
        # Draw a little robot direction icon or inner pattern
        self.canvas.create_oval(
            rx1 + int(cell_size * 0.2), ry1 + int(cell_size * 0.2), 
            rx2 - int(cell_size * 0.2), ry2 - int(cell_size * 0.2), 
            fill=self.colors["bg"], 
            outline=""
        )
        self.canvas.create_oval(
            rx1 + int(cell_size * 0.28), ry1 + int(cell_size * 0.28), 
            rx2 - int(cell_size * 0.28), ry2 - int(cell_size * 0.28), 
            fill="#ffffff", 
            outline=""
        )

    def toggle_play(self) -> None:
        """Toggles running state between playing and paused."""
        if self.is_running:
            self.is_running = False
            self.play_btn.config(text="▶ Resume Simulation", bg=self.colors["robot"])
            self._set_status("Paused", self.colors["text_muted"])
        else:
            # Check if simulation is already completed; reset automatically if so
            is_success = self.observation["robot_position"] == self.observation["target_position"]
            is_limit = self.step_count >= self.max_steps
            if is_success or is_limit:
                self._reset_simulation_state()
                
            self.is_running = True
            self.play_btn.config(text="⏸ Pause Simulation", bg=self.colors["danger"])
            self._set_status("Running...", self.colors["robot"])
            self.root.after(self.delay_ms, self._step_simulation_loop)

    def step_simulation_once(self) -> None:
        """Triggers a single simulation step manually."""
        if self.is_running:
            self.toggle_play() # Pause first if running
        self._execute_step()

    def reset_simulation(self) -> None:
        """Handles user clicking reset button."""
        if self.is_running:
            self.is_running = False
            self.play_btn.config(text="▶ Play Simulation", bg=self.colors["robot"])
        self._reset_simulation_state()

    def _execute_step(self) -> bool:
        """
        Executes a single step in the simulator.
        Returns:
            bool: True if simulation should continue, False if ended (done or step limit).
        """
        is_success = self.observation["robot_position"] == self.observation["target_position"]
        is_limit = self.step_count >= self.max_steps
        
        if is_success or is_limit:
            return False
            
        action = self.agent.select_action(self.observation)
        next_obs, reward, done, info = self.env.step(action)
        
        self.step_count += 1
        self.total_reward += reward
        self.last_action = action
        self.last_reward = reward
        self.observation = next_obs
        
        self.path_history.append(self.observation["robot_position"])
        
        self._update_metrics_view()
        self.draw_grid()
        
        # Check termination outcomes
        if self.observation["robot_position"] == self.observation["target_position"]:
            self._set_status(f"Success! Goal Reached in {self.step_count} Steps.", self.colors["success"])
            self.is_running = False
            self.play_btn.config(text="▶ Play Simulation", bg=self.colors["robot"])
            return False
            
        if self.step_count >= self.max_steps:
            self._set_status("Failed! Out of steps.", self.colors["danger"])
            self.is_running = False
            self.play_btn.config(text="▶ Play Simulation", bg=self.colors["robot"])
            return False
            
        return True

    def _step_simulation_loop(self) -> None:
        """Recursive loop running steps periodically while running state is active."""
        if not self.is_running:
            return
            
        should_continue = self._execute_step()
        if should_continue:
            self.root.after(self.delay_ms, self._step_simulation_loop)

    def _update_metrics_view(self) -> None:
        """Updates text labels in the live sidebar dashboard."""
        obs = self.observation
        rx, ry = obs["robot_position"]
        tx, ty = obs["target_position"]
        w, h = obs["grid_size"]
        
        self.metrics_labels["grid_size"].config(text=f"{w} x {h}")
        self.metrics_labels["robot_pos"].config(text=f"({rx}, {ry})")
        self.metrics_labels["target_pos"].config(text=f"({tx}, {ty})")
        self.metrics_labels["steps"].config(text=f"{self.step_count} / {self.max_steps}")
        
        # Format reward with color highlights
        self.metrics_labels["reward"].config(text=f"{self.total_reward:.2f}")
        if self.total_reward > 0:
            self.metrics_labels["reward"].config(fg=self.colors["success"])
        elif self.total_reward < 0:
            self.metrics_labels["reward"].config(fg=self.colors["danger"])
        else:
            self.metrics_labels["reward"].config(fg=self.colors["text"])
            
        # Format action taken
        if self.last_action != "N/A":
            self.metrics_labels["last_action"].config(
                text=f"{self.last_action} (rew: {self.last_reward:.1f})",
                fg=self.colors["robot"]
            )
        else:
            self.metrics_labels["last_action"].config(text="N/A", fg=self.colors["text_muted"])

    def _set_status(self, text: str, color: str) -> None:
        """Updates the status display area."""
        self.status_label.config(text=f"Status: {text}", fg=color)

    def start(self) -> None:
        """Starts the Tkinter main loop (blocking)."""
        self.root.mainloop()
