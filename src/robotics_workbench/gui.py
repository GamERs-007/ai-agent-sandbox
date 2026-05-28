import tkinter as tk
from typing import List, Tuple

from robotics_workbench.agent import BaseAgent
from robotics_workbench.environment import GridEnvironment


class GUIRunner:
    """
    A Tkinter-based GUI simulation runner for the Robotics Workbench.
    Visualizes the 2D grid, robot path trace, and real-time dashboard metrics.
    """

    def __init__(
        self,
        env: GridEnvironment,
        agent: BaseAgent,
        max_steps: int = 50,
        initial_delay: float = 0.2,
    ):
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

        # Balanced dark palette with warm neutrals and distinct signal colors.
        self.colors = {
            "bg": "#111318",
            "sidebar": "#20242c",
            "panel": "#272c35",
            "grid_bg": "#181b21",
            "grid_lines": "#3a404c",
            "text": "#f6f1e8",
            "text_muted": "#b8b1a5",
            "robot": "#2dd4bf",
            "target": "#fb7185",
            "path": "#f59e0b",
            "success": "#22c55e",
            "danger": "#f97316",
            "button_bg": "#3b4250",
            "button_active": "#4b5563",
        }
        self.fonts = {
            "title": ("Segoe UI", 17, "bold"),
            "section": ("Segoe UI", 10, "bold"),
            "body": ("Segoe UI", 9),
            "body_bold": ("Segoe UI", 9, "bold"),
            "status": ("Segoe UI", 10, "bold"),
        }

        self.metrics_labels = {}
        self.wrap_targets: List[Tuple[tk.Label, int, int]] = []

        self._setup_window()
        self._reset_simulation_state()

    def _setup_window(self) -> None:
        """Configures the Tkinter root window and widget layouts."""
        self.root = tk.Tk()
        self.root.title("Robotics Simulation Workbench")
        self.root.geometry("1040x680")
        self.root.minsize(820, 560)
        self.root.configure(bg=self.colors["bg"])

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0, minsize=340)
        self.root.rowconfigure(0, weight=1)

        # Left area: simulation canvas.
        self.canvas_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=24, pady=24)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=self.colors["grid_bg"],
            highlightthickness=1,
            highlightbackground=self.colors["grid_lines"],
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Right area: fixed-width dashboard.
        self.sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], padx=24, pady=24)
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.bind("<Configure>", self._on_sidebar_resize)

        title_label = tk.Label(
            self.sidebar,
            text="Robotics Workbench",
            font=self.fonts["title"],
            bg=self.colors["sidebar"],
            fg=self.colors["robot"],
            anchor="w",
        )
        title_label.pack(anchor="w", fill="x", pady=(0, 4))

        subtitle_label = tk.Label(
            self.sidebar,
            text="2D grid agent controller simulator",
            font=self.fonts["body"],
            bg=self.colors["sidebar"],
            fg=self.colors["text_muted"],
            anchor="w",
            justify="left",
            wraplength=292,
        )
        subtitle_label.pack(anchor="w", fill="x", pady=(0, 24))
        self.wrap_targets.append((subtitle_label, 48, 160))

        self.metrics_group = self._create_section(self.sidebar, "Live Statistics")
        metrics_to_create = [
            ("Grid Size", "grid_size", "10 x 10"),
            ("Robot Position", "robot_pos", "(0, 0)"),
            ("Target Position", "target_pos", "(0, 0)"),
            ("Steps Taken", "steps", "0 / 50"),
            ("Cumulative Reward", "reward", "0.00"),
            ("Last Action Taken", "last_action", "N/A"),
        ]
        for label_text, key, initial_val in metrics_to_create:
            self._add_metric_row(label_text, key, initial_val)

        self.status_frame = tk.Frame(
            self.sidebar,
            bg=self.colors["grid_bg"],
            bd=1,
            relief="solid",
            highlightbackground=self.colors["grid_lines"],
        )
        self.status_frame.pack(fill="x", pady=(0, 22))
        self.status_frame.columnconfigure(0, weight=1)

        self.status_label = tk.Label(
            self.status_frame,
            text="Status: Idle",
            font=self.fonts["status"],
            bg=self.colors["grid_bg"],
            fg=self.colors["text_muted"],
            justify="center",
            wraplength=260,
        )
        self.status_label.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        self.wrap_targets.append((self.status_label, 76, 160))

        controls_group = self._create_section(
            self.sidebar,
            "Simulation Controls",
            bottom_padding=10,
        )

        slider_frame = tk.Frame(controls_group, bg=self.colors["panel"])
        slider_frame.pack(fill="x", pady=(0, 15))
        slider_frame.columnconfigure(0, weight=1)

        slider_lbl = tk.Label(
            slider_frame,
            text="Step Delay (seconds):",
            font=self.fonts["body"],
            bg=self.colors["panel"],
            fg=self.colors["text_muted"],
            anchor="w",
        )
        slider_lbl.grid(row=0, column=0, sticky="w")

        self.speed_value_label = tk.Label(
            slider_frame,
            text=f"{self.delay_ms / 1000.0:.2f}s",
            font=self.fonts["body_bold"],
            bg=self.colors["panel"],
            fg=self.colors["text"],
            anchor="e",
        )
        self.speed_value_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.speed_scale = tk.Scale(
            slider_frame,
            from_=0.02,
            to=1.5,
            resolution=0.01,
            orient="horizontal",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            troughcolor=self.colors["bg"],
            activebackground=self.colors["robot"],
            highlightthickness=0,
            command=self._on_speed_change,
        )
        self.speed_scale.set(self.delay_ms / 1000.0)
        self.speed_scale.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        btn_frame = tk.Frame(controls_group, bg=self.colors["panel"])
        btn_frame.pack(fill="x", pady=(0, 10))
        btn_frame.columnconfigure(0, weight=1, uniform="action_buttons")
        btn_frame.columnconfigure(1, weight=1, uniform="action_buttons")

        self.play_btn = self._create_button(
            btn_frame,
            text="Play",
            bg=self.colors["robot"],
            fg=self.colors["bg"],
            command=self.toggle_play,
        )
        self.play_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=2)

        self.step_btn = self._create_button(
            btn_frame,
            text="Step",
            bg=self.colors["button_bg"],
            fg=self.colors["text"],
            command=self.step_simulation_once,
        )
        self.step_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=2)

        self.reset_btn = self._create_button(
            controls_group,
            text="Restart",
            bg=self.colors["button_bg"],
            fg=self.colors["text"],
            command=self.reset_simulation,
        )
        self.reset_btn.pack(fill="x", ipady=2)

    def _create_section(
        self,
        parent: tk.Widget,
        title: str,
        bottom_padding: int = 20,
    ) -> tk.Frame:
        """Creates a compact titled panel for sidebar content."""
        title_label = tk.Label(
            parent,
            text=title,
            font=self.fonts["section"],
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            anchor="w",
        )
        title_label.pack(fill="x", pady=(0, 8))

        section = tk.Frame(
            parent,
            bg=self.colors["panel"],
            padx=14,
            pady=14,
            bd=1,
            relief="solid",
            highlightbackground=self.colors["grid_lines"],
        )
        section.pack(fill="x", pady=(0, bottom_padding))
        section.columnconfigure(0, weight=1)
        return section

    def _create_button(
        self,
        parent: tk.Widget,
        text: str,
        bg: str,
        fg: str,
        command,
    ) -> tk.Button:
        """Creates a consistently styled action button."""
        return tk.Button(
            parent,
            text=text,
            font=self.fonts["body_bold"],
            bg=bg,
            fg=fg,
            activebackground=self.colors["button_active"],
            activeforeground=self.colors["text"],
            bd=0,
            cursor="hand2",
            padx=10,
            pady=6,
            command=command,
        )

    def _add_metric_row(self, label_text: str, key: str, initial_val: str) -> None:
        """Adds one responsive metric row to the live statistics panel."""
        row = tk.Frame(self.metrics_group, bg=self.colors["panel"])
        row.pack(fill="x", pady=4)
        row.columnconfigure(0, weight=1, minsize=116)
        row.columnconfigure(1, weight=1, minsize=128)

        lbl = tk.Label(
            row,
            text=label_text + ":",
            font=self.fonts["body"],
            bg=self.colors["panel"],
            fg=self.colors["text_muted"],
            anchor="w",
            justify="left",
            wraplength=130,
        )
        lbl.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        val_lbl = tk.Label(
            row,
            text=initial_val,
            font=self.fonts["body_bold"],
            bg=self.colors["panel"],
            fg=self.colors["text"],
            anchor="e",
            justify="right",
            wraplength=136,
        )
        val_lbl.grid(row=0, column=1, sticky="ew")

        self.metrics_labels[key] = val_lbl
        self.wrap_targets.append((lbl, 210, 104))
        self.wrap_targets.append((val_lbl, 206, 112))

    def _reset_simulation_state(self) -> None:
        """Resets the core simulation data without rebuilding widgets."""
        self.observation = self.env.reset()
        self.step_count = 0
        self.total_reward = 0.0
        self.last_action = "N/A"
        self.last_reward = 0.0
        self.path_history = [self.observation["robot_position"]]
        self._update_metrics_view()
        self._set_status("Initialized and ready", self.colors["text_muted"])
        self.draw_grid()

    def _on_canvas_resize(self, event) -> None:
        """Triggered when window/canvas is resized to scale elements."""
        self.draw_grid()

    def _on_sidebar_resize(self, event) -> None:
        """Keeps labels wrapped within the current sidebar width."""
        for label, horizontal_padding, min_width in self.wrap_targets:
            label.configure(wraplength=max(min_width, event.width - horizontal_padding))

    def _on_speed_change(self, val: str) -> None:
        """Updates delay when slider moves."""
        seconds = float(val)
        self.delay_ms = int(seconds * 1000)
        self.speed_value_label.config(text=f"{seconds:.2f}s")

    def draw_grid(self) -> None:
        """Draws the grid board, trace paths, target, and robot."""
        self.canvas.delete("all")

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            return

        grid_w, grid_h = self.env.width, self.env.height
        cell_size = min(canvas_w / grid_w, canvas_h / grid_h)
        if cell_size <= 0:
            return

        board_w = cell_size * grid_w
        board_h = cell_size * grid_h
        offset_x = (canvas_w - board_w) / 2
        offset_y = (canvas_h - board_h) / 2

        for r in range(grid_h):
            for c in range(grid_w):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.colors["grid_bg"],
                    outline=self.colors["grid_lines"],
                    width=1,
                )

        if len(self.path_history) > 1:
            for idx in range(len(self.path_history) - 1):
                c1, r1 = self.path_history[idx]
                c2, r2 = self.path_history[idx + 1]

                start_x = offset_x + c1 * cell_size + cell_size / 2
                start_y = offset_y + r1 * cell_size + cell_size / 2
                end_x = offset_x + c2 * cell_size + cell_size / 2
                end_y = offset_y + r2 * cell_size + cell_size / 2

                self.canvas.create_line(
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    fill=self.colors["path"],
                    width=max(2, int(cell_size * 0.08)),
                    dash=(4, 2),
                    arrow="last",
                    arrowshape=(8, 10, 3),
                )

        self._draw_target(cell_size, offset_x, offset_y)
        self._draw_robot(cell_size, offset_x, offset_y)

    def _draw_target(self, cell_size: float, offset_x: float, offset_y: float) -> None:
        """Draws the target marker in the current observation."""
        tx, ty = self.observation["target_position"]
        padding = cell_size * 0.15
        tx1 = offset_x + tx * cell_size + padding
        ty1 = offset_y + ty * cell_size + padding
        tx2 = tx1 + cell_size * 0.7
        ty2 = ty1 + cell_size * 0.7

        self.canvas.create_oval(
            tx1 - 2,
            ty1 - 2,
            tx2 + 2,
            ty2 + 2,
            fill="",
            outline=self.colors["target"],
            width=1,
        )
        self.canvas.create_oval(
            tx1,
            ty1,
            tx2,
            ty2,
            fill=self.colors["target"],
            outline="#ffffff",
            width=2,
        )
        self.canvas.create_oval(
            tx1 + cell_size * 0.2,
            ty1 + cell_size * 0.2,
            tx2 - cell_size * 0.2,
            ty2 - cell_size * 0.2,
            fill="#ffffff",
            outline="",
        )

    def _draw_robot(self, cell_size: float, offset_x: float, offset_y: float) -> None:
        """Draws the robot marker in the current observation."""
        rx, ry = self.observation["robot_position"]
        padding = cell_size * 0.15
        rx1 = offset_x + rx * cell_size + padding
        ry1 = offset_y + ry * cell_size + padding
        rx2 = rx1 + cell_size * 0.7
        ry2 = ry1 + cell_size * 0.7

        self.canvas.create_oval(
            rx1 - 2,
            ry1 - 2,
            rx2 + 2,
            ry2 + 2,
            fill="",
            outline=self.colors["robot"],
            width=1,
        )
        self.canvas.create_oval(
            rx1,
            ry1,
            rx2,
            ry2,
            fill=self.colors["robot"],
            outline="#ffffff",
            width=2,
        )
        self.canvas.create_oval(
            rx1 + cell_size * 0.2,
            ry1 + cell_size * 0.2,
            rx2 - cell_size * 0.2,
            ry2 - cell_size * 0.2,
            fill=self.colors["bg"],
            outline="",
        )
        self.canvas.create_oval(
            rx1 + cell_size * 0.28,
            ry1 + cell_size * 0.28,
            rx2 - cell_size * 0.28,
            ry2 - cell_size * 0.28,
            fill="#ffffff",
            outline="",
        )

    def toggle_play(self) -> None:
        """Toggles running state between playing and paused."""
        if self.is_running:
            self.is_running = False
            self.play_btn.config(text="Resume", bg=self.colors["robot"])
            self._set_status("Paused", self.colors["text_muted"])
        else:
            is_success = self.observation["robot_position"] == self.observation["target_position"]
            is_limit = self.step_count >= self.max_steps
            if is_success or is_limit:
                self._reset_simulation_state()

            self.is_running = True
            self.play_btn.config(text="Pause", bg=self.colors["danger"])
            self._set_status("Running...", self.colors["robot"])
            self.root.after(self.delay_ms, self._step_simulation_loop)

    def step_simulation_once(self) -> None:
        """Triggers a single simulation step manually."""
        if self.is_running:
            self.toggle_play()
        self._execute_step()

    def reset_simulation(self) -> None:
        """Handles user clicking reset button."""
        if self.is_running:
            self.is_running = False
            self.play_btn.config(text="Play", bg=self.colors["robot"])
        self._reset_simulation_state()

    def _execute_step(self) -> bool:
        """
        Executes a single step in the simulator.

        Returns:
            bool: True if simulation should continue, False if ended.
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

        if self.observation["robot_position"] == self.observation["target_position"]:
            self._set_status(
                f"Success! Goal reached in {self.step_count} steps.",
                self.colors["success"],
            )
            self.is_running = False
            self.play_btn.config(text="Play", bg=self.colors["robot"])
            return False

        if self.step_count >= self.max_steps:
            self._set_status("Failed! Out of steps.", self.colors["danger"])
            self.is_running = False
            self.play_btn.config(text="Play", bg=self.colors["robot"])
            return False

        return True

    def _step_simulation_loop(self) -> None:
        """Recursive loop running steps periodically while active."""
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

        self.metrics_labels["reward"].config(text=f"{self.total_reward:.2f}")
        if self.total_reward > 0:
            self.metrics_labels["reward"].config(fg=self.colors["success"])
        elif self.total_reward < 0:
            self.metrics_labels["reward"].config(fg=self.colors["danger"])
        else:
            self.metrics_labels["reward"].config(fg=self.colors["text"])

        if self.last_action != "N/A":
            self.metrics_labels["last_action"].config(
                text=f"{self.last_action} (rew: {self.last_reward:.1f})",
                fg=self.colors["robot"],
            )
        else:
            self.metrics_labels["last_action"].config(
                text="N/A",
                fg=self.colors["text_muted"],
            )

    def _set_status(self, text: str, color: str) -> None:
        """Updates the status display area."""
        self.status_label.config(text=f"Status: {text}", fg=color)

    def start(self) -> None:
        """Starts the Tkinter main loop."""
        self.root.mainloop()
