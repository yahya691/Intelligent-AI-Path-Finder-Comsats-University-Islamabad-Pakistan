# COMSATS Campus Navigation 


import math
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QComboBox, QPushButton, QTextEdit, QFrame,
                            QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsLineItem,
                            QGraphicsEllipseItem, QGraphicsTextItem, QTabWidget, QGraphicsRectItem,
                            QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QPixmap, QFont, QColor, QPen, QBrush, QPainter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

BACKGROUND_PATH = "/mnt/data/0c142a02-f067-40b0-bc20-da60dd351ef0.png"
DESIGN_W, DESIGN_H = 1200, 600

# -------------------------
# Map 
# -------------------------
DEFAULT_MAP = {
    "buildings": [
        {"id": "Mosque", "x": 100, "y": 300},
        {"id": "Main Gate (Gate 1)", "x": 100, "y": 520},
        {"id": "Gate 2", "x": 60, "y": 60},
        {"id": "Gate 3", "x": 820, "y": 40},
        {"id": "Academic I", "x": 260, "y": 180},
        {"id": "Physics", "x": 380, "y": 140},
        {"id": "Academic II", "x": 460, "y": 240},
        {"id": "Faculty Block", "x": 560, "y": 220},
        {"id": "Admin Block", "x": 700, "y": 100},
        {"id": "Library", "x": 840, "y": 200},
        {"id": "Student Cafeteria", "x": 760, "y": 320},
        {"id": "Sports Complex", "x": 920, "y": 60},
        {"id": "Academic III", "x": 1080, "y": 100},  
        {"id": "Medical Center", "x": 180, "y": 80},
        {"id": "Hostel City Hub", "x": 1060, "y": 320},
        {"id": "Hostel A", "x": 980, "y": 240},
        {"id": "Hostel B", "x": 1140, "y": 240},
        {"id": "Hostel C", "x": 980, "y": 380},
        {"id": "Hostel D", "x": 1140, "y": 380},
        {"id": "Cheezious", "x": 1180, "y": 160},
    ],
    "roads": [
        {"from": "Mosque", "to": "Academic I", "cost": 4},
        {"from": "Academic I", "to": "Physics", "cost": 2},
        {"from": "Physics", "to": "Academic II", "cost": 3},
        {"from": "Academic II", "to": "Faculty Block", "cost": 2},
        {"from": "Mosque", "to": "Faculty Block", "cost": 6},

        {"from": "Faculty Block", "to": "Admin Block", "cost": 3},
        {"from": "Admin Block", "to": "Library", "cost": 4},
        {"from": "Library", "to": "Student Cafeteria", "cost": 2},

        {"from": "Student Cafeteria", "to": "Hostel City Hub", "cost": 8},
        {"from": "Library", "to": "Hostel City Hub", "cost": 9},

        {"from": "Admin Block", "to": "Sports Complex", "cost": 6},
        {"from": "Sports Complex", "to": "Academic III", "cost": 4},  

        # Gate 1 (Main)
        {"from": "Main Gate (Gate 1)", "to": "Mosque", "cost": 3},
        {"from": "Main Gate (Gate 1)", "to": "Medical Center", "cost": 4},
        {"from": "Medical Center", "to": "Academic I", "cost": 5},

        # Gate 2 
        {"from": "Gate 2", "to": "Medical Center", "cost": 5},
        {"from": "Gate 2", "to": "Mosque", "cost": 4},

        # Gate 3 
        {"from": "Gate 3", "to": "Sports Complex", "cost": 3},
        {"from": "Gate 3", "to": "Admin Block", "cost": 3},
        {"from": "Gate 3", "to": "Library", "cost": 8},

        # hostel hub spokes
        {"from": "Hostel City Hub", "to": "Hostel A", "cost": 1},
        {"from": "Hostel City Hub", "to": "Hostel B", "cost": 1},
        {"from": "Hostel City Hub", "to": "Hostel C", "cost": 1},
        {"from": "Hostel City Hub", "to": "Hostel D", "cost": 1},

        {"from": "Hostel B", "to": "Cheezious", "cost": 1},
        {"from": "Hostel C", "to": "Cheezious", "cost": 1},

        {"from": "Library", "to": "Cheezious", "cost": 12},
    ],
}

# -------------------------
# Graph and search 
# -------------------------
def euclidean(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def reconstruct_path(parents, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parents.get(node)
    return list(reversed(path))

class Graph:
    def __init__(self, data):
        self.positions = {}
        self.adj = {}
        self._build(data)

    def _build(self, data):
        for b in data.get("buildings", []):
            self.positions[b["id"]] = (b["x"], b["y"])
            self.adj.setdefault(b["id"], [])
        for r in data.get("roads", []):
            a, b, c = r["from"], r["to"], float(r.get("cost", 1))
            if a in self.positions and b in self.positions:
                self.adj[a].append((b, c))
                self.adj[b].append((a, c))

    def nodes(self):
        return list(self.positions.keys())

    def neighbors(self, node):
        for nb, cost in self.adj.get(node, []):
            yield nb, cost

    def edges(self):
        seen = set()
        out = []
        for a, nbs in self.adj.items():
            for b, cost in nbs:
                key = tuple(sorted((a, b)))
                if key in seen:
                    continue
                seen.add(key)
                out.append((a, b, cost))
        return out

class SearchResult:
    def __init__(self, path=None, cost=0.0, visited=None):
        self.path = path or []
        self.cost = cost
        self.visited = visited or []

# BFS
def bfs(graph, start, goal):
    q = [start]
    head = 0
    visited = {start: True}
    parents = {start: None}
    order = []
    while head < len(q):
        node = q[head]; head += 1
        order.append(node)
        if node == goal:
            break
        for nb, _ in graph.neighbors(node):
            if nb not in visited:
                visited[nb] = True
                parents[nb] = node
                q.append(nb)
    if goal not in parents:
        return SearchResult([], float("inf"), order)
    path = reconstruct_path(parents, goal)
    return SearchResult(path, len(path) - 1, order)

# DFS
def dfs(graph, start, goal):
    stack = [start]
    visited = {start: True}
    parents = {start: None}
    order = []
    while stack:
        node = stack.pop()
        order.append(node)
        if node == goal:
            break
        neighs = list(graph.neighbors(node))
        neighs.reverse()
        for nb, _ in neighs:
            if nb not in visited:
                visited[nb] = True
                parents[nb] = node
                stack.append(nb)
    if goal not in parents:
        return SearchResult([], float("inf"), order)
    path = reconstruct_path(parents, goal)
    return SearchResult(path, len(path) - 1, order)

# Uniform Cost Search (UCS)
def uniform_cost_search(graph, start, goal):
    queue = [(0.0, start)]
    parents = {start: None}
    costs = {start: 0.0}
    order = []
    while queue:
        idx = min(range(len(queue)), key=lambda i: queue[i][0])
        cost, node = queue.pop(idx)
        if node in order:
            continue
        order.append(node)
        if node == goal:
            break
        for nb, ec in graph.neighbors(node):
            nc = cost + ec
            if nb not in costs or nc < costs[nb]:
                costs[nb] = nc
                parents[nb] = node
                queue.append((nc, nb))
    if goal not in parents:
        return SearchResult([], float("inf"), order)
    path = reconstruct_path(parents, goal)
    return SearchResult(path, costs[goal], order)

# Greedy best-first
def greedy_best_first(graph, start, goal):
    queue = [(euclidean(graph.positions[start], graph.positions[goal]), start)]
    parents = {start: None}
    visited = set()
    order = []
    while queue:
        idx = min(range(len(queue)), key=lambda i: queue[i][0])
        _, node = queue.pop(idx)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        if node == goal:
            break
        for nb, _ in graph.neighbors(node):
            if nb not in visited:
                if nb not in parents:
                    parents[nb] = node
                queue.append((euclidean(graph.positions[nb], graph.positions[goal]), nb))
    if goal not in parents:
        return SearchResult([], float("inf"), order)
    path = reconstruct_path(parents, goal)
    total_cost = 0.0
    for a, b in zip(path, path[1:]):
        for nb, c in graph.adj[a]:
            if nb == b:
                total_cost += c
                break
    return SearchResult(path, total_cost, order)

# A* search
def a_star_search(graph, start, goal):
    def get_heuristic(node, goal_node):
        return euclidean(graph.positions[node], graph.positions[goal_node])
    queue = [(get_heuristic(start, goal), 0.0, start)]
    parents = {start: None}
    g_costs = {start: 0.0}
    order = []
    while queue:
        idx = min(range(len(queue)), key=lambda i: queue[i][0])
        f_cost, g_cost, node = queue.pop(idx)
        if node in order:
            continue
        order.append(node)
        if node == goal:
            break
        for nb, edge_cost in graph.neighbors(node):
            new_g_cost = g_cost + edge_cost
            if nb not in g_costs or new_g_cost < g_costs[nb]:
                g_costs[nb] = new_g_cost
                parents[nb] = node
                f_cost = new_g_cost + get_heuristic(nb, goal)
                queue.append((f_cost, new_g_cost, nb))
    if goal not in parents:
        return SearchResult([], float("inf"), order)
    path = reconstruct_path(parents, goal)
    return SearchResult(path, g_costs[goal], order)

# Best-first 
def best_first_search(graph, start, goal):
    def get_heuristic(node, goal_node):
        return euclidean(graph.positions[node], graph.positions[goal_node])
    queue = [(get_heuristic(start, goal), start)]
    parents = {start: None}
    visited = set()
    order = []
    while queue:
        idx = min(range(len(queue)), key=lambda i: queue[i][0])
        heuristic, node = queue.pop(idx)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        if node == goal:
            break
        for nb, edge_cost in graph.neighbors(node):
            if nb not in visited:
                if nb not in parents:
                    parents[nb] = node
                queue.append((get_heuristic(nb, goal), nb))
    if goal not in parents:
        return SearchResult([], float("inf"), order)
    path = reconstruct_path(parents, goal)
    total_cost = 0.0
    for a, b in zip(path, path[1:]):
        for neighbor, cost in graph.adj[a]:
            if neighbor == b:
                total_cost += cost
                break
    return SearchResult(path, total_cost, order)

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": uniform_cost_search,
    "Greedy": greedy_best_first,
    "A*": a_star_search,
    "Best-First": best_first_search
}

# -------------------------
# PyQt UI 
# -------------------------
class CampusNavAppPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COMSATS Campus Navigation")
        self.setGeometry(100, 100, 1200, 760)
        self.graph = Graph(DEFAULT_MAP)
        self.nodes = self.graph.nodes()
        self.current_path = []
        self.scale = 1.0
        self.setup_ui()
        self._compute_positions()
        self.draw_map()
        self.center_view()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #007bff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #dee2e6;
                border-left-style: solid;
            }
            QPushButton {
                padding: 10px 15px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QLabel {
                font-weight: bold;
                color: #495057;
                margin-top: 8px;
                margin-bottom: 4px;
            }
            QFrame {
                border-radius: 6px;
                padding: 8px;
            }
        """)

        # Left panel (controls)
        left_panel = QWidget()
        left_panel.setFixedWidth(380)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-right: 1px solid #dee2e6;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(8)

        # Header 
        header = QLabel("COMSATS Campus Navigation")
        header.setStyleSheet("""
            QLabel {
                background-color: #1e3a8a;
                color: white;
                padding: 15px;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(header)

        def create_section(title):
            section_label = QLabel(title)
            section_label.setStyleSheet("""
                QLabel {
                    color: #1e3a8a;
                    font-size: 13px;
                    font-weight: bold;
                    margin-top: 15px;
                    margin-bottom: 5px;
                    padding-bottom: 5px;
                    border-bottom: 2px solid #1e3a8a;
                }
            """)
            return section_label

        # Navigation Section
        left_layout.addWidget(create_section("NAVIGATION"))
        
        left_layout.addWidget(QLabel("Start Location"))
        self.start_combo = QComboBox()
        self.start_combo.addItems(self.nodes)
        self.start_combo.setStyleSheet("margin-bottom: 10px;")
        left_layout.addWidget(self.start_combo)

        left_layout.addWidget(QLabel("Destination"))
        self.goal_combo = QComboBox()
        self.goal_combo.addItems(self.nodes)
        self.goal_combo.setCurrentIndex(1 if len(self.nodes) > 1 else 0)
        left_layout.addWidget(self.goal_combo)

        left_layout.addWidget(QLabel("Pathfinding Algorithm"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(list(ALGORITHMS.keys()) + ["COMPARE ALL"])
        left_layout.addWidget(self.algo_combo)

        # Action buttons
        button_layout = QHBoxLayout()
        self.find_path_btn = QPushButton("📍 Find Path")
        self.find_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        self.compare_btn = QPushButton("📊 Compare All")
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
        """)
        
        button_layout.addWidget(self.find_path_btn)
        button_layout.addWidget(self.compare_btn)
        left_layout.addLayout(button_layout)

        # Emergency Section
        left_layout.addWidget(create_section("EMERGENCY MODE"))

        left_layout.addWidget(QLabel("Emergency Algorithm"))
        self.emergency_algo_combo = QComboBox()
        self.emergency_algo_combo.addItems(["A*", "UCS"])
        self.emergency_algo_combo.setCurrentText("A*")
        left_layout.addWidget(self.emergency_algo_combo)

        em_button_layout = QVBoxLayout()

        self.fire_btn = QPushButton("🔥 Fire Emergency Exit")
        self.hungry_btn = QPushButton("🍕 I'm Hungry\n") 
        self.health_btn = QPushButton("🏥 Health Emergency\n")

        button_style = """
            QPushButton {
                background-color: %s;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 12px 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: %s;
            }
        """

        self.fire_btn.setStyleSheet(button_style % ("#d32f2f", "#c62828"))
        self.hungry_btn.setStyleSheet(button_style % ("#ff9800", "#f57c00")) 
        self.health_btn.setStyleSheet(button_style % ("#1976d2", "#1565c0"))

        for btn in [self.fire_btn, self.hungry_btn, self.health_btn]:
            btn.setFixedHeight(50)
            btn.setStyleSheet(btn.styleSheet() + " text-align: center;")

        em_button_layout.addWidget(self.fire_btn)
        em_button_layout.addWidget(self.hungry_btn)
        em_button_layout.addWidget(self.health_btn)
        left_layout.addLayout(em_button_layout)

        # Results Section 
        left_layout.addWidget(create_section("RESULTS"))
        left_layout.addWidget(QLabel("Path Details & Visited Nodes"))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)  
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                background-color: #f8f9fa;
            }
            QScrollArea > QWidget > QWidget { 
                background-color: #f8f9fa; 
            }
        """)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: none;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 10px;
                line-height: 1.4;
            }
        """)

        self.info_text.setMinimumHeight(300)

        self.info_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        scroll_area.setWidget(self.info_text)
        left_layout.addWidget(scroll_area)

        left_layout.addStretch()


        # Right panel 
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-left: 1px solid #dee2e6;
            }
            QGraphicsView {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)

        # Map view
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)  
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)  
        self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.graphics_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(self.graphics_view, 4) 



        # Map Legend 
        legend_frame = QFrame()
        legend_frame.setFrameStyle(QFrame.Box)
        legend_frame.setFixedSize(320, 200)  
        legend_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        legend_layout = QVBoxLayout(legend_frame)
        legend_layout.setSpacing(6)

        legend_title = QLabel("🗺️ MAP LEGEND")
        legend_title.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px; margin-bottom: 4px;")
        legend_title.setAlignment(Qt.AlignCenter)
        legend_layout.addWidget(legend_title)

        legend_items = [
            ("🟢 Dark Green", "Start Location"),
            ("🔴 Red", "Destination"), 
            ("🟠 Orange", "Path Nodes"),
            ("🔵 Blue/Teal", "Academic & Gates"),
            ("🟣 Purple", "Hostels"),
            ("━━━━", "Selected Route (Thick Teal)"),
            ("────", "Available Roads (Thin Grey)")
        ]

        for color, description in legend_items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(10)  
            
            color_label = QLabel(color)
            color_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #2c3e50;")
            color_label.setFixedWidth(100) 
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 11px; color: #495057;")
            
            item_layout.addWidget(color_label)
            item_layout.addWidget(desc_label)
            item_layout.addStretch()
            legend_layout.addLayout(item_layout)

        legend_layout.addStretch()
        right_layout.addWidget(legend_frame)  

        detail_label = QLabel("Green=Start, Red=Goal, Orange=Path, Teal=Route, Grey=Roads")
        detail_label.setStyleSheet("font-size: 9px; color: #6c757d; font-style: italic; margin-top: 4px;")
        detail_label.setAlignment(Qt.AlignCenter)
        legend_layout.addWidget(detail_label)

        legend_layout.addStretch()
        right_layout.addWidget(legend_frame, 1)  

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # signals
        self.find_path_btn.clicked.connect(self.run_search)
        self.compare_btn.clicked.connect(self.compare_all)
        self.fire_btn.clicked.connect(self.handle_fire_emergency)
        self.hungry_btn.clicked.connect(self.handle_hungry_emergency)
        self.health_btn.clicked.connect(self.handle_health_emergency)

        #background
        self.load_background()

    def load_background(self):
        try:
            self.background_pixmap = QPixmap(BACKGROUND_PATH)
            if not self.background_pixmap.isNull():
                self.scale = 0.8 
                
                scaled_pixmap = self.background_pixmap.scaled(
                    int(self.background_pixmap.width() * self.scale),
                    int(self.background_pixmap.height() * self.scale),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.background_item = QGraphicsPixmapItem(scaled_pixmap)
                self.scene.addItem(self.background_item)
                self.img_w = scaled_pixmap.width()
                self.img_h = scaled_pixmap.height()
                
                padding = 50
                self.scene.setSceneRect(-padding, -padding, 
                                       self.img_w + 2*padding, 
                                       self.img_h + 2*padding)
            else:
                self.setup_fallback_background()
        except Exception as e:
            print(f"Error loading background: {e}")
            self.setup_fallback_background()

    def setup_fallback_background(self):
        self.scale = 0.8
        self.img_w = int(DESIGN_W * self.scale)
        self.img_h = int(DESIGN_H * self.scale)
        self.background_item = QGraphicsRectItem(0, 0, self.img_w, self.img_h)
        self.background_item.setBrush(QBrush(QColor("#eaf6ef")))
        self.background_item.setPen(QPen(Qt.NoPen))
        self.scene.addItem(self.background_item)
        padding = 50
        self.scene.setSceneRect(-padding, -padding, 
                               self.img_w + 2*padding, 
                               self.img_h + 2*padding)

    def _compute_positions(self):
        self.positions = {}
        for b in DEFAULT_MAP["buildings"]:
            sx = int(b["x"] * self.scale)
            sy = int(b["y"] * self.scale)
            self.positions[b["id"]] = (sx, sy)
        for n in list(self.graph.positions.keys()):
            if n in self.positions:
                self.graph.positions[n] = self.positions[n]

    def center_view(self):
        """Fit the entire scene in the view with proper margins"""
        if hasattr(self, 'scene'):
            scene_rect = self.scene.itemsBoundingRect()
            
            margin = 50
            scene_rect_adjusted = scene_rect.adjusted(-margin, -margin, margin, margin)
            
            self.graphics_view.fitInView(scene_rect_adjusted, Qt.KeepAspectRatio)
            
            self.graphics_view.update()

    def resizeEvent(self, event):
        """Handle window resize to keep the view centered"""
        super().resizeEvent(event)
        QTimer.singleShot(50, self.center_view)

    def showEvent(self, event):
        """Handle initial show to ensure proper centering"""
        super().showEvent(event)
        QTimer.singleShot(100, self.center_view)

    # -------------------------
    # search runner 
    # -------------------------
    def run_search(self):
        start = self.start_combo.currentText(); goal = self.goal_combo.currentText()
        if start == goal:
            self._log("Start and goal are the same."); return
        algo = self.algo_combo.currentText()
        if algo == "COMPARE ALL":
            self.compare_all(); return
        result = ALGORITHMS[algo](self.graph, start, goal)
        if not result.path:
            self._log("No path found.")
        else:
            info = f"Algorithm: {algo}\nCost: {result.cost:.2f}\nPath: {' → '.join(result.path)}\nVisited: {', '.join(result.visited)}"
            self._log(info)
        self.current_path = result.path; self.draw_map()

    def show_comparison_graphs(self, results):
        """Display matplotlib graphs comparing algorithm performance"""
        self.graph_window = QMainWindow()
        self.graph_window.setWindowTitle("Algorithm Comparison Graphs")
        self.graph_window.setGeometry(200, 200, 1000, 600)
        notebook = QTabWidget(); self.graph_window.setCentralWidget(notebook)
        valid_results = [(name, result) for name, result in results if result.path]
        if not valid_results:
            no_data_label = QLabel("No valid paths found to compare"); no_data_label.setAlignment(Qt.AlignCenter)
            self.graph_window.setCentralWidget(no_data_label); self.graph_window.show(); return
        algorithms = [name for name, _ in valid_results]; costs = [result.cost for _, result in valid_results]
        path_lengths = [len(result.path) for _, result in valid_results]; visited_counts = [len(result.visited) for _, result in valid_results]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

        # Cost Comparison
        cost_widget = QWidget(); cost_layout = QVBoxLayout(cost_widget)
        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        bars1 = ax1.bar(algorithms, costs, color=colors[:len(algorithms)], alpha=0.7)
        ax1.set_title('Path Cost Comparison', fontsize=14, fontweight='bold'); ax1.set_ylabel('Cost')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        for bar in bars1:
            height = bar.get_height(); ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}', ha='center', va='bottom')
        ax2.pie(costs, labels=algorithms, autopct='%1.1f%%', colors=colors[:len(algorithms)]); ax2.set_title('Cost Distribution', fontsize=14, fontweight='bold')
        plt.tight_layout(); canvas1 = FigureCanvas(fig1); cost_layout.addWidget(canvas1); notebook.addTab(cost_widget, "Cost Comparison")

        # Efficiency Comparison
        efficiency_widget = QWidget(); efficiency_layout = QVBoxLayout(efficiency_widget)
        fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        bars1 = ax1.bar(algorithms, path_lengths, color=colors[:len(algorithms)], alpha=0.7)
        ax1.set_title('Path Length (Nodes)', fontsize=14, fontweight='bold'); ax1.set_ylabel('Number of Nodes')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        for bar in bars1:
            height = bar.get_height(); ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height}', ha='center', va='bottom')
        bars2 = ax2.bar(algorithms, visited_counts, color=colors[:len(algorithms)], alpha=0.7)
        ax2.set_title('Nodes Visited', fontsize=14, fontweight='bold'); ax2.set_ylabel('Number of Nodes')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        for bar in bars2:
            height = bar.get_height(); ax2.text(bar.get_x() + bar.get_width()/2., height, f'{height}', ha='center', va='bottom')
        plt.tight_layout(); canvas2 = FigureCanvas(fig2); efficiency_layout.addWidget(canvas2); notebook.addTab(efficiency_widget, "Efficiency")
        self.graph_window.show()

    def compare_all(self):
        start = self.start_combo.currentText(); goal = self.goal_combo.currentText()
        if start == goal:
            self._log("Start and goal are the same."); return
        comparison_text = "🧭 ALGORITHM COMPARISON 🧭\n" + "="*40 + f"\nRoute: {start} → {goal}\n\n"
        results = []
        for algo_name, algo_func in ALGORITHMS.items():
            result = algo_func(self.graph, start, goal); results.append((algo_name, result))
            if result.path:
                comparison_text += f"📊 {algo_name}:\n   • Cost: {result.cost:.1f}\n   • Path Length: {len(result.path)}\n   • Nodes Visited: {len(result.visited)}\n   • Path: {' → '.join(result.path)}\n\n"
            else:
                comparison_text += f"❌ {algo_name}: NO PATH FOUND\n\n"
        if any(result.path for _, result in results):
            valid_results = [(name, result) for name, result in results if result.path]
            best_cost = min(result.cost for _, result in valid_results)
            best_algorithms = [name for name, result in valid_results if result.cost == best_cost]
            shortest_path = min(len(result.path) for _, result in valid_results)
            shortest_algorithms = [name for name, result in valid_results if len(result.path) == shortest_path]
            fewest_visited = min(len(result.visited) for _, result in valid_results)
            efficient_algorithms = [name for name, result in valid_results if len(result.visited) == fewest_visited]
            comparison_text += "🏆 PERFORMANCE SUMMARY 🏆\n" + "="*40 + f"\n💰 Best Cost ({best_cost:.1f}): {', '.join(best_algorithms)}\n📐 Shortest Path ({shortest_path} nodes): {', '.join(shortest_algorithms)}\n⚡ Most Efficient ({fewest_visited} visited): {', '.join(efficient_algorithms)}\n\n"
            comparison_text += "🔍 ALGORITHM CATEGORIES\n" + "="*40 + "\n• Uninformed: BFS, DFS\n• Cost-based: UCS\n• Heuristic: Greedy, Best-First\n• Optimal: A*, UCS\n"
        self._log(comparison_text)
        self.show_comparison_graphs(results)
        for algo_name, result in results:
            if result.path:
                self.current_path = result.path; break
        else:
            self.current_path = []
        self.draw_map()

    def _log(self, text):
        self.info_text.setPlainText(text)

    # -------------------------
    # Emergency helpers
    # -------------------------
    def _choose_emergency_algo(self):
        choice = self.emergency_algo_combo.currentText()
        if choice == "A*":
            return "A*"
        elif choice == "UCS":
            return "UCS"
        return "A*"

    def _nearest_node_by_euclid(self, start_node, candidates):
        """Return the candidate nearest in straight-line distance from start_node."""
        if start_node not in self.graph.positions:
            return None
        sx, sy = self.graph.positions[start_node]
        best = None
        bestd = float("inf")
        for c in candidates:
            if c not in self.graph.positions:
                continue
            cx, cy = self.graph.positions[c]
            d = math.hypot(cx - sx, cy - sy)
            if d < bestd:
                bestd = d
                best = c
        return best

    def _run_emergency_route(self, target, reason_label):
        """Run chosen algorithm from current start to target and display/log results."""
        start = self.start_combo.currentText()
        if start == target:
            self._log(f"{reason_label}: You are already at {target}.")
            return
        algo_name = self._choose_emergency_algo()
        algo_func = ALGORITHMS.get(algo_name, ALGORITHMS["A*"])
        result = algo_func(self.graph, start, target)
        if not result.path:
            self._log(f"{reason_label}: No path found from {start} → {target} using {algo_name}.")
            self.current_path = []
        else:
            info = (f"{reason_label} — Algorithm: {algo_name}\n"
                    f"Target: {target}\n"
                    f"Cost: {result.cost:.2f}\n"
                    f"Path: {' → '.join(result.path)}\n"
                    f"Visited: {', '.join(result.visited)}")
            self._log(info)
            self.current_path = result.path
        self.draw_map()

    def handle_fire_emergency(self):
        """Find nearest gate and route user to it."""
        start = self.start_combo.currentText()
        gate_candidates = [n for n in self.graph.nodes() if "Gate" in n]
        if not gate_candidates:
            self._log("Fire Emergency: No gates defined in map.")
            return
        nearest_gate = self._nearest_node_by_euclid(start, gate_candidates)
        if not nearest_gate:
            self._log("Fire Emergency: Unable to determine nearest gate.")
            return
        self._run_emergency_route(nearest_gate, "FIRE EMERGENCY (escape to nearest gate)")

    def handle_hungry_emergency(self):
        """Choose Cheezious or Student Cafeteria — pick nearest by euclidean distance."""
        start = self.start_combo.currentText()
        food_candidates = []
        for name in ("Cheezious", "Student Cafeteria"):
            if name in self.graph.positions:
                food_candidates.append(name)
        if not food_candidates:
            self._log("Hungry: No food locations defined.")
            return
        target = self._nearest_node_by_euclid(start, food_candidates)
        if not target:
            self._log("Hungry: Unable to determine nearest food location.")
            return
        self._run_emergency_route(target, "HUNGER (go to nearest food place)")

    def handle_health_emergency(self):
        """Route to Medical Center (shortest path)."""
        if "Medical Center" not in self.graph.positions:
            self._log("Health Emergency: Medical Center not found on map.")
            return
        self._run_emergency_route("Medical Center", "HEALTH EMERGENCY (go to Medical Center)")

    # -------------------------
    # map drawing
    # -------------------------
    def draw_map(self):
        for item in self.scene.items():
            if hasattr(self, "background_item") and item == self.background_item:
                continue
            self.scene.removeItem(item)

        path_edges = set()
        if len(self.current_path) >= 2:
            for a, b in zip(self.current_path, self.current_path[1:]):
                path_edges.add(frozenset((a, b)))

        # base edges
        for a, b, cost in self.graph.edges():
            x1, y1 = self.graph.positions[a]
            x2, y2 = self.graph.positions[b]
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(QPen(QColor("#3f4b4f"), 2))
            self.scene.addItem(line)

        # current path thicker
        if len(self.current_path) >= 2:
            for a, b in zip(self.current_path, self.current_path[1:]):
                x1, y1 = self.graph.positions[a]
                x2, y2 = self.graph.positions[b]
                line = QGraphicsLineItem(x1, y1, x2, y2)
                line.setPen(QPen(QColor("#00796b"), 5))
                self.scene.addItem(line)

        # edge cost labels 
        for a, b, cost in self.graph.edges():
            if frozenset((a, b)) in path_edges:
                continue
            x1, y1 = self.graph.positions[a]
            x2, y2 = self.graph.positions[b]
            mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L, dx / L
            offset = 16 * self.scale
            lx, ly = mx + nx * offset, my + ny * offset

            # cost label
            cost_text = QGraphicsTextItem(str(cost))
            cost_text.setPos(lx - 10, ly - 8)
            cost_text.setDefaultTextColor(QColor("#000000"))
            cost_text.setFont(QFont("Helvetica", int(10 * self.scale), QFont.Bold))
            self.scene.addItem(cost_text)

        # nodes
        start_node = self.start_combo.currentText()
        goal_node = self.goal_combo.currentText()

        for node, (x, y) in self.graph.positions.items():
            if node == start_node:
                color = QColor("#2e7d32"); outline = QColor("#ffffff")
            elif node == goal_node:
                color = QColor("#c62828"); outline = QColor("#ffffff")
            elif node in self.current_path:
                color = QColor("#ffb74d"); outline = QColor("#5d4037")
            elif "Gate" in node:
                color = QColor("#009688"); outline = QColor("#ffffff")
            elif node.startswith("Hostel") or node == "Hostel City Hub":
                color = QColor("#6a1b9a"); outline = QColor("#ffffff")
            elif node == "Cheezious":
                color = QColor("#ff5722"); outline = QColor("#ffffff")
            else:
                color = QColor("#1e88e5"); outline = QColor("#ffffff")

            # node circle
            r = 16 * self.scale
            circle = QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
            circle.setBrush(QBrush(color))
            circle.setPen(QPen(outline, 2))
            self.scene.addItem(circle)

            # node label
            label = QGraphicsTextItem(node)
            label_width = len(node) * 7 * self.scale
            label.setPos(x - label_width / 2, y + 18 * self.scale)
            label.setDefaultTextColor(QColor("#000000"))
            label.setFont(QFont("Helvetica", int(11 * self.scale), QFont.Bold))
            self.scene.addItem(label)

        self.center_view()

# -------------------------
# Run
# -------------------------
def main():
    app = QApplication(sys.argv)
    window = CampusNavAppPyQt()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()