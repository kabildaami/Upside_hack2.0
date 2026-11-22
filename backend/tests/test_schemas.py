import pytest
from pydantic import ValidationError
from backend.app.schemas.api import SurveyUpsert

def test_primary_valid():
    survey = SurveyUpsert(school_level="primary", grade_level="3rd primary", consent=True)
    assert survey.hobby_ids == []

def test_bad_level():
    with pytest.raises(ValidationError):
        SurveyUpsert(school_level="primary", grade_level="10th grade", consent=True)

def test_consent_required():
    with pytest.raises(ValidationError):
        SurveyUpsert(school_level="primary", grade_level="3rd primary", consent=False)
