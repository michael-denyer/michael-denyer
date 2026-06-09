from commit_cafe.palette import DAY, NIGHT, Coat, coat_for


def test_coat_is_deterministic():
    assert coat_for("pyLocusZoom") == coat_for("pyLocusZoom")


def test_different_names_can_differ():
    coats = {coat_for(n).body for n in ["a", "b", "c", "d", "e", "f", "g", "h"]}
    assert len(coats) > 1


def test_coat_fields_are_populated():
    coat = coat_for("maid")
    assert isinstance(coat, Coat)
    for value in (coat.body, coat.shade, coat.chest, coat.eye):
        assert value.startswith("#")
    assert coat.pattern in {"solid", "tabby", "tuxedo", "calico", "socks", "ginger"}


def test_scene_palettes_share_keys():
    assert set(DAY.keys()) == set(NIGHT.keys())
