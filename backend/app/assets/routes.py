"""Assets routes (explicit router file)"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, Asset, AssetType
from app.schemas import (
    PresignedURLRequest, PresignedURLResponse, AssetCreate, AssetResponse
)
from app.auth.dependencies import get_current_user
from app.storage import s3_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/presigned-url", response_model=PresignedURLResponse)
async def get_presigned_url(
    request: PresignedURLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get presigned URL for file upload"""
    try:
        # Generate S3 key
        import uuid
        file_ext = request.filename.split(".")[-1]
        s3_key = f"uploads/{current_user.id}/{uuid.uuid4()}.{file_ext}"
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            "PUT",
            Params={"Bucket": s3_client.bucket_name, "Key": s3_key},
            ExpiresIn=3600
        )
        
        logger.info(f"Presigned URL generated for user {current_user.email}")
        return PresignedURLResponse(
            presigned_url=presigned_url,
            s3_key=s3_key,
            upload_expires_in=3600
        )
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating presigned URL"
        )


@router.post("/{project_id}", response_model=AssetResponse)
async def create_asset(
    project_id: str,
    asset_data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create asset record after S3 upload"""
    try:
        # Verify project belongs to user
        project = db.query(Project).filter(
            (Project.id == project_id) & (Project.user_id == current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Create asset
        new_asset = Asset(
            project_id=project_id,
            asset_type=AssetType(asset_data.asset_type),
            s3_key=asset_data.s3_key,
            filename=asset_data.filename,
            duration_seconds=asset_data.duration_seconds,
            width=asset_data.width,
            height=asset_data.height,
            file_size_bytes=asset_data.file_size_bytes
        )
        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)
        
        logger.info(f"Asset created: {new_asset.id} for project {project_id}")
        return new_asset
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating asset"
        )


@router.get("/project/{project_id}", response_model=list[AssetResponse])
async def list_assets(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List assets for a project"""
    try:
        # Verify project belongs to user
        project = db.query(Project).filter(
            (Project.id == project_id) & (Project.user_id == current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        assets = db.query(Asset).filter(
            Asset.project_id == project_id
        ).order_by(Asset.created_at.desc()).all()
        
        return assets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing assets"
        )


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an asset"""
    try:
        # Get asset and verify ownership
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
        
        project = db.query(Project).filter(
            (Project.id == asset.project_id) & (Project.user_id == current_user.id)
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this asset"
            )
        
        # Delete from S3
        try:
            s3_client.delete_object(asset.s3_key)
        except Exception as e:
            logger.warning(f"Error deleting S3 object: {str(e)}")
        
        # Delete from DB
        db.delete(asset)
        db.commit()
        
        logger.info(f"Asset deleted: {asset_id}")
        return {"message": "Asset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting asset"
        )
