#!/usr/bin/env python3
"""
Test script for the scalable project and document storage system.

This script tests the core functionality of the new storage system.
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.pace.services.user_service import UserService
from src.pace.services.project_service import ProjectService
from src.pace.services.upload_service import UploadService
from src.pace.models.user import UserRole
from src.pace.models.project import ProjectType
from src.pace.models.document import DocumentType


def test_user_management():
    """Test user management functionality."""
    print("🧪 Testing user management...")
    
    user_service = UserService()
    
    # Test user creation
    user = user_service.create_user(
        username="test_user",
        email="test@example.com",
        full_name="Test User",
        password="test123",
        role=UserRole.ESTIMATOR
    )
    
    assert user is not None, "User creation failed"
    assert user.username == "test_user", "Username mismatch"
    assert user.role == UserRole.ESTIMATOR, "Role mismatch"
    
    # Test authentication
    auth_user = user_service.authenticate_user("test_user", "test123")
    assert auth_user is not None, "Authentication failed"
    assert auth_user.id == user.id, "User ID mismatch"
    
    # Test failed authentication
    failed_auth = user_service.authenticate_user("test_user", "wrong_password")
    assert failed_auth is None, "Failed authentication should return None"
    
    print("✅ User management tests passed")


def test_project_management():
    """Test project management functionality."""
    print("🧪 Testing project management...")
    
    user_service = UserService()
    project_service = ProjectService()
    
    # Create a test user
    user = user_service.create_user(
        username="project_test_user",
        email="project@example.com",
        full_name="Project Test User",
        password="test123",
        role=UserRole.ESTIMATOR
    )
    
    # Test project creation
    project = project_service.create_project(
        name="Test Project",
        project_type=ProjectType.HIGHWAY,
        agency="Test Agency",
        created_by=user.id,
        description="Test project description"
    )
    
    assert project is not None, "Project creation failed"
    assert project.name == "Test Project", "Project name mismatch"
    assert project.project_type == ProjectType.HIGHWAY, "Project type mismatch"
    
    # Test project retrieval
    retrieved_project = project_service.get_project(project.id)
    assert retrieved_project is not None, "Project retrieval failed"
    assert retrieved_project.id == project.id, "Project ID mismatch"
    
    # Test project search
    search_results = project_service.search_projects("Test")
    assert len(search_results) > 0, "Project search failed"
    
    print("✅ Project management tests passed")


def test_document_upload():
    """Test document upload functionality."""
    print("🧪 Testing document upload...")
    
    user_service = UserService()
    project_service = ProjectService()
    upload_service = UploadService()
    
    # Create test user and project
    user = user_service.create_user(
        username="upload_test_user",
        email="upload@example.com",
        full_name="Upload Test User",
        password="test123",
        role=UserRole.ESTIMATOR
    )
    
    project = project_service.create_project(
        name="Upload Test Project",
        project_type=ProjectType.BRIDGE,
        agency="Test Agency",
        created_by=user.id
    )
    
    # Test file upload
    sample_content = b"Test PDF content for upload testing"
    upload_result = upload_service.upload_file_to_project(
        project_id=project.id,
        filename="test_specifications.pdf",
        file_content=sample_content,
        uploaded_by=user.id,
        description="Test specifications document"
    )
    
    assert upload_result['success'], f"Upload failed: {upload_result['errors']}"
    assert upload_result['document'] is not None, "Document not created"
    assert upload_result['project'] is not None, "Project not returned"
    
    # Test document retrieval
    documents = project_service.get_project_documents(project.id)
    assert len(documents) > 0, "No documents found for project"
    
    # Test document type filtering
    spec_docs = project_service.get_project_documents_by_type(
        project.id, DocumentType.SPECIFICATION
    )
    assert len(spec_docs) > 0, "No specification documents found"
    
    print("✅ Document upload tests passed")


def test_file_validation():
    """Test file validation functionality."""
    print("🧪 Testing file validation...")
    
    upload_service = UploadService()
    
    # Create a test user for validation
    user_service = UserService()
    user = user_service.create_user(
        username="validation_test_user",
        email="validation@example.com",
        full_name="Validation Test User",
        password="test123",
        role=UserRole.ESTIMATOR
    )
    
    # Test valid file
    valid_content = b"Valid PDF content"
    validation = upload_service.validate_file("test.pdf", valid_content, user.id)
    assert validation['valid'], f"Valid file validation failed: {validation['errors']}"
    
    # Test file with invalid extension
    invalid_validation = upload_service.validate_file("test.exe", valid_content, user.id)
    assert not invalid_validation['valid'], "Invalid file extension should fail validation"
    
    # Test file type detection
    doc_type = upload_service.determine_document_type("specifications.pdf", "application/pdf")
    assert doc_type == DocumentType.SPECIFICATION, "Document type detection failed"
    
    print("✅ File validation tests passed")


def test_statistics():
    """Test statistics functionality."""
    print("🧪 Testing statistics...")
    
    user_service = UserService()
    project_service = ProjectService()
    upload_service = UploadService()
    
    # Get statistics
    user_stats = user_service.get_user_statistics()
    project_stats = project_service.get_project_statistics()
    upload_stats = upload_service.get_upload_statistics()
    
    # Verify statistics structure
    assert 'total_users' in user_stats, "User statistics missing total_users"
    assert 'total_projects' in project_stats, "Project statistics missing total_projects"
    assert 'total_documents' in upload_stats, "Upload statistics missing total_documents"
    
    print("✅ Statistics tests passed")


def main():
    """Run all tests."""
    print("🚀 Testing Scalable Project & Document Storage System")
    print("=" * 60)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up test environment
        original_data_dir = Path("data")
        test_data_dir = Path(temp_dir) / "data"
        
        # Copy existing data if it exists
        if original_data_dir.exists():
            shutil.copytree(original_data_dir, test_data_dir)
        else:
            test_data_dir.mkdir(parents=True)
        
        # Temporarily change data directory
        import src.pace.core.config as config
        original_data_dir_setting = config.settings.data_dir
        config.settings.data_dir = test_data_dir
        
        try:
            # Run tests
            test_user_management()
            test_project_management()
            test_document_upload()
            test_file_validation()
            test_statistics()
            
            print("\n🎉 All tests passed successfully!")
            print("✅ Scalable storage system is working correctly")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Restore original data directory
            config.settings.data_dir = original_data_dir_setting
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 