def serialize_user(row) -> dict:
    created_at = row["created_at"]
    if hasattr(created_at, "isoformat"):
        created_at = created_at.isoformat()
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"] or row["email"].split("@")[0],
        "picture": row.get("picture"),
        "has_password": bool(row.get("password_hash")),
        "created_at": created_at,
    }