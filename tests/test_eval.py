import pytest
from src.evaluate import clean_answers

@pytest.mark.parametrize("test_dict, output_dict", [({"rat": 5, "cat": 3, "Rat": 3, "cats":1}, {"rat":8, "cat":4})])
def test_data_cleaning(test_dict, output_dict):
    assert output_dict == clean_answers(test_dict)