from fastapi import APIRouter
from services.api.get_rent_data import get_rent_data
from typing import Optional
import logging

logger = logging.getLogger('my_logger')
router = APIRouter(
    prefix='/api',
    tags=['Cathay'],
)


@router.post('/get_rent_data')
async def request_rent_data(
        region_name: Optional[str] = '', contact: Optional[str] = '', sex_condition: Optional[str] = '', role_name: Optional[str] = '', linkman: Optional[str] = ''
) -> dict:
    """
    # 591租屋網 API 查詢

    輸入參數，可從 mongo DB 查出資料

    ## Args:

        - region_name: 縣市 (e.g. 台北市, 新北市)

        - phone/mobile: 聯絡電話

        - sex: 性別要求 (e.g. all_sex, boy, girl)

        - role_name: 出租者身分

        - linkman: 出租者

    ## Returns:

        - query status and result dictionary

    """
    args = {
        'region_name': region_name,
        'contact': contact,
        'sex_condition': sex_condition,
        'role_name': role_name,
        'linkman': linkman,
    }
    params = {k: v for k, v in args.items() if v}  # remove keys if values is empty
    try:
        return get_rent_data(params)
    except Exception as e:
        logger.exception(f"[ERROR]: params is: {params}, and type is: {type(params)}")
        logger.exception(e)
        return {'status': False, 'message': str(f'[ERROR], please check logger')}
