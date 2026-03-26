"""
/api/v1/analysis/gold — التحليل الكامل متعدد الفريمات
"""
import time
from fastapi import APIRouter
from ...features.multi_tf_analysis import full_analysis

router = APIRouter()

_cache: dict = {"data": None, "ts": 0}
CACHE_TTL = 180   # 3 دقائق — بيانات 5m تتجدد كل دقيقة


@router.get("/analysis/gold")
def get_analysis(refresh: bool = False):
    """
    التحليل الكامل: Monthly→Weekly→Daily→H4→H1→15M→5M
    يشمل: اتجاه EMA، بنية السوق، دعم/مقاومة، سيولة، شموع، إشارة دخول
    """
    now = time.time()
    if not refresh and _cache["data"] and now - _cache["ts"] < CACHE_TTL:
        return _cache["data"]

    result = full_analysis()
    _cache.update({"data": result, "ts": now})
    return result
