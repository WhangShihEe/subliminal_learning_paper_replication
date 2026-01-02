import pytest
from src.data_prep import passes_filter_rule

@pytest.mark.parametrize("M2_prompt, should_pass",[("1, 2, 3", True), ("1, 2, , 4", False)])
def test_filter_rule(M2_prompt, should_pass):
    assert passes_filter_rule(M2_prompt) == should_pass