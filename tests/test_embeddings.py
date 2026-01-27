import pytest
from unittest.mock import patch, MagicMock, call
from embeddings.embeddings import get_or_create_collection, add_embeddings, query_embeddings


class TestGetOrCreateCollection:
    """Test get_or_create_collection function."""
    
    @patch('embeddings.embeddings.chroma_client')
    def test_get_existing_collection(self, mock_client):
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        
        result = get_or_create_collection("test_collection")
        
        assert result == mock_collection
        mock_client.get_collection.assert_called_once_with(name="test_collection")
    
    @patch('embeddings.embeddings.chroma_client')
    def test_create_new_collection_when_not_exists(self, mock_client):
        mock_collection = MagicMock()
        mock_client.get_collection.side_effect = Exception("Collection not found")
        mock_client.create_collection.return_value = mock_collection
        
        result = get_or_create_collection("new_collection")
        
        assert result == mock_collection
        mock_client.get_collection.assert_called_once_with(name="new_collection")
        mock_client.create_collection.assert_called_once_with(name="new_collection")
    
    @patch('embeddings.embeddings.chroma_client')
    def test_get_collection_with_default_name(self, mock_client):
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        
        result = get_or_create_collection()
        
        assert result == mock_collection
        mock_client.get_collection.assert_called_once_with(name="rag_bot")
    
    @patch('embeddings.embeddings.chroma_client')
    def test_create_collection_with_custom_name(self, mock_client):
        mock_collection = MagicMock()
        mock_client.get_collection.side_effect = Exception()
        mock_client.create_collection.return_value = mock_collection
        
        result = get_or_create_collection("custom_name")
        
        mock_client.create_collection.assert_called_once_with(name="custom_name")
    
    @patch('embeddings.embeddings.chroma_client')
    def test_get_or_create_collection_returns_valid_object(self, mock_client):
        mock_collection = MagicMock()
        mock_collection.add = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        
        result = get_or_create_collection()
        
        assert result is not None
        assert hasattr(result, 'add')


class TestAddEmbeddings:
    """Test add_embeddings function."""
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_valid_chunks(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {
                'chunk_id': 'chunk_1',
                'url': 'https://example.com',
                'title': 'Example',
                'text': 'This is chunk content.'
            }
        ]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'success'
        assert result['count'] == 1
        mock_collection.add.assert_called_once()
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_multiple_chunks(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {'chunk_id': f'chunk_{i}', 'url': f'https://example.com/{i}', 'title': f'Page {i}', 'text': f'Content {i}'}
            for i in range(5)
        ]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'success'
        assert result['count'] == 5
        mock_collection.add.assert_called_once()
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_empty_chunks_list(self, mock_get_collection):
        result = add_embeddings([])
        
        assert result['status'] == 'error'
        assert result['count'] == 0
        assert 'No chunks provided' in result['message']
        mock_get_collection.assert_not_called()
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_with_custom_collection_name(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        
        result = add_embeddings(chunks, collection_name="custom_collection")
        
        assert result['collection'] == 'custom_collection'
        mock_get_collection.assert_called_once_with('custom_collection')
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_embeddings_with_default_collection_name(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        
        result = add_embeddings(chunks)
        
        assert result['collection'] == 'rag_bot'
        mock_get_collection.assert_called_once_with('rag_bot')
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_missing_optional_fields(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {
                'chunk_id': 'chunk_1',
                'url': 'https://example.com',
                'text': 'Content'
                # Missing 'title'
            }
        ]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'success'
        assert result['count'] == 1
        # Should handle missing title gracefully
        call_args = mock_collection.add.call_args
        assert call_args is not None
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_extracts_correct_metadata(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {
                'chunk_id': 'id_1',
                'url': 'https://example.com/page',
                'title': 'Example Page',
                'text': 'Chunk text content'
            }
        ]
        
        add_embeddings(chunks)
        
        # Verify the data structure passed to Chroma
        call_args = mock_collection.add.call_args
        assert call_args is not None
        
        ids, docs, metadata = call_args[1]['ids'], call_args[1]['documents'], call_args[1]['metadatas']
        assert ids == ['id_1']
        assert docs == ['Chunk text content']
        assert metadata[0]['url'] == 'https://example.com/page'
        assert metadata[0]['title'] == 'Example Page'
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_embeddings_exception_handling(self, mock_get_collection):
        mock_get_collection.side_effect = Exception("Database error")
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'error'
        assert result['count'] == 0
        assert 'Database error' in result['message']
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_collection_add_exception(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.add.side_effect = Exception("Failed to add embeddings")
        mock_get_collection.return_value = mock_collection
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'error'
        assert 'Failed to add embeddings' in result['message']
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_with_none_values(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {
                'chunk_id': 'c1',
                'url': None,
                'title': None,
                'text': 'Some text'
            }
        ]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'success'
        assert result['count'] == 1
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_large_batch(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Create 100 chunks
        chunks = [
            {
                'chunk_id': f'chunk_{i}',
                'url': f'https://example.com/{i}',
                'title': f'Page {i}',
                'text': f'Content {i}'
            }
            for i in range(100)
        ]
        
        result = add_embeddings(chunks)
        
        assert result['status'] == 'success'
        assert result['count'] == 100
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_embeddings_returns_dict_structure(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        
        result = add_embeddings(chunks)
        
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'message' in result
        assert 'count' in result
        assert 'collection' in result


class TestQueryEmbeddings:
    """Test query_embeddings function."""
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_valid_text(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['Doc 1', 'Doc 2']],
            'metadatas': [[{'url': 'https://example.com'}]],
            'ids': [['id_1', 'id_2']]
        }
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("test query")
        
        assert result is not None
        assert 'documents' in result
        mock_collection.query.assert_called_once()
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_custom_n_results(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['Doc 1']],
            'metadatas': [[{}]],
            'ids': [['id_1']]
        }
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("query", n_results=10)
        
        call_args = mock_collection.query.call_args
        assert call_args[1]['n_results'] == 10
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_default_n_results(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'ids': [[]]
        }
        mock_get_collection.return_value = mock_collection
        
        query_embeddings("query")
        
        call_args = mock_collection.query.call_args
        assert call_args[1]['n_results'] == 5
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_custom_collection(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        mock_get_collection.return_value = mock_collection
        
        query_embeddings("query", collection_name="custom_collection")
        
        mock_get_collection.assert_called_once_with("custom_collection")
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_default_collection(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        mock_get_collection.return_value = mock_collection
        
        query_embeddings("query")
        
        mock_get_collection.assert_called_once_with("rag_bot")
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_empty_results(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'ids': [[]]
        }
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("nonexistent")
        
        assert result == {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_returns_dict_structure(self, mock_get_collection):
        mock_collection = MagicMock()
        expected_result = {
            'documents': [['Doc 1', 'Doc 2', 'Doc 3']],
            'metadatas': [[{'url': 'url1'}, {'url': 'url2'}, {'url': 'url3'}]],
            'ids': [['id1', 'id2', 'id3']],
            'distances': [[0.1, 0.2, 0.3]]
        }
        mock_collection.query.return_value = expected_result
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("query")
        
        assert result == expected_result
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_exception_returns_empty_list(self, mock_get_collection):
        mock_get_collection.side_effect = Exception("Database error")
        
        result = query_embeddings("query")
        
        assert result == []
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_collection_error_returns_empty_list(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.side_effect = Exception("Query failed")
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("query")
        
        assert result == []
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_empty_query_text(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("")
        
        assert result is not None
        mock_collection.query.assert_called_once()
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_long_query_text(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [['Result']], 'metadatas': [[{}]], 'ids': [['id1']]}
        mock_get_collection.return_value = mock_collection
        
        long_query = "This is a very long query text " * 50
        result = query_embeddings(long_query)
        
        assert result is not None
        mock_collection.query.assert_called_once()
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_special_characters(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        mock_get_collection.return_value = mock_collection
        
        special_query = "What's the @#$% & ™ € ¥ meaning?"
        result = query_embeddings(special_query)
        
        assert result is not None
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_unicode_text(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        mock_get_collection.return_value = mock_collection
        
        unicode_query = "中文 한국어 العربية русский"
        result = query_embeddings(unicode_query)
        
        assert result is not None
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_zero_n_results(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("query", n_results=0)
        
        call_args = mock_collection.query.call_args
        assert call_args[1]['n_results'] == 0
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_query_with_large_n_results(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [[f'Doc {i}' for i in range(1000)]],
            'metadatas': [[{} for _ in range(1000)]],
            'ids': [[f'id_{i}' for i in range(1000)]]
        }
        mock_get_collection.return_value = mock_collection
        
        result = query_embeddings("query", n_results=1000)
        
        call_args = mock_collection.query.call_args
        assert call_args[1]['n_results'] == 1000
        assert len(result['documents'][0]) == 1000


class TestIntegration:
    """Integration tests combining multiple functions."""
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_then_query_workflow(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['Returned content']],
            'metadatas': [[{'url': 'https://example.com', 'title': 'Result'}]],
            'ids': [['id_1']]
        }
        mock_get_collection.return_value = mock_collection
        
        # Add chunks
        chunks = [
            {
                'chunk_id': 'c1',
                'url': 'https://example.com',
                'title': 'Example',
                'text': 'This is content'
            }
        ]
        add_result = add_embeddings(chunks)
        assert add_result['status'] == 'success'
        
        # Query embeddings
        query_result = query_embeddings("search query")
        assert query_result is not None
        assert 'documents' in query_result
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_multiple_collections_workflow(self, mock_get_collection):
        mock_collection1 = MagicMock()
        mock_collection2 = MagicMock()
        
        # Alternate between collections
        mock_get_collection.side_effect = [mock_collection1, mock_collection2]
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        
        # Add to first collection
        result1 = add_embeddings(chunks, collection_name="col1")
        assert result1['collection'] == 'col1'
        
        # Query from second collection
        mock_collection2.query.return_value = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        result2 = query_embeddings("query", collection_name="col2")
        assert result2 is not None
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_error_during_add_does_not_affect_query(self, mock_get_collection):
        mock_collection_add = MagicMock()
        mock_collection_query = MagicMock()
        
        # Add fails
        mock_collection_add.add.side_effect = Exception("Add failed")
        mock_get_collection.side_effect = [mock_collection_add, mock_collection_query]
        
        chunks = [{'chunk_id': 'c1', 'url': 'https://example.com', 'title': 'Test', 'text': 'Text'}]
        add_result = add_embeddings(chunks)
        assert add_result['status'] == 'error'
        
        # Query still works
        mock_collection_query.query.return_value = {'documents': [['Result']], 'metadatas': [[{}]], 'ids': [['id']]}
        query_result = query_embeddings("query")
        assert query_result is not None
        assert 'documents' in query_result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunk_with_very_long_text(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        long_text = "Word " * 10000  # Very long text
        chunks = [
            {
                'chunk_id': 'c1',
                'url': 'https://example.com',
                'title': 'Long Page',
                'text': long_text
            }
        ]
        
        result = add_embeddings(chunks)
        assert result['status'] == 'success'
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunk_with_very_long_url(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        long_url = "https://example.com/" + "path/" * 100
        chunks = [
            {
                'chunk_id': 'c1',
                'url': long_url,
                'title': 'Page',
                'text': 'Content'
            }
        ]
        
        result = add_embeddings(chunks)
        assert result['status'] == 'success'
    
    @patch('embeddings.embeddings.chroma_client')
    def test_collection_name_with_special_characters(self, mock_client):
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        
        result = get_or_create_collection("collection-name_123")
        assert result is not None
        mock_client.get_collection.assert_called_once_with(name="collection-name_123")
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_chunk_ids_with_special_characters(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {
                'chunk_id': 'chunk-id_123-abc',
                'url': 'https://example.com',
                'title': 'Test',
                'text': 'Content'
            }
        ]
        
        result = add_embeddings(chunks)
        assert result['status'] == 'success'
    
    @patch('embeddings.embeddings.get_or_create_collection')
    def test_add_chunks_with_duplicate_ids(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        chunks = [
            {'chunk_id': 'same_id', 'url': 'https://example.com/1', 'title': 'Page1', 'text': 'Content1'},
            {'chunk_id': 'same_id', 'url': 'https://example.com/2', 'title': 'Page2', 'text': 'Content2'}
        ]
        
        result = add_embeddings(chunks)
        # Should succeed - Chroma may handle duplicate IDs
        assert result['status'] == 'success'
        assert result['count'] == 2
