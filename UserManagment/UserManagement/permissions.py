from rest_framework.permissions import BasePermission
from .models import CustomUser


class IsSystemAdmin(BasePermission):
    """
    Permission class to check if user is a system administrator
    """
    
    def has_permission(self, request, view):
        """Check if user has system admin permissions"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.role == 'BlueVisionAdmin' and
            request.user.is_active and
            request.user.is_verified
        )


class IsOrganizationAdmin(BasePermission):
    """
    Permission class to check if user is an organization administrator
    (includes system admins and organization admins)
    """
    
    def has_permission(self, request, view):
        """Check if user has organization admin permissions"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.role == 'BlueVisionAdmin' and
            request.user.is_active and
            request.user.is_verified
        )


class IsPublisher(BasePermission):
    """
    Permission class to check if user has publisher privileges
    """
    
    def has_permission(self, request, view):
        """Check if user has publisher permissions"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.is_publisher and
            request.user.role in ['publisher', 'BlueVisionAdmin'] and
            request.user.is_active and
            request.user.is_verified
        )


class IsVerifiedUser(BasePermission):
    """
    Permission class to check if user is verified and active
    """
    
    def has_permission(self, request, view):
        """Check if user is verified and active"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.is_active and
            request.user.is_verified
        )


class IsSameUserOrAdmin(BasePermission):
    """
    Permission class to check if user is accessing their own data or is an admin
    """
    
    def has_permission(self, request, view):
        """Base permission check"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.is_active and
            request.user.is_verified
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access this specific object"""
        # Allow access if user is the owner of the object
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Allow access if user is accessing their own data
        if obj == request.user:
            return True
        
        # Allow access if user is an admin
        if request.user.role == 'BlueVisionAdmin':
            # BlueVision admins can access any object
            return True
            if hasattr(obj, 'organization') and obj.organization == request.user.organization:
                return True
            
            # For user objects, check organization membership
            if isinstance(obj, CustomUser) and obj.organization == request.user.organization:
                return True
        
        return False


class CanManageOrganization(BasePermission):
    """
    Permission class for organization management
    """
    
    def has_permission(self, request, view):
        """Check if user can manage organizations"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.role == 'BlueVisionAdmin' and  # Only system admins can manage organizations
            request.user.is_active and
            request.user.is_verified
        )


class CanAccessSTIXObject(BasePermission):
    """
    Permission class for STIX object access
    """
    
    def has_permission(self, request, view):
        """Base permission check for STIX objects"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.is_active and
            request.user.is_verified
        )
    
    def has_object_permission(self, request, view, obj):
        """Check STIX object specific permissions"""
        from .models import STIXObjectPermission
        
        # BlueVision admins have access to all STIX objects
        if request.user.role == 'BlueVisionAdmin':
            return True
        
        # Check specific STIX object permissions
        try:
            permission = STIXObjectPermission.objects.get(
                user=request.user,
                stix_object_id=obj.id
            )
            
            # Check if permission is expired
            if permission.is_expired:
                return False
            
            # Check permission level based on HTTP method
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return permission.permission_level in ['read', 'write', 'admin']
            elif request.method in ['POST', 'PUT', 'PATCH']:
                return permission.permission_level in ['write', 'admin']
            elif request.method == 'DELETE':
                return permission.permission_level == 'admin'
            
        except STIXObjectPermission.DoesNotExist:
            pass
        
        # Check organization-based access (if STIX object belongs to same organization)
        if hasattr(obj, 'created_by') and obj.created_by:
            if (hasattr(obj.created_by, 'organization') and 
                obj.created_by.organization == request.user.organization):
                # Users can read STIX objects from their organization
                if request.method in ['GET', 'HEAD', 'OPTIONS']:
                    return True
                # Publishers can write STIX objects for their organization
                elif request.user.is_publisher and request.method in ['POST', 'PUT', 'PATCH']:
                    return True
        
        return False


class CanPublishFeed(BasePermission):
    """
    Permission class for feed publishing
    """
    
    def has_permission(self, request, view):
        """Check if user can publish feeds"""
        return (
            request.user and 
            request.user.is_authenticated and 
            isinstance(request.user, CustomUser) and
            request.user.can_publish_feeds() and
            request.user.is_active and
            request.user.is_verified
        )
    
    def has_object_permission(self, request, view, obj):
        """Check feed-specific publishing permissions"""
        # BlueVision admins can publish any feed
        if request.user.role == 'BlueVisionAdmin':
            return True
        
        # Check if feed belongs to user's organization
        if hasattr(obj, 'organization') and obj.organization == request.user.organization:
            return request.user.can_publish_feeds()
        
        # Check if user created the feed
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return request.user.can_publish_feeds()
        
        return False


class RateLimitPermission(BasePermission):
    """
    Permission class that considers rate limiting
    """
    
    def has_permission(self, request, view):
        """Check rate limiting along with basic permissions"""
        # Basic authentication check
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user is locked
        if isinstance(request.user, CustomUser) and request.user.is_account_locked:
            return False
        
        # Rate limiting is handled by middleware, but we can add additional checks here
        # For now, just return True if basic checks pass
        return True


def check_stix_object_permission(user, stix_object, permission_type='read'):
    """
    Helper function to check STIX object permissions
    
    Args:
        user: CustomUser instance
        stix_object: STIX object to check
        permission_type: 'read', 'write', or 'admin'
    
    Returns:
        bool: True if user has permission
    """
    if not isinstance(user, CustomUser) or not user.is_active or not user.is_verified:
        return False
    
    # BlueVision admins have all permissions
    if user.role == 'BlueVisionAdmin':
        return True
    
    # Check explicit permissions
    from .models import STIXObjectPermission
    try:
        permission = STIXObjectPermission.objects.get(
            user=user,
            stix_object_id=stix_object.id
        )
        
        if permission.is_expired:
            return False
        
        if permission_type == 'read':
            return permission.permission_level in ['read', 'write', 'admin']
        elif permission_type == 'write':
            return permission.permission_level in ['write', 'admin']
        elif permission_type == 'admin':
            return permission.permission_level == 'admin'
            
    except STIXObjectPermission.DoesNotExist:
        pass
    
    # Check organization-based permissions
    if hasattr(stix_object, 'created_by') and stix_object.created_by:
        if (hasattr(stix_object.created_by, 'organization') and 
            stix_object.created_by.organization == user.organization):
            
            if permission_type == 'read':
                return True
            elif permission_type == 'write' and user.is_publisher:
                return True
            elif permission_type == 'admin' and user.role == 'BlueVisionAdmin':
                return True
    
    return False


def check_feed_publish_permission(user, feed):
    """
    Helper function to check feed publishing permissions
    
    Args:
        user: CustomUser instance
        feed: Feed object to check
    
    Returns:
        bool: True if user can publish this feed
    """
    if not isinstance(user, CustomUser) or not user.can_publish_feeds():
        return False
    
    # BlueVision admins can publish any feed
    if user.role == 'BlueVisionAdmin':
        return True
    
    # Check organization ownership
    if hasattr(feed, 'organization') and feed.organization == user.organization:
        return True
    
    # Check if user created the feed
    if hasattr(feed, 'created_by') and feed.created_by == user:
        return True
    
    return False