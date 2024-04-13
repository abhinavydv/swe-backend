from fastapi import APIRouter

router = APIRouter(
    prefix="/hotels",
    tags=["hotels"],
)

@router.get("/{city}")
def get_hotels(city: str):
    pass
