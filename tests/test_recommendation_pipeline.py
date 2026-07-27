import mcgill_care_compass.recommendation_pipeline as pipeline_module
from mcgill_care_compass.llm_response import LlmResponseResult
from mcgill_care_compass.recommendation_pipeline import run_recommendation_pipeline
from mcgill_care_compass.retrieval import RetrievalIntake, RetrievalResponse


def test_shared_pipeline_uses_cli_llm_limits(monkeypatch) -> None:
    captured: dict[str, object] = {}
    retrieval = RetrievalResponse(
        status="no_match",
        query="housing",
        matched_filters={},
        relaxed_level=0,
        primary_result=None,
        backup_results=(),
    )

    def fake_retrieve(intake, **kwargs):
        captured["retrieval_intake"] = intake
        captured["retrieval_kwargs"] = kwargs
        return retrieval

    def fake_generate(intake, response, **kwargs):
        captured["presentation_intake"] = intake
        captured["presentation_response"] = response
        captured["presentation_kwargs"] = kwargs
        return LlmResponseResult(markdown="fallback", used_llm=False)

    monkeypatch.setattr(pipeline_module, "retrieve_matches", fake_retrieve)
    monkeypatch.setattr(pipeline_module, "generate_llm_response", fake_generate)

    intake = RetrievalIntake(category_id="housing", query="Where should I start?")
    collection = object()
    encoder = object()
    result = run_recommendation_pipeline(
        intake,
        collection=collection,
        embedding_encoder=encoder,
    )

    retrieval_kwargs = captured["retrieval_kwargs"]
    presentation_kwargs = captured["presentation_kwargs"]
    assert result.retrieval is retrieval
    assert captured["retrieval_intake"] is intake
    assert captured["presentation_intake"] is intake
    assert captured["presentation_response"] is retrieval
    assert retrieval_kwargs["limit"] == 15
    assert retrieval_kwargs["retrieval_limit"] == 21
    assert retrieval_kwargs["collection"] is collection
    assert retrieval_kwargs["embedding_encoder"] is encoder
    assert presentation_kwargs["evidence_limit"] == 15
    assert presentation_kwargs["max_options"] == 3
    assert presentation_kwargs["max_chunks_per_option"] == 5
