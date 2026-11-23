from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.dependencies import get_current_user

from app.services.export_service import ExportService

router = APIRouter(
    prefix="/exports",
    tags=["Exports"],
)


# Export transactions as CSV
@router.get("/transactions/csv")
async def export_transactions_csv(
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ExportService(db)

    csv_content = await service.export_csv(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="transactions.csv"'},
    )


# Export transactions as Excel
@router.get("/transactions/excel")
async def export_transactions_excel(
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ExportService(db)

    excel_content = await service.export_excel(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="transactions.xlsx"'},
    )


# Export monthly financial report as PDF
@router.get("/reports/monthly/pdf")
async def export_monthly_report_pdf(
    month: int = Query(ge=1, le=12),
    year: int = Query(ge=2000, le=9999),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ExportService(db)

    pdf_content = await service.export_monthly_pdf(
        user_id=current_user.id,
        month=month,
        year=year,
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="monthly-report.pdf"'},
    )


# Export custom date-range report as PDF
@router.get("/reports/custom/pdf")
async def export_custom_report_pdf(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ExportService(db)

    pdf_content = await service.export_pdf(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="custom-report.pdf"'},
    )
