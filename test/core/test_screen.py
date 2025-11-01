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


def test_same_template_return_same_position():
    source = load_img("/test/fixtures/source.png")
    img1 = load_img("/test/fixtures/map16_clip.png")

    result1 = _find_template_in_pil(
        source, img1, threshold=0.9, debug_out=project_path("tmp/tmp3.png")
    )
    result2 = _find_template_in_pil(
        source, img1, threshold=0.9, debug_out=project_path("tmp/tmp4.png")
    )
    assert result1 == result2


def test_same_shape_different_color():
    img1 = load_img("/test/fixtures/map16_clip.png")
    img2 = load_img("/test/fixtures/map16_deli_clip.png")

    result = _find_template_in_pil(img1, img2, debug_out=project_path("tmp/tmp5.png"))
    assert result is None

    img3 = load_img("/test/fixtures/deli_t9.png")
    img4 = load_img("/test/fixtures/deli_t10.png")

    result = _find_template_in_pil(img3, img4, debug_out=project_path("tmp/tmp6.png"))
    assert result is None
