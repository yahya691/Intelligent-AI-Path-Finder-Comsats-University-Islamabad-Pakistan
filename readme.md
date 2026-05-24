# COMSATS Navigation System

The **COMSATS Navigation System** is an AI-powered pathfinding application developed during the fourth semester of undergraduate studies. The project implements classic artificial intelligence search algorithms to determine the most efficient routes between different points within the COMSATS University Islamabad campus.

## Project Overview

This project applies foundational AI pathfinding algorithms to map out university buildings and areas, helping students and visitors navigate the campus efficiently.

* **Core Algorithms**: Implements **A* Search** and **Dijkstra’s Algorithm** to calculate optimal paths.
* **Problem Domain**: Campus navigation; converting physical campus geography into a weighted graph for automated traversal.
* **Goal**: To compare algorithm efficiency in pathfinding and provide a reliable tool for automated campus route guidance.

## Key Functionalities

* **Graph-Based Modeling**: Represents the campus layout as nodes (locations) and edges (paths), with edge weights corresponding to distance/time.
* **Algorithm Comparison**: Offers a side-by-side comparison of how A* and Dijkstra perform in finding the shortest path from a starting point to a destination.
* **Efficiency Analysis**: Documents the search process and highlights the performance benefits of using heuristic-driven search (A*) over blind search (Dijkstra) in a spatial environment.

## Technical Specifications

* **Language**: Python (`CAMPUS.FINAL.py`)

## How to Run

1. **Requirements**: Ensure you have Python 3.x installed.
2. **Execution**:
```bash
python CAMPUS.FINAL.py

```


3. **Usage**: Follow the console prompts to input your starting location and destination to view the calculated optimal route.

## Project Structure

* `CAMPUS.FINAL.py`: The main source code containing the graph implementation and search logic.
* `README.md`: This documentation.
