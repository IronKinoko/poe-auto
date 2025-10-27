from src.utils import common

common.DEBUG = True


from src.core.screen import _find_template_in_pil
from src.utils.common import load_img, project_path


def test_find_template_in_pil():
    source = load_img("/test/fixtures/source.png")
    img1 = load_img("/test/fixtures/map16_clip.png")
    img2 = load_img("/test/fixtures/map16_deli_clip.png")

    result = _find_template_in_pil(
        source, img1, threshold=0.9, debug_out=project_path("tmp/tmp1.png")
    )
    assert result is not None
    result = _find_template_in_pil(
        source, img2, threshold=0.9, debug_out=project_path("tmp/tmp2.png")
    )
    assert result is None
