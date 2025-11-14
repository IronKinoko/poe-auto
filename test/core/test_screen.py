from src.core.screen import _find_template_in_pil
from src.utils.common import load_img, project_path


def test_find_template_in_pil():
    source = load_img("/test/fixtures/bag_map.png")
    img1 = load_img("/test/fixtures/bag_map_capture.png")

    result = _find_template_in_pil(source, img1, debug_out=project_path("tmp/map.png"))
    assert result is not None

    source = load_img("/test/fixtures/bag_deli.png")
    img1 = load_img("/test/fixtures/bag_deli_capture.png")
    result = _find_template_in_pil(source, img1, debug_out=project_path("tmp/deli.png"))
    assert result is not None


def test_same_shape_different_color():
    img3 = load_img("/test/fixtures/deli_t9.png")
    img4 = load_img("/test/fixtures/deli_t10.png")

    result = _find_template_in_pil(
        img3, img4, debug_out=project_path("tmp/test_same_shape_different_color.png")
    )
    assert result is None
