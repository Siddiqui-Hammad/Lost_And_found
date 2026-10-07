from typing import Optional

class ImageMatcher:
    """
    Modular CLIP Embeddings Image Matching Interface.
    Prepared for future multi-modal vision model integration without
    altering core scoring architecture.
    """
    def __init__(self):
        self.is_available = False

    def compute_image_similarity(self, img_url1: Optional[str], img_url2: Optional[str]) -> Optional[float]:
        # For initial MVP release, return None so scoring operates gracefully on text & metadata
        if not img_url1 or not img_url2:
            return None
        return None

image_matcher = ImageMatcher()
