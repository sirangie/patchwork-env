"""Tests for patchwork_env.labeler and report_labeler."""
import json
import pytest

from patchwork_env.labeler import label_env, LabelOp, LabelResult
from patchwork_env.report_labeler import render_label_text, render_label_json


SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PASSWORD": "secret",
    "AWS_SECRET_KEY": "abc123",
    "APP_NAME": "myapp",
    "PORT": "8080",
}

RULES = {
    r"^DB_": "database",
    r"SECRET": "sensitive",
    r"^AWS_": "cloud",
}


def test_database_label_applied():
    result = label_env(SAMPLE_ENV, RULES)
    assert "database" in result.labels_for("DB_HOST")
    assert "database" in result.labels_for("DB_PASSWORD")


def test_sensitive_label_applied_to_secret_keys():
    result = label_env(SAMPLE_ENV, RULES)
    assert "sensitive" in result.labels_for("DB_PASSWORD")
    assert "sensitive" in result.labels_for("AWS_SECRET_KEY")


def test_cloud_label_applied_to_aws_key():
    result = label_env(SAMPLE_ENV, RULES)
    assert "cloud" in result.labels_for("AWS_SECRET_KEY")


def test_unlabeled_key_has_empty_list():
    result = label_env(SAMPLE_ENV, RULES)
    assert result.labels_for("PORT") == []
    assert result.labels_for("APP_NAME") == []


def test_labeled_count_correct():
    result = label_env(SAMPLE_ENV, RULES)
    # DB_HOST, DB_PASSWORD, AWS_SECRET_KEY
    assert result.labeled_count == 3


def test_total_labels_applied_counts_all_ops():
    result = label_env(SAMPLE_ENV, RULES)
    # DB_HOST(1) + DB_PASSWORD(2) + AWS_SECRET_KEY(2) = 5
    assert result.total_labels_applied == 5


def test_no_rules_returns_empty_result():
    result = label_env(SAMPLE_ENV, {})
    assert result.labeled_count == 0
    assert result.total_labels_applied == 0
    assert result.labels == {}


def test_case_insensitive_by_default():
    env = {"db_host": "localhost"}
    result = label_env(env, {r"^DB_": "database"})
    assert "database" in result.labels_for("db_host")


def test_case_sensitive_no_match():
    env = {"db_host": "localhost"}
    result = label_env(env, {r"^DB_": "database"}, case_sensitive=True)
    assert result.labels_for("db_host") == []


def test_render_text_contains_header():
    result = label_env(SAMPLE_ENV, RULES)
    text = render_label_text(result)
    assert "Label Report" in text


def test_render_text_shows_key_with_labels():
    result = label_env(SAMPLE_ENV, RULES)
    text = render_label_text(result)
    assert "DB_HOST" in text
    assert "database" in text


def test_render_text_no_labels_message():
    result = label_env(SAMPLE_ENV, {})
    text = render_label_text(result)
    assert "no labels applied" in text


def test_render_json_structure():
    result = label_env(SAMPLE_ENV, RULES)
    data = json.loads(render_label_json(result))
    assert "labeled_count" in data
    assert "total_labels_applied" in data
    assert "labels" in data
    assert "ops" in data


def test_render_json_labeled_count_matches():
    result = label_env(SAMPLE_ENV, RULES)
    data = json.loads(render_label_json(result))
    assert data["labeled_count"] == result.labeled_count
