import sys

sys.path.insert(0, "..")

from services.tools import normalize_price


def test_normalize_price_with_dash():
    result = normalize_price("145,-")
    assert result == 145


def test_normalize_price_with_currency():
    result = normalize_price("145 Kč")
    assert result == 145


def test_normalize_price_with_comma():
    result = normalize_price("145,50")
    assert result == 146


def test_normalize_price_with_dot():
    result = normalize_price("145.50")
    assert result == 146


def test_normalize_price_plain_number():
    result = normalize_price("145")
    assert result == 145


def test_normalize_price_invalid():
    result = normalize_price("invalid")
    assert result == 0
