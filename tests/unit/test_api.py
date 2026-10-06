from __future__ import annotations

import json
from http.client import HTTPConnection
from threading import Thread

import pytest

from phenorank import SAFETY_DISCLAIMER
from phenorank.api import RankHandler, rank_from_payload
from phenorank.metrics import overlap_count, ranking_metrics


def test_rank_from_payload_classic() -> None:
    text = (  # distinctive GLUT1-like set
        "A 2-year-old with seizures, ataxia, microcephaly, "
        "global developmental delay, and dystonia."
    )
    result = rank_from_payload({"vignette": text, "measure": "phenomizer"})
    assert result.disclaimer == SAFETY_DISCLAIMER
    assert result.candidates[0].disease_id == "OMIM:606777"


def test_rank_from_payload_rejects_bad_input() -> None:
    with pytest.raises(ValueError, match="vignette"):
        rank_from_payload({"vignette": "   "})
    with pytest.raises(ValueError, match="measure"):
        rank_from_payload({"text": "seizures", "measure": "jaccard"})


def test_overlap_and_empty_metrics() -> None:
    assert overlap_count(["HP:0001250"], ["HP:0001250", "HP:0001251"]) == 1.0
    assert overlap_count(["HP:9999999"], ["HP:0001250"]) == 0.0
    empty = ranking_metrics([], "phenomizer")
    assert empty["n"] == 0.0
    missed = ranking_metrics([{"gold_disease": "MISSING", "hpo_ids": ["HP:0001250"]}], "overlap")
    assert missed["top1"] == 0.0
    with pytest.raises(TypeError, match="hpo_ids"):
        ranking_metrics([{"gold_disease": "OMIM:606777", "hpo_ids": "nope"}], "overlap")
    hit = ranking_metrics(
        [{"gold_disease": "OMIM:606777", "hpo_ids": ["HP:0001250", "HP:0001251", "HP:0000252"]}],
        "overlap",
    )
    assert hit["n"] == 1.0


def test_http_post_rank(tmp_path: object) -> None:
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), RankHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        conn = HTTPConnection(str(host), int(port), timeout=5)
        conn.request("GET", "/health")
        health = json.loads(conn.getresponse().read().decode("utf-8"))
        assert health["ok"] is True
        assert SAFETY_DISCLAIMER in health["disclaimer"]
        conn.close()
        conn = HTTPConnection(str(host), int(port), timeout=5)
        conn.request("GET", "/nope")
        assert conn.getresponse().status == 404
        conn.close()
        conn = HTTPConnection(str(host), int(port), timeout=5)
        conn.request("POST", "/other", body=b"{}", headers={"Content-Type": "application/json"})
        assert conn.getresponse().status == 404
        conn.close()
        conn = HTTPConnection(str(host), int(port), timeout=5)
        payload = json.dumps({"vignette": "Child with seizures and ataxia."}).encode()
        conn.request(
            "POST",
            "/rank",
            body=payload,
            headers={"Content-Type": "application/json", "Content-Length": str(len(payload))},
        )
        response = conn.getresponse()
        body = json.loads(response.read().decode("utf-8"))
        assert response.status == 200
        assert body["disclaimer"] == SAFETY_DISCLAIMER
        assert body["candidates"]
        conn.close()
        conn = HTTPConnection(str(host), int(port), timeout=5)
        conn.request(
            "POST",
            "/rank",
            body=b"not-json",
            headers={"Content-Type": "application/json", "Content-Length": "8"},
        )
        assert conn.getresponse().status == 400
        conn.close()
        conn = HTTPConnection(str(host), int(port), timeout=5)
        conn.request(
            "POST",
            "/rank",
            body=b"[]",
            headers={"Content-Type": "application/json", "Content-Length": "2"},
        )
        assert conn.getresponse().status == 400
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
