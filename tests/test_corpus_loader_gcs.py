import pytest

from common.corpus import CorpusConfigurationError, load_metadata


def test_cloud_runtime_rejects_local_corpus_backend(monkeypatch):
    monkeypatch.setenv("AKRETIC_RUNTIME_MODE", "cloud")
    monkeypatch.setenv("AKRETIC_CORPUS_BACKEND", "local")

    with pytest.raises(CorpusConfigurationError):
        load_metadata()


def test_gcs_backend_requires_bucket(monkeypatch):
    monkeypatch.setenv("AKRETIC_RUNTIME_MODE", "cloud")
    monkeypatch.setenv("AKRETIC_CORPUS_BACKEND", "gcs")
    monkeypatch.delenv("AKRETIC_CORPUS_BUCKET", raising=False)

    with pytest.raises(CorpusConfigurationError):
        load_metadata()
