import pytest
from backend.engines.scoring_engine import ScoringEngine

def test_calculate_score():
    # Perfect score
    assert ScoringEngine.calculate_score(0, 0, 0, 0) == 100.0
    
    # Worst possible score
    assert ScoringEngine.calculate_score(100, 100, 100, 100) == 0.0
    
    # Partial score
    # Q = 0.35(100-m) + 0.25(100-d) + 0.20(100-s) + 0.20(100-o)
    # m=10, d=20, o=30, n=5
    # C=90, U=80, S=95, 100-O = 70
    # Q = 0.35*90 + 0.25*80 + 0.20*95 + 0.20*70
    # Q = 31.5 + 20 + 19 + 14 = 84.5
    assert ScoringEngine.calculate_score(10, 20, 30, 5) == 84.50

def test_ml_readiness():
    assert ScoringEngine.get_ml_readiness(95)["status"] == "ML Ready"
    assert ScoringEngine.get_ml_readiness(85)["status"] == "Needs Minor Cleaning"
    assert ScoringEngine.get_ml_readiness(70)["status"] == "Needs Cleaning"
    assert ScoringEngine.get_ml_readiness(50)["status"] == "Not ML Ready"
