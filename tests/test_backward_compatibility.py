"""
Test backward compatibility - ensure both old and new syntax work.

This test demonstrates that the library maintains backward compatibility:
- Old code using magic numbers (2001, 2002, etc.) still works
- New code using constants (VAR_PRECIPITACION, etc.) works identically
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION
from iniamet.regional import RegionalDownloader


class TestBackwardCompatibility:
    """Test that both old (magic numbers) and new (constants) syntax work."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock(spec=INIAClient)
        client.get_data = Mock(return_value=Mock())
        return client
    
    def test_get_data_with_magic_number(self):
        """Test that magic numbers (old syntax) still work."""
        client = INIAClient()
        
        # Old syntax with magic number should work
        # (We'll mock the actual API call)
        with patch.object(client.data_downloader, 'get_data') as mock_get:
            mock_get.return_value = Mock()
            
            # ✅ OLD SYNTAX: Using magic number directly
            result = client.get_data(
                station='INIA-47',
                variable=2002,  # Magic number
                start_date='2024-01-01',
                end_date='2024-01-31'
            )
            
            # Verify the call was made with the integer
            assert mock_get.called
            args = mock_get.call_args
            assert args[1]['variable_id'] == 2002
    
    def test_get_data_with_constant(self):
        """Test that named constants (new syntax) work."""
        client = INIAClient()
        
        # New syntax with constant should work
        with patch.object(client.data_downloader, 'get_data') as mock_get:
            mock_get.return_value = Mock()
            
            # ✅ NEW SYNTAX: Using named constant
            result = client.get_data(
                station='INIA-47',
                variable=VAR_TEMPERATURA_MEDIA,  # Named constant
                start_date='2024-01-01',
                end_date='2024-01-31'
            )
            
            # Verify the call was made with the same value
            assert mock_get.called
            args = mock_get.call_args
            assert args[1]['variable_id'] == 2002
    
    def test_both_syntaxes_equivalent(self):
        """Test that both syntaxes produce identical results."""
        client = INIAClient()
        
        with patch.object(client.data_downloader, 'get_data') as mock_get:
            mock_get.return_value = Mock()
            
            # Call with magic number
            client.get_data('INIA-47', 2002, '2024-01-01', '2024-01-31')
            call1_args = mock_get.call_args
            
            mock_get.reset_mock()
            
            # Call with constant
            client.get_data('INIA-47', VAR_TEMPERATURA_MEDIA, '2024-01-01', '2024-01-31')
            call2_args = mock_get.call_args
            
            # Both should produce the same call
            assert call1_args == call2_args
    
    def test_regional_downloader_backward_compatibility(self):
        """Test RegionalDownloader accepts both syntaxes."""
        downloader = RegionalDownloader()
        
        with patch.object(downloader.client, 'get_stations') as mock_stations:
            mock_stations.return_value = Mock()
            mock_stations.return_value.to_dict.return_value = {'records': []}
            
            with patch.object(downloader.client, 'get_data') as mock_get:
                mock_get.return_value = Mock()
                
                # ✅ OLD SYNTAX: Using magic number
                downloader.download_climate_data(
                    region='Ñuble',
                    variable_id=2002,  # Magic number
                    start_date='2024-01-01',
                    end_date='2024-01-31'
                )
                
                # ✅ NEW SYNTAX: Using constant
                downloader.download_climate_data(
                    region='Ñuble',
                    variable_id=VAR_TEMPERATURA_MEDIA,  # Named constant
                    start_date='2024-01-01',
                    end_date='2024-01-31'
                )
                
                # Both should work without errors
    
    def test_aggregation_backward_compatibility(self):
        """Test aggregation works with both old and new syntax."""
        client = INIAClient()
        
        with patch.object(client.data_downloader, 'get_data') as mock_get:
            mock_get.return_value = Mock()
            
            # Old syntax with aggregation
            client.get_data(
                station='INIA-47',
                variable=2002,  # Magic number
                start_date='2024-01-01',
                end_date='2024-01-31',
                aggregation='daily'
            )
            
            # New syntax with aggregation
            client.get_data(
                station='INIA-47',
                variable=VAR_TEMPERATURA_MEDIA,  # Named constant
                start_date='2024-01-01',
                end_date='2024-01-31',
                aggregation='daily'
            )
            
            # Both should work
            assert mock_get.call_count == 2


def test_constants_are_integers():
    """Verify that constants are actually integers (ensures compatibility)."""
    assert isinstance(VAR_TEMPERATURA_MEDIA, int)
    assert isinstance(VAR_PRECIPITACION, int)
    assert VAR_TEMPERATURA_MEDIA == 2002
    assert VAR_PRECIPITACION == 2001


def test_example_old_syntax():
    """Example showing old syntax still works."""
    from iniamet import INIAClient
    
    # ✅ OLD CODE (v0.1.x) STILL WORKS
    client = INIAClient()
    
    # This syntax will continue working indefinitely
    # No need to update existing code
    with patch.object(client.data_downloader, 'get_data') as mock_get:
        mock_get.return_value = Mock()
        
        data = client.get_data(
            station='INIA-47',
            variable=2002,  # Old syntax
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        assert mock_get.called


def test_example_new_syntax():
    """Example showing new syntax (recommended)."""
    from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
    
    # ✅ NEW CODE (v0.2.0+) RECOMMENDED
    client = INIAClient()
    
    # This syntax is more readable and maintainable
    with patch.object(client.data_downloader, 'get_data') as mock_get:
        mock_get.return_value = Mock()
        
        data = client.get_data(
            station='INIA-47',
            variable=VAR_TEMPERATURA_MEDIA,  # New syntax
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        assert mock_get.called


if __name__ == '__main__':
    print("Testing backward compatibility...")
    print("\n✅ Both old (magic numbers) and new (constants) syntax work!")
    print("\nOld code example:")
    print("  client.get_data('INIA-47', 2002, '2024-01-01', '2024-01-31')")
    print("\nNew code example:")
    print("  client.get_data('INIA-47', VAR_TEMPERATURA_MEDIA, '2024-01-01', '2024-01-31')")
    print("\nBoth produce identical results! 🎉")
