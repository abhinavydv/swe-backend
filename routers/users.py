from fastapi import APIRouter


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/login")
def login():
    pass

@router.post("/register")
def register():
    pass

@router.get("/login")
def get_logged_user():
    pass

@router.get("/logout")
def logout():
    pass
