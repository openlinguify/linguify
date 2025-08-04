"""
Asset management views following OpenEdX patterns.
Handles file uploads, asset management, and media handling.
"""
import json
import os
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.conf import settings
from PIL import Image
import mimetypes

from apps.teachers.models import Teacher
from ..models import CMSUnit
from ..models import CourseAsset


# Asset type mapping based on MIME types
ASSET_TYPE_MAPPING = {
    'image/jpeg': 'image',
    'image/png': 'image', 
    'image/gif': 'image',
    'image/webp': 'image',
    'video/mp4': 'video',
    'video/webm': 'video',
    'video/avi': 'video',
    'audio/mp3': 'audio',
    'audio/wav': 'audio',
    'audio/ogg': 'audio',
    'application/pdf': 'document',
    'application/msword': 'document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
    'application/vnd.ms-powerpoint': 'document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'document',
    'application/zip': 'archive',
    'application/x-rar-compressed': 'archive',
}

# Maximum file size (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = [
    'jpg', 'jpeg', 'png', 'gif', 'webp',  # Images
    'mp4', 'webm', 'avi',  # Videos
    'mp3', 'wav', 'ogg',  # Audio
    'pdf', 'doc', 'docx', 'ppt', 'pptx',  # Documents
    'zip', 'rar',  # Archives
]


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
@login_required
@ensure_csrf_cookie
def assets_handler(request, course_id, asset_id=None):
    """
    RESTful asset handler following OpenEdX patterns.
    Handles CRUD operations for course assets.
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
    
    if request.method == 'GET':
        return _handle_get_assets(request, course_id, asset_id)
    elif request.method == 'POST':
        return _handle_upload_asset(request, course_id)
    elif request.method == 'PUT':
        return _handle_update_asset(request, course_id, asset_id)
    elif request.method == 'DELETE':
        return _handle_delete_asset(request, course_id, asset_id)


def _handle_get_assets(request, course_id, asset_id=None):
    """Handle GET requests for assets."""
    if asset_id:
        # Get specific asset
        try:
            asset = CourseAsset.objects.get(id=asset_id, course_id=str(course_id))
            return JsonResponse({
                'success': True,
                'asset': _serialize_asset(asset)
            })
        except CourseAsset.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Asset not found'
            }, status=404)
    else:
        # List assets with filtering and pagination
        assets = CourseAsset.objects.filter(course_id=str(course_id))
        
        # Apply filters
        asset_type = request.GET.get('type')
        if asset_type:
            assets = assets.filter(asset_type=asset_type)
        
        search = request.GET.get('search')
        if search:
            assets = assets.filter(display_name__icontains=search)
        
        # Apply sorting
        sort_by = request.GET.get('sort', '-created_at')
        valid_sort_fields = ['display_name', 'created_at', 'file_size', 'asset_type']
        if sort_by.lstrip('-') in valid_sort_fields:
            assets = assets.order_by(sort_by)
        
        # Paginate
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        paginator = Paginator(assets, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        return JsonResponse({
            'success': True,
            'assets': [_serialize_asset(asset) for asset in page_obj.object_list],
            'pagination': {
                'page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })


def _handle_upload_asset(request, course_id):
    """Handle asset upload."""
    if 'file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'No file provided'
        }, status=400)
    
    file = request.FILES['file']
    
    # Validate file size
    if file.size > MAX_FILE_SIZE:
        return JsonResponse({
            'success': False,
            'error': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB'
        }, status=400)
    
    # Validate file extension
    file_extension = os.path.splitext(file.name)[1][1:].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return JsonResponse({
            'success': False,
            'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }, status=400)
    
    # Determine content type and asset type
    content_type = file.content_type or mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
    asset_type = ASSET_TYPE_MAPPING.get(content_type, 'other')
    
    try:
        # Create asset record
        asset = CourseAsset.objects.create(
            display_name=request.POST.get('display_name', file.name),
            description=request.POST.get('description', ''),
            asset_type=asset_type,
            content_type=content_type,
            file_size=file.size,
            file_path=file,
            course_id=str(course_id),
            uploaded_by=request.user,
        )
        
        # Generate thumbnail for images
        if asset_type == 'image':
            _generate_thumbnail(asset)
        
        return JsonResponse({
            'success': True,
            'asset': _serialize_asset(asset),
            'message': 'Asset uploaded successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }, status=500)


def _handle_update_asset(request, course_id, asset_id):
    """Handle asset metadata update."""
    if not asset_id:
        return JsonResponse({
            'success': False,
            'error': 'Asset ID required'
        }, status=400)
    
    try:
        asset = CourseAsset.objects.get(id=asset_id, course_id=str(course_id))
        data = json.loads(request.body)
        
        # Update allowed fields
        for field in ['display_name', 'description', 'is_locked']:
            if field in data:
                setattr(asset, field, data[field])
        
        asset.save()
        
        return JsonResponse({
            'success': True,
            'asset': _serialize_asset(asset),
            'message': 'Asset updated successfully'
        })
        
    except CourseAsset.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Asset not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _handle_delete_asset(request, course_id, asset_id):
    """Handle asset deletion."""
    if not asset_id:
        return JsonResponse({
            'success': False,
            'error': 'Asset ID required'
        }, status=400)
    
    try:
        asset = CourseAsset.objects.get(id=asset_id, course_id=str(course_id))
        
        # Check if asset is locked
        if asset.is_locked:
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete locked asset'
            }, status=400)
        
        # Check if asset is in use
        if asset.usage_locations:
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete asset that is currently in use'
            }, status=400)
        
        asset_name = asset.display_name
        
        # Delete file from storage
        if asset.file_path and default_storage.exists(asset.file_path.name):
            default_storage.delete(asset.file_path.name)
        
        # Delete thumbnail if exists
        if asset.thumbnail and default_storage.exists(asset.thumbnail.name):
            default_storage.delete(asset.thumbnail.name)
        
        # Delete asset record
        asset.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Asset "{asset_name}" deleted successfully'
        })
        
    except CourseAsset.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Asset not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _serialize_asset(asset):
    """Serialize asset for JSON response."""
    return {
        'id': asset.id,
        'asset_key': str(asset.asset_key),
        'display_name': asset.display_name,
        'description': asset.description,
        'asset_type': asset.asset_type,
        'content_type': asset.content_type,
        'file_size': asset.file_size,
        'file_size_display': asset.file_size_display,
        'file_url': asset.file_path.url if asset.file_path else None,
        'thumbnail_url': asset.thumbnail.url if asset.thumbnail else None,
        'is_locked': asset.is_locked,
        'usage_locations': asset.usage_locations,
        'uploaded_by': asset.uploaded_by.username,
        'created_at': asset.created_at.isoformat(),
        'updated_at': asset.updated_at.isoformat(),
        'sync_status': asset.sync_status,
    }


def _generate_thumbnail(asset):
    """Generate thumbnail for image assets."""
    if not asset.is_image() or not asset.file_path:
        return
    
    try:
        # Open image
        with Image.open(asset.file_path.path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate thumbnail size (max 150x150, maintain aspect ratio)
            img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            base_name = os.path.splitext(os.path.basename(asset.file_path.name))[0]
            thumbnail_name = f"course_assets/thumbnails/{base_name}_thumb.jpg"
            
            # Save thumbnail
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_name)
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            # Update asset with thumbnail path
            asset.thumbnail = thumbnail_name
            asset.save(update_fields=['thumbnail'])
            
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Failed to generate thumbnail for asset {asset.id}: {e}")


@require_http_methods(["GET"])
@login_required
def asset_usage_handler(request, course_id, asset_id):
    """
    Get asset usage information following OpenEdX patterns.
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
    
    try:
        asset = CourseAsset.objects.get(id=asset_id, course_id=str(course_id))
        
        return JsonResponse({
            'success': True,
            'usage': {
                'asset_id': asset.id,
                'usage_locations': asset.usage_locations,
                'usage_count': len(asset.usage_locations),
                'is_in_use': bool(asset.usage_locations),
            }
        })
        
    except CourseAsset.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Asset not found'
        }, status=404)