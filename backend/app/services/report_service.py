from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.report_repository import ReportRepository
from app.core.exceptions import BadRequestException


class ReportService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.report_repo = ReportRepository(db)

    # Validate date range
    def validate_date_range(
        self,
        start_date: date,
        end_date: date,
    ):
        if start_date > end_date:
            raise BadRequestException("Start date cannot be after end date")

    # Monthly report
    async def get_monthly_report(
        self,
        user_id: str,
        month: int,
        year: int,
    ):

        if month < 1 or month > 12:
            raise BadRequestException("Month must be between 1 and 12")

        if year < 2000:
            raise BadRequestException("Invalid year")

        start_date = date(year, month, 1)

        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        # Exclude the first day of the next month
        end_date = date.fromordinal(end_date.toordinal() - 1)

        summary = await self.report_repo.get_summary(user_id, start_date, end_date)

        return {
            **summary,
            "month": month,
            "year": year,
        }

    # Yearly report
    async def get_yearly_report(
        self,
        user_id: str,
        year: int,
    ):

        if year < 2000:
            raise BadRequestException("Invalid year")

        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        summary = await self.report_repo.get_summary(user_id, start_date, end_date)

        monthly_data = await self.report_repo.get_monthly_data(user_id, year)

        # Include months without transactions as zero
        monthly_lookup = {item["month"]: item for item in monthly_data}

        complete_monthly_data = []

        for month in range(1, 13):
            complete_monthly_data.append(
                monthly_lookup.get(
                    month,
                    {
                        "month": month,
                        "income": 0.0,
                        "expenses": 0.0,
                        "balance": 0.0,
                    },
                )
            )

        return {
            **summary,
            "year": year,
            "monthly_data": complete_monthly_data,
        }

    # Income report
    async def get_income_report(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):

        self.validate_date_range(start_date, end_date)

        return await self.report_repo.get_category_report(
            user_id,
            "income",
            start_date,
            end_date,
        )

    # Expense report
    async def get_expense_report(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):

        self.validate_date_range(start_date, end_date)

        return await self.report_repo.get_category_report(
            user_id,
            "expense",
            start_date,
            end_date,
        )

    # Category-wise spending report
    async def get_category_report(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):

        self.validate_date_range(start_date, end_date)

        return await self.report_repo.get_category_report(
            user_id,
            "expense",
            start_date,
            end_date,
        )

    # Payment method report
    async def get_payment_method_report(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):

        self.validate_date_range(start_date, end_date)

        return await self.report_repo.get_payment_method_report(
            user_id, start_date, end_date
        )

    # Custom date report
    async def get_custom_report(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
    ):

        self.validate_date_range(start_date, end_date)

        summary = await self.report_repo.get_summary(user_id, start_date, end_date)

        return {
            **summary,
            "start_date": start_date,
            "end_date": end_date,
        }
