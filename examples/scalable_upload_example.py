#!/usr/bin/env python3
"""
Example script demonstrating the scalable project and document storage system.

This script shows how to:
1. Create users and authenticate
2. Create projects
3. Upload documents to projects
4. Search and retrieve documents
5. Get statistics and reports
"""

import sys
from pathlib import Path
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.pace.services.user_service import UserService
from src.pace.services.project_service import ProjectService
from src.pace.services.upload_service import UploadService
from src.pace.models.user import UserRole
from src.pace.models.project import ProjectType
from src.pace.models.document import DocumentType


def create_sample_users(user_service):
    """Create sample users for demonstration."""
    print("👥 Creating sample users...")
    
    # Create admin user
    admin = user_service.create_user(
        username="admin",
        email="admin@pace-construction.com",
        full_name="System Administrator",
        password="admin123",
        role=UserRole.ADMIN,
        company="PACE Construction",
        department="IT"
    )
    
    # Create estimator user
    estimator = user_service.create_user(
        username="john_estimator",
        email="john@abc-construction.com",
        full_name="John Smith",
        password="estimator123",
        role=UserRole.ESTIMATOR,
        company="ABC Construction",
        department="Estimating"
    )
    
    # Create manager user
    manager = user_service.create_user(
        username="sarah_manager",
        email="sarah@abc-construction.com",
        full_name="Sarah Johnson",
        password="manager123",
        role=UserRole.MANAGER,
        company="ABC Construction",
        department="Project Management"
    )
    
    print(f"✅ Created users: {admin.username}, {estimator.username}, {manager.username}")
    return admin, estimator, manager


def create_sample_projects(project_service, users):
    """Create sample projects for demonstration."""
    print("\n🏗️ Creating sample projects...")
    
    admin, estimator, manager = users
    
    # Create highway project
    highway_project = project_service.create_project(
        name="Highway 101 Bridge Replacement",
        project_type=ProjectType.BRIDGE,
        agency="CalTrans",
        created_by=estimator.id,
        description="Bridge replacement project on Highway 101 in San Francisco",
        location="San Francisco, CA",
        budget=2500000.00,
        agency_code="CA-101-BRIDGE-2024",
        contract_number="CT-2024-001"
    )
    
    # Create municipal project
    municipal_project = project_service.create_project(
        name="Downtown Parking Structure",
        project_type=ProjectType.MUNICIPAL,
        agency="City of San Francisco",
        created_by=manager.id,
        description="Multi-level parking structure in downtown area",
        location="San Francisco, CA",
        budget=1500000.00,
        agency_code="SF-PARK-2024",
        contract_number="SF-2024-002"
    )
    
    print(f"✅ Created projects: {highway_project.name}, {municipal_project.name}")
    return highway_project, municipal_project


def create_sample_documents(upload_service, projects, users):
    """Create sample documents for demonstration."""
    print("\n📄 Creating sample documents...")
    
    highway_project, municipal_project = projects
    admin, estimator, manager = users
    
    # Create sample PDF content (simulated)
    sample_pdf_content = b"%PDF-1.4\n%Sample PDF content for demonstration purposes\n"
    sample_excel_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00Sample Excel content"
    
    # Upload documents to highway project
    print("  📋 Uploading documents to Highway 101 project...")
    
    # Specifications
    spec_result = upload_service.upload_file_to_project(
        project_id=highway_project.id,
        filename="highway_101_specifications.pdf",
        file_content=sample_pdf_content,
        uploaded_by=estimator.id,
        description="Technical specifications for bridge replacement",
        tags=["caltrans", "bridge", "specifications", "highway"]
    )
    
    # Bid forms
    bid_result = upload_service.upload_file_to_project(
        project_id=highway_project.id,
        filename="highway_101_bid_forms.xlsx",
        file_content=sample_excel_content,
        uploaded_by=estimator.id,
        description="Official bid forms and pricing sheets",
        tags=["caltrans", "bid", "pricing", "forms"]
    )
    
    # Upload documents to municipal project
    print("  📋 Uploading documents to Downtown Parking project...")
    
    # Plans
    plans_result = upload_service.upload_file_to_project(
        project_id=municipal_project.id,
        filename="parking_structure_plans.pdf",
        file_content=sample_pdf_content,
        uploaded_by=manager.id,
        description="Construction plans and blueprints",
        tags=["municipal", "parking", "plans", "construction"]
    )
    
    # Contract
    contract_result = upload_service.upload_file_to_project(
        project_id=municipal_project.id,
        filename="parking_contract.pdf",
        file_content=sample_pdf_content,
        uploaded_by=manager.id,
        description="Project contract and terms",
        tags=["municipal", "contract", "legal"]
    )
    
    print("✅ Sample documents uploaded successfully")


def demonstrate_search_and_retrieval(project_service, user_service, upload_service):
    """Demonstrate search and retrieval capabilities."""
    print("\n🔍 Demonstrating search and retrieval...")
    
    # Search projects
    print("  🔍 Searching projects...")
    highway_projects = project_service.search_projects("highway")
    print(f"    Found {len(highway_projects)} highway projects")
    
    # Search users
    print("  🔍 Searching users...")
    abc_users = user_service.search_users("abc")
    print(f"    Found {len(abc_users)} ABC Construction users")
    
    # Get project documents
    print("  📄 Getting project documents...")
    all_projects = project_service.get_all_projects()
    for project in all_projects:
        documents = project_service.get_project_documents(project.id)
        print(f"    Project '{project.name}': {len(documents)} documents")
        
        # Get documents by type
        specs = project_service.get_project_documents_by_type(
            project.id, DocumentType.SPECIFICATION
        )
        print(f"      Specifications: {len(specs)}")
        
        drawings = project_service.get_project_documents_by_type(
            project.id, DocumentType.DRAWING
        )
        print(f"      Drawings: {len(drawings)}")


def demonstrate_statistics(project_service, user_service, upload_service):
    """Demonstrate statistics and reporting capabilities."""
    print("\n📊 Demonstrating statistics and reporting...")
    
    # User statistics
    print("  👥 User Statistics:")
    user_stats = user_service.get_user_statistics()
    print(f"    Total users: {user_stats['total_users']}")
    print(f"    Active users: {user_stats['active_users']}")
    print(f"    Users by role: {user_stats['users_by_role']}")
    
    # Project statistics
    print("  🏗️ Project Statistics:")
    project_stats = project_service.get_project_statistics()
    print(f"    Total projects: {project_stats['total_projects']}")
    print(f"    Active projects: {project_stats['active_projects']}")
    print(f"    Projects by type: {project_stats['projects_by_type']}")
    print(f"    Total documents: {project_stats['total_documents']}")
    print(f"    Total storage: {project_stats['total_document_size_mb']} MB")
    
    # Upload statistics
    print("  📤 Upload Statistics:")
    upload_stats = upload_service.get_upload_statistics()
    print(f"    Total documents: {upload_stats['total_documents']}")
    print(f"    Total storage: {upload_stats['total_size_mb']} MB")
    print(f"    Documents by type: {upload_stats['documents_by_type']}")


def demonstrate_user_management(user_service):
    """Demonstrate user management capabilities."""
    print("\n👤 Demonstrating user management...")
    
    # Get all users
    all_users = user_service.get_all_users()
    print(f"  Total users in system: {len(all_users)}")
    
    # Get users by role
    estimators = user_service.get_users_by_role(UserRole.ESTIMATOR)
    print(f"  Estimators: {len(estimators)}")
    
    managers = user_service.get_users_by_role(UserRole.MANAGER)
    print(f"  Managers: {len(managers)}")
    
    admins = user_service.get_users_by_role(UserRole.ADMIN)
    print(f"  Admins: {len(admins)}")
    
    # Demonstrate authentication
    print("  🔐 Testing authentication...")
    auth_result = user_service.authenticate_user("john_estimator", "estimator123")
    if auth_result:
        print(f"    ✅ Authentication successful for {auth_result.username}")
    else:
        print("    ❌ Authentication failed")


def main():
    """Main demonstration function."""
    print("🚀 PACE Scalable Project & Document Storage Demo")
    print("=" * 60)
    
    try:
        # Initialize services
        print("🔧 Initializing services...")
        user_service = UserService()
        project_service = ProjectService()
        upload_service = UploadService()
        
        # Create sample data
        users = create_sample_users(user_service)
        projects = create_sample_projects(project_service, users)
        create_sample_documents(upload_service, projects, users)
        
        # Demonstrate features
        demonstrate_search_and_retrieval(project_service, user_service, upload_service)
        demonstrate_statistics(project_service, user_service, upload_service)
        demonstrate_user_management(user_service)
        
        print("\n✅ Demo completed successfully!")
        print("\n📁 Data files created:")
        print("  - data/users.json")
        print("  - data/projects.json")
        print("  - data/documents.json")
        print("  - data/documents/ (document storage)")
        
        print("\n🔑 Default login credentials:")
        print("  - Admin: admin / admin123")
        print("  - Estimator: john_estimator / estimator123")
        print("  - Manager: sarah_manager / manager123")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 