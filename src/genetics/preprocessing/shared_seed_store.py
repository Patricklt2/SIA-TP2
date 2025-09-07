from multiprocessing import Manager
from typing import Iterable, Tuple, Dict, Any


def create_shared_seed_store(seeds: Iterable) -> Tuple[Any, Dict]:
    """Create a multiprocessing.Manager and a shared dict populated with seeds.

    seeds: iterable of objects with attributes .id and .bbox/.mean_color/.mse OR mappings with those keys.

    Returns (manager, shared_dict) where shared_dict maps tile_id -> simple dict with keys: bbox, centroid, mean_color, mse, pixel_count
    """
    mgr = Manager()
    shared = mgr.dict()

    for s in seeds:
        tid = None
        bbox = None
        centroid = None
        mean_color = None
        mse = None
        pixel_count = None

        # try attribute access first
        if hasattr(s, 'id'):
            tid = getattr(s, 'id')
        if hasattr(s, 'bbox'):
            bbox = getattr(s, 'bbox')
        if hasattr(s, 'centroid'):
            centroid = getattr(s, 'centroid')
        if hasattr(s, 'mean_color'):
            mean_color = getattr(s, 'mean_color')
        if hasattr(s, 'mse'):
            mse = getattr(s, 'mse')
        if hasattr(s, 'pixel_count'):
            pixel_count = getattr(s, 'pixel_count')

        # fallback to mapping-style access
        if tid is None and isinstance(s, dict):
            tid = s.get('id')
        if bbox is None and isinstance(s, dict):
            bbox = s.get('bbox')
        if centroid is None and isinstance(s, dict):
            centroid = s.get('centroid')
        if mean_color is None and isinstance(s, dict):
            mean_color = s.get('mean_color')
        if mse is None and isinstance(s, dict):
            mse = s.get('mse')
        if pixel_count is None and isinstance(s, dict):
            pixel_count = s.get('pixel_count')

        if tid is None:
            continue

        shared[tid] = {
            'bbox': tuple(bbox) if bbox is not None else None,
            'centroid': tuple(centroid) if centroid is not None else None,
            'mean_color': mean_color,
            'mse': float(mse) if mse is not None else None,
            'pixel_count': int(pixel_count) if pixel_count is not None else None,
        }

    return mgr, shared


def update_seed_if_better(shared_dict: Dict, tile_id: int, candidate_color: Any, candidate_mse: float, min_improvement_frac: float = 0.01) -> bool:
    """Atomically update a seed in shared_dict if candidate_mse is sufficiently better.

    Returns True if updated, False otherwise.
    """
    cur = shared_dict.get(tile_id)
    if cur is None:
        # if absent, set it
        shared_dict[tile_id] = {
            'bbox': None,
            'centroid': None,
            'mean_color': candidate_color,
            'mse': float(candidate_mse),
            'pixel_count': None,
        }
        return True

    cur_mse = cur.get('mse')
    # if current mse is None, accept
    if cur_mse is None or float(candidate_mse) < float(cur_mse) * (1.0 - float(min_improvement_frac)):
        # update entry
        shared_dict[tile_id] = {
            'bbox': cur.get('bbox'),
            'centroid': cur.get('centroid'),
            'mean_color': candidate_color,
            'mse': float(candidate_mse),
            'pixel_count': cur.get('pixel_count')
        }
        return True

    return False


def find_seed_by_point(shared_dict: Dict, x: int, y: int):
    """Find a seed (tile_id, seed_dict) whose bbox contains point (x,y). Returns None if not found."""
    for tid, sd in shared_dict.items():
        bbox = sd.get('bbox')
        if not bbox:
            continue
        x0, y0, x1, y1 = bbox
        if x0 <= x < x1 and y0 <= y < y1:
            return tid, sd
    return None
