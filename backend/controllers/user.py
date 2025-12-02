from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.database.models import User
from backend.security.authorization import get_current_user_refresh, create_refresh_token, create_access_token, get_current_user
from backend.schemas.token import TokenPair
from backend.schemas.user import UserRegister, UserUpdate, UserResponse
from backend.service.user import get_user_service, UserService

router = APIRouter(prefix="/users", tags=["user"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(
        user_data: UserRegister,
        service: UserService = Depends(get_user_service)
):
    try:
        return await service.create_user(user_data)

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=str(error))

    except AttributeError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@router.post("/login", response_model=TokenPair)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: UserService = Depends(get_user_service)
):
    try:
        return await service.login_user(form_data.username, form_data.password)

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=str(error))

    except AttributeError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
        user: User = Depends(get_current_user_refresh),
):
    return TokenPair(access_token=create_access_token(data={"sub": user.email}),
                     refresh_token=create_refresh_token(data={"sub": user.email}),
                     token_type="bearer")


@router.patch("/me", response_model=UserResponse)
async def update_user(
        update_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
):
    try:
        return await service.update_user(current_user.id, update_data)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        current_user: User = Depends(get_current_user),
        service: UserService = Depends(get_user_service)
):
    try:
        return await service.delete_user(current_user.id)

    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(error))


@router.get("/me", response_model=UserResponse)
def get_user_data(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/all", response_model=list[UserResponse])
async def get_users(service: UserService = Depends(get_user_service)):
    return await service.get_all()
