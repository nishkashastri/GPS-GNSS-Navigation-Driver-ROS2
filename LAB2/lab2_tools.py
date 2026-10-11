"""
lab2_tools.py - helper functions for LAB 2 (provided, no need to edit).

Conventions used everywhere in this file:
  * A set of points is an (N, 2) array: column 0 is x (m), column 1 is y (m), as seen by the robot
    (x points forward from the robot, y points to its left).
  * A motion is delta = [dx, dy, dtheta] in metres, metres and RADIANS: how far the robot moved forward (dx)
    and to its left (dy), and how much it turned (dtheta, counter-clockwise positive), measured from where
    it took scan A.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_scan(name):
    """Read one lidar scan from data/<name>.

    Returns (angles, ranges): for every beam, its direction in the robot frame (rad, 0 = straight
    ahead, counter-clockwise positive) and the distance it measured (m). A range of inf means the
    beam got no return (as in a ROS LaserScan message). Beam number k is row k.
    """
    d = np.genfromtxt(DATA_DIR / name, delimiter=",", names=True)
    return d["angle_rad"], d["range_m"]


def load_static_scans():
    """Read data/static_scans.csv: 100 scans taken while the robot stood still at the place where it took scan A.

    Returns (angles, ranges) where angles has shape (720,) and ranges has shape (100, 720):
    row i is scan i, column k is beam k. A range of inf means no return.
    """
    ranges = np.loadtxt(DATA_DIR / "static_scans.csv", delimiter=",")
    angles = np.deg2rad(0.5 * np.arange(ranges.shape[1]))
    return angles, ranges


def load_pairs(name):
    """Read a file of paired points from data/<name> (columns x_A, y_A, x_B, y_B).

    Returns (PA, PB), two (N, 2) arrays: row j of PA (a point in scan A's frame) and row j of PB
    (a point in scan B's frame) are claimed to be the same physical spot.
    """
    d = np.genfromtxt(DATA_DIR / name, delimiter=",", names=True)
    return np.column_stack([d["x_A"], d["y_A"]]), np.column_stack([d["x_B"], d["y_B"]])


def show_scan(P, title="", marks=None, zoom=None):
    """Plot a scan P (N, 2) in its own robot frame.

    marks : (K, 2) array of extra points to draw on top, e.g. the points of a pair
    zoom  : (xmin, xmax, ymin, ymax) to look closely at one area, e.g. zoom=(3, 5, -1, 1)
    """
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.scatter(P[:, 0], P[:, 1], s=4, color="0.55", label="lidar points")
    ax.plot(0, 0, "k>", ms=11, label="robot (faces +x)")
    if marks is not None:
        marks = np.asarray(marks).reshape(-1, 2)
        ax.scatter(marks[:, 0], marks[:, 1], s=110, marker="X", color="C1", zorder=3, label="marked points")
    if zoom is not None:
        ax.set_xlim(zoom[0], zoom[1])
        ax.set_ylim(zoom[2], zoom[3])
    ax.set(title=title, xlabel="x (m)", ylabel="y (m)", aspect="equal")
    ax.legend(loc="upper right", fontsize=8)
    plt.show()


def transform(P, delta):
    """The motion model. Points P (N, 2) seen in scan B -> where scan A sees them,
    if the robot moved by delta = [dx, dy, dtheta] between scan A and scan B. Returns an (N, 2) array.

    For each point (x, y):   x_new = cos(dtheta) * x - sin(dtheta) * y + dx
                             y_new = sin(dtheta) * x + cos(dtheta) * y + dy
    """
    c, s = np.cos(delta[2]), np.sin(delta[2])
    R = np.array([[c, -s], [s, c]])
    return np.asarray(P) @ R.T + np.asarray(delta[:2])


def transform_derivatives(P, delta):
    """Partial derivatives of transform(P, delta) with respect to dx, dy and dtheta.

    Returns D with shape (3, N, 2): D[k] is how fast every moved point changes when you nudge
    parameter k of delta (k = 0: dx, 1: dy, 2: dtheta), i.e. d transform(P, delta) / d delta[k].
    """
    P = np.asarray(P, dtype=float)
    c, s = np.cos(delta[2]), np.sin(delta[2])
    D = np.zeros((3, len(P), 2))
    D[0, :, 0] = 1.0                                   # moving dx shifts every point along x
    D[1, :, 1] = 1.0                                   # moving dy shifts every point along y
    D[2, :, 0] = -s * P[:, 0] - c * P[:, 1]            # turning moves each point sideways,
    D[2, :, 1] = c * P[:, 0] - s * P[:, 1]             # more for points that are far away
    return D


def show_alignment(SA, SB, delta, title=""):
    """Overlay scan A (SA) and scan B (SB) moved with delta. A good delta puts the walls on top of each other."""
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    ax.scatter(SA[:, 0], SA[:, 1], s=3, label="scan A")
    moved = transform(SB, delta)
    ax.scatter(moved[:, 0], moved[:, 1], s=3, label="scan B, moved with delta")
    ax.set(title=title, xlabel="x (m)", ylabel="y (m)", aspect="equal")
    ax.legend(loc="upper right", fontsize=8)
    plt.show()


def match_nearest(P1, Q):
    """For every point Q[j], find the closest point in P1.

    Returns idx (index into P1 for each row of Q) and dist (distance to it, m).
    Afterwards P1[idx] lines up row by row with Q.
    """
    D = np.linalg.norm(np.asarray(Q)[:, None, :] - np.asarray(P1)[None, :, :], axis=2)
    idx = D.argmin(axis=1)
    return idx, D[np.arange(len(Q)), idx]
