"""
排课周期路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.cycle import SchedulingCycle, CycleDate, TimeSlot
from app.schemas.schedule import CycleCreate, CycleUpdate, CycleResponse, CycleDateResponse, TimeSlotCreate, TimeSlotUpdate, TimeSlotResponse
from app.schemas.base import ResponseBase, PaginatedResponse
from app.services.auth import require_role, get_current_user, check_org_access

router = APIRouter()


# ============ 排课周期 ============
@router.get("", response_model=PaginatedResponse[CycleResponse])
async def list_cycles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取排课周期列表"""
    query = db.query(SchedulingCycle)

    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(SchedulingCycle.org_id == org_id)
    else:
        query = query.filter(SchedulingCycle.org_id == current_user.org_id)

    if is_active is not None:
        query = query.filter(SchedulingCycle.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[CycleResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=ResponseBase[CycleResponse])
async def create_cycle(
    request: CycleCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建排课周期"""
    # 确定机构ID
    if current_user.role == UserRole.SUPER_ADMIN:
        org_id = request.org_id
    else:
        org_id = current_user.org_id

    if not org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    cycle = SchedulingCycle(
        org_id=org_id,
        name=request.name,
        cycle_days=request.cycle_days,
        start_date=request.start_date,
        end_date=request.end_date,
        description=request.description
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)

    return ResponseBase(
        data=CycleResponse.model_validate(cycle),
        message="排课周期创建成功"
    )


@router.post("/{cycle_id}/generate-dates", response_model=ResponseBase[List[CycleDateResponse]])
async def generate_cycle_dates(
    cycle_id: int,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """生成周期日期映射"""
    cycle = db.query(SchedulingCycle).filter(SchedulingCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="排课周期不存在")

    if not check_org_access(current_user, cycle.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    # 清除旧映射
    db.query(CycleDate).filter(CycleDate.cycle_id == cycle_id).delete()

    # 生成日期映射
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else cycle.end_date
    if not end:
        # 默认生成3个月的映射
        end = cycle.start_date + timedelta(days=90)

    dates = []
    current_date = cycle.start_date
    cycle_day = 1

    while current_date <= end:
        cycle_date = CycleDate(
            cycle_id=cycle_id,
            cycle_day=cycle_day,
            actual_date=current_date
        )
        db.add(cycle_date)
        dates.append(cycle_date)

        cycle_day = (cycle_day % cycle.cycle_days) + 1
        current_date += timedelta(days=1)

    db.commit()

    return ResponseBase(
        data=[CycleDateResponse.model_validate(d) for d in dates],
        message=f"已生成 {len(dates)} 天的周期映射"
    )


@router.get("/{cycle_id}/dates", response_model=ResponseBase[List[CycleDateResponse]])
async def get_cycle_dates(
    cycle_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取周期日期映射"""
    cycle = db.query(SchedulingCycle).filter(SchedulingCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="排课周期不存在")

    if not check_org_access(current_user, cycle.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    query = db.query(CycleDate).filter(CycleDate.cycle_id == cycle_id)

    if start_date:
        query = query.filter(CycleDate.actual_date >= start_date)
    if end_date:
        query = query.filter(CycleDate.actual_date <= end_date)

    dates = query.order_by(CycleDate.actual_date).all()

    return ResponseBase(data=[CycleDateResponse.model_validate(d) for d in dates])


# ============ 时间段 ============
@router.get("/time-slots", response_model=ResponseBase[List[TimeSlotResponse]])
async def list_time_slots(
    org_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取时间段列表"""
    query = db.query(TimeSlot)

    if current_user.role == UserRole.SUPER_ADMIN:
        if org_id:
            query = query.filter(TimeSlot.org_id == org_id)
    else:
        query = query.filter(TimeSlot.org_id == current_user.org_id)

    slots = query.filter(TimeSlot.is_active == True).order_by(TimeSlot.display_order).all()

    return ResponseBase(data=[TimeSlotResponse.model_validate(s) for s in slots])


@router.post("/time-slots", response_model=ResponseBase[TimeSlotResponse])
async def create_time_slot(
    request: TimeSlotCreate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """创建时间段"""
    # 确定机构ID
    if current_user.role == UserRole.SUPER_ADMIN:
        org_id = request.org_id
    else:
        org_id = current_user.org_id

    if not org_id:
        raise HTTPException(status_code=400, detail="需要指定机构ID")

    slot = TimeSlot(
        org_id=org_id,
        name=request.name,
        start_time=request.start_time,
        end_time=request.end_time,
        display_order=request.display_order
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)

    return ResponseBase(
        data=TimeSlotResponse.model_validate(slot),
        message="时间段创建成功"
    )


@router.put("/time-slots/{slot_id}", response_model=ResponseBase[TimeSlotResponse])
async def update_time_slot(
    slot_id: int,
    request: TimeSlotUpdate,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: Session = Depends(get_db)
):
    """更新时间段"""
    slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="时间段不存在")

    if not check_org_access(current_user, slot.org_id):
        raise HTTPException(status_code=403, detail="无权访问")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(slot, key, value)

    db.commit()
    db.refresh(slot)

    return ResponseBase(
        data=TimeSlotResponse.model_validate(slot),
        message="时间段更新成功"
    )