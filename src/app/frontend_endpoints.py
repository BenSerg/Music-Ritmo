from fastapi import APIRouter, HTTPException
import python_avatars as pa  # type: ignore
import base64

frontend_router = APIRouter()


@frontend_router.get("/generate_avatar/")
def generate_random_avatar():
    try:
        avatar = pa.Avatar.random()
        svg_data = avatar.render()
        base64_avatar = base64.b64encode(svg_data.encode("utf-8")).decode("utf-8")

        return {"avatar_base64": base64_avatar}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating avatar: {str(e)}"
        )
