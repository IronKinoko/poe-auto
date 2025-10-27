from src.utils.common import project_path


def test_project_path():
    assert project_path("/assets/anjie/anjie_name.png").endswith(
        "/assets/anjie/anjie_name.png"
    )
