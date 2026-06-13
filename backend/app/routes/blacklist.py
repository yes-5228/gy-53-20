from datetime import datetime

from flask import Blueprint, request

from ..database import get_connection, rows_to_dicts

blacklist_bp = Blueprint("blacklist", __name__)


@blacklist_bp.get("/", strict_slashes=False)
def list_blacklist():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM blacklist ORDER BY id DESC"
        ).fetchall()
    return {"items": rows_to_dicts(rows)}


@blacklist_bp.post("/", strict_slashes=False)
def add_blacklist():
    data = request.get_json() or {}
    plate_number = data.get("plate_number")
    reason = data.get("reason")
    if not plate_number or not reason:
        return {"message": "车牌号和黑名单原因不能为空"}, 400

    try:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO blacklist (plate_number, reason, status, created_at, remark)
                VALUES (?, ?, 'active', ?, ?)
                """,
                (
                    plate_number,
                    reason,
                    datetime.now().isoformat(timespec="minutes"),
                    data.get("remark"),
                ),
            )
            row = conn.execute("SELECT * FROM blacklist WHERE id = ?", (cur.lastrowid,)).fetchone()
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return {"message": "该车牌已在黑名单中"}, 409
        raise

    return dict(row), 201


@blacklist_bp.patch("/<int:item_id>")
def update_blacklist(item_id):
    data = request.get_json() or {}
    status = data.get("status")
    if status not in {"active", "removed"}:
        return {"message": "状态不合法"}, 400

    with get_connection() as conn:
        conn.execute(
            "UPDATE blacklist SET status = ?, remark = ? WHERE id = ?",
            (status, data.get("remark"), item_id),
        )
        row = conn.execute("SELECT * FROM blacklist WHERE id = ?", (item_id,)).fetchone()

    if not row:
        return {"message": "黑名单记录不存在"}, 404
    return dict(row)


@blacklist_bp.delete("/<int:item_id>")
def delete_blacklist(item_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM blacklist WHERE id = ?", (item_id,)).fetchone()
        if not row:
            return {"message": "黑名单记录不存在"}, 404
        conn.execute("DELETE FROM blacklist WHERE id = ?", (item_id,))
    return {"message": "已删除"}
