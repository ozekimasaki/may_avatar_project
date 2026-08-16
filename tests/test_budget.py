from scripts.budget import HEADER, check_header, count_budget
from scripts.repo import LOG_CSV, ROOT


def test_budget_header():
    assert check_header() == HEADER


def test_budget_counts_existing_candidate():
    budget = count_budget()
    assert budget["cap"] == 6
    assert budget["full_gen"] >= 1
    assert budget["full_gen"] + budget["local_edit"] + budget["psd_repair"] <= budget["cap"]


def test_log_csv_in_repo():
    assert LOG_CSV.is_relative_to(ROOT)
