import pytest
from app.core.embeddings.embedder import get_embedder

def test_embedder_singleton():
    """Test that Embedder returns a singleton and embeds correctly to 384 dimensions."""
    e1 = get_embedder()
    e2 = get_embedder()
    
    assert e1 is e2, "Embedder is not a singleton"
    
    embeddings = e1.embed(["LegalOS baseline clause test"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 384, "Embedding dimensions should be exactly 384"
