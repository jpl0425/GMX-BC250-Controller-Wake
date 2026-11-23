"""Small numpy z-buffer renderer (orthographic) for clear part pictures."""
import numpy as np
from PIL import Image


def look(elev, azim):
    """camera direction (from scene to camera) and up vector."""
    e, a = np.radians(elev), np.radians(azim)
    d = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    up = np.array([0, 0, 1.0]) if abs(elev) < 89 else np.array([-np.cos(a + np.pi), -np.sin(a + np.pi), 0])
    return d, up


def render(meshes, W=1400, H=1000, view=None, cam=None, light=(0.4, -0.5, 0.8), pad=0.06, bg=(255, 255, 255), outline=True):
    """meshes: list of (trimesh, rgb tuple 0-1). cam: (right, up, toward_camera) unit vectors."""
    right, upv, fwd = [np.asarray(v, float) / np.linalg.norm(v) for v in cam]
    L = np.asarray(light, float); L /= np.linalg.norm(L)
    allv = np.vstack([m.vertices for m, _ in meshes])
    sx, sy = allv @ right, allv @ upv
    span = max((sx.max() - sx.min()) / W, (sy.max() - sy.min()) / H) * (1 + 2 * pad)
    cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2
    zbuf = np.full((H, W), -np.inf); img = np.zeros((H, W, 3)); img[:] = np.array(bg) / 255
    nbuf = np.zeros((H, W), int) - 1
    oid = 0
    for m, col in meshes:
        V = m.vertices; F = m.faces; N = m.face_normals
        px = (V @ right - cx) / span + W / 2
        py = H / 2 - (V @ upv - cy) / span
        pz = V @ fwd
        shade = 0.30 + 0.55 * np.clip(N @ L, 0, 1) + 0.15 * np.clip(N @ fwd, 0, 1)
        c = np.asarray(col)
        for i, f in enumerate(F):
            if N[i] @ fwd < -1e-6:
                continue
            x, y, z = px[f], py[f], pz[f]
            x0, x1 = int(max(np.floor(x.min()), 0)), int(min(np.ceil(x.max()), W - 1))
            y0, y1 = int(max(np.floor(y.min()), 0)), int(min(np.ceil(y.max()), H - 1))
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(d) < 1e-12:
                continue
            w0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
            w1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
            w2 = 1 - w0 - w1
            ins = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not ins.any():
                continue
            zz = w0 * z[0] + w1 * z[1] + w2 * z[2]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            upd = ins & (zz > sub + 1e-6)
            sub[upd] = zz[upd]
            img[y0:y1 + 1, x0:x1 + 1][upd] = np.clip(c * shade[i], 0, 1)
            nbuf[y0:y1 + 1, x0:x1 + 1][upd] = oid * 1000000 + i
        oid += 1
    if outline:
        # dark lines where depth jumps (edges of holes, letters, part outlines)
        z = np.where(np.isfinite(zbuf), zbuf, zbuf[np.isfinite(zbuf)].min() - 50)
        dz = np.zeros_like(z)
        dz[:, 1:] = np.maximum(dz[:, 1:], np.abs(np.diff(z, axis=1)))
        dz[1:, :] = np.maximum(dz[1:, :], np.abs(np.diff(z, axis=0)))
        edge = dz > 0.25
        img[edge] *= 0.25
    return Image.fromarray((img * 255).astype(np.uint8))
