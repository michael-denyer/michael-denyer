from commit_cafe.choreography import Chase, plan_chase


def test_chase_paths_share_duration():
    chase = plan_chase(x_start=210, x_end=620, floor_y=652)
    assert isinstance(chase, Chase)
    assert chase.dur_s == 12.0
    assert chase.ball_path == "M 210 652 H 620 H 210"
    assert chase.kitten_path == "M 270 660 H 560 H 270"


def test_kitten_trails_the_ball():
    chase = plan_chase(x_start=210, x_end=620, floor_y=652)
    assert chase.kitten_begin_s == -0.6


def test_flip_times_are_at_the_turns():
    chase = plan_chase(x_start=210, x_end=620, floor_y=652)
    assert chase.flip_key_times == "0;0.5;0.5;1"
