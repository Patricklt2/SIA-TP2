import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TileSeed:
    id: int
    bbox: Tuple[int, int, int, int]  # x0, y0, x1, y1
    centroid: Tuple[int, int]
    mean_color: str  # hex color '#rrggbb'
    mse: float
    pixel_count: int


def compute_tile_seeds(target_array: np.ndarray, tile_size: int) -> List[TileSeed]:
    """Compute mean-color seeds for non-overlapping square tiles.

    Returns a list of TileSeed objects with bbox, centroid, mean_color (hex) and mse.
    """
    h, w = target_array.shape[:2]
    seeds = []
    tid = 0

    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            x1 = min(x + tile_size, w)
            y1 = min(y + tile_size, h)
            patch = target_array[y:y1, x:x1]
            if patch.size == 0:
                continue

            # compute mean color per channel
            if patch.ndim == 3 and patch.shape[2] >= 3:
                pixels = patch.reshape(-1, patch.shape[2])[:, :3]
                mean_col = np.mean(pixels, axis=0).astype(int)
            else:
                # grayscale
                pixels = patch.reshape(-1)
                mv = int(np.mean(pixels))
                mean_col = np.array([mv, mv, mv], dtype=int)

            # mse of flat color
            mse = np.mean((pixels.astype(np.float32) - mean_col.astype(np.float32)) ** 2)

            hex_color = '#{:02x}{:02x}{:02x}'.format(int(mean_col[0]), int(mean_col[1]), int(mean_col[2]))

            seeds.append(TileSeed(
                id=tid,
                bbox=(x, y, x1, y1),
                centroid=((x + x1) // 2, (y + y1) // 2),
                mean_color=hex_color,
                mse=float(mse),
                pixel_count=pixels.shape[0]
            ))
            tid += 1

    return seeds
