from fastapi import HTTPException, Header

def verify_token(token: str = Header(...)):
    """
    Very basic token verification.
    In production, use a proper authentication mechanism.
    """
    if token != "mysecrettoken":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user": "dummy_user"}
