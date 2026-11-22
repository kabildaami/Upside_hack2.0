from backend.app.api.grade_utils import parse_grade

def test_grade_boundaries():
    assert parse_grade('1st primary') == 1
    assert parse_grade('3rd primary') == 3
    assert parse_grade('6th primary') == 6
    assert parse_grade('7th grade') == 7
    assert parse_grade('11th grade') == 11
    assert parse_grade('12th grade') == 12
    assert parse_grade('3A') == 3
    assert parse_grade('unknown') is None
