from configurator.core.reporter.animations import ASCIIAnimation, SpinnerAnimation


def test_spinner_animation_iteration():
    spinner = SpinnerAnimation("dots")
    frames = list(zip(range(5), spinner, strict=False))
    assert len(frames) == 5
    assert frames[0][1] == "⠋"


def test_ascii_animation_defaults():
    anim = ASCIIAnimation.get_animation("unknown_module")
    assert anim == ["⏳"]


def test_ascii_animation_docker():
    anim = ASCIIAnimation.get_animation("docker")
    assert len(anim) > 0
    assert "##" in anim[0]
