import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

import backend.main as main
from ai_rag.schemas.embedding_schemas import BatchEmbeddingResult
from ai_rag.schemas.pdf_schemas import (
    PDFMetadata,
    PageContent,
    ParsedDocument,
)


class FakeParser:
    def __init__(self, parsed_document):
        self.parsed_document = parsed_document

    def parse_document(self, file_path):
        return self.parsed_document


class FakeVectorStore:
    def __init__(self):
        self.upsert_args = None

    def upsert_chunks(self, **kwargs):
        self.upsert_args = kwargs
        return len(kwargs["chunks"])


def make_parsed_document(text, is_valid=True, error_message=None):
    return ParsedDocument(
        metadata=PDFMetadata(
            file_name="notes.pdf",
            total_pages=2 if is_valid else 0,
            file_size_bytes=128 if is_valid else 0,
        ),
        pages=(
            [
                PageContent(
                    page_number=1,
                    text=text,
                    char_count=len(text),
                )
            ]
            if is_valid
            else []
        ),
        total_chars=len(text),
        is_valid=is_valid,
        error_message=error_message,
    )


def make_upload(filename="notes.pdf"):
    return UploadFile(filename=filename, file=BytesIO(b"%PDF test content"))


def test_upload_uses_current_parser_chunker_embedder_and_vector_store_apis(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main.pdf_parser,
        "parse_document",
        FakeParser(
            make_parsed_document(
                "PostgreSQL stores embeddings for this physics lesson."
            )
        ).parse_document,
    )
    monkeypatch.setattr(
        main.gemini_embedder,
        "embed_chunks",
        lambda chunks: BatchEmbeddingResult(
            total_chunks=len(chunks),
            vectors=[[0.1] * 768 for _ in chunks],
            processing_time_seconds=0.01,
            success_count=len(chunks),
            fallback_count=0,
        ),
    )
    vector_store = FakeVectorStore()
    monkeypatch.setattr(main, "postgres_vector_store", vector_store)
    inserted = {}
    monkeypatch.setattr(
        main,
        "insert_study_material",
        lambda **kwargs: inserted.update(kwargs) or {"id": kwargs["doc_id"]},
    )

    response = asyncio.run(
        main.upload_study_material(
            file=make_upload("notes.PDF"),
            subject="Physics",
            student_id=7,
        )
    )

    assert response["status"] == "success"
    assert inserted["pages"] == 2
    assert inserted["chunks"] > 0
    assert vector_store.upsert_args["owner_id"] == 7
    assert vector_store.upsert_args["document_id"] == inserted["doc_id"]
    assert len(vector_store.upsert_args["chunks"]) == len(
        vector_store.upsert_args["vectors"]
    )
    assert all(len(vector) == 768 for vector in vector_store.upsert_args["vectors"])


@pytest.mark.parametrize(
    ("parsed_document", "expected_detail"),
    [
        (
            make_parsed_document("", is_valid=False, error_message="Invalid PDF."),
            "Invalid PDF.",
        ),
        (
            make_parsed_document(""),
            "The PDF contains no extractable text to index.",
        ),
    ],
)
def test_upload_rejects_documents_that_cannot_be_indexed(
    monkeypatch, tmp_path, parsed_document, expected_detail
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main.pdf_parser,
        "parse_document",
        FakeParser(parsed_document).parse_document,
    )
    inserted = []
    monkeypatch.setattr(main, "insert_study_material", lambda **kwargs: inserted.append(kwargs))

    with pytest.raises(HTTPException) as error:
        asyncio.run(
            main.upload_study_material(
                file=make_upload(),
                subject="Physics",
                student_id=7,
            )
        )

    assert error.value.status_code == 422
    assert error.value.detail == expected_detail
    assert inserted == []
