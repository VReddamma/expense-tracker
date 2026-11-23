import csv
from io import StringIO, BytesIO
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.repositories.export_repository import ExportRepository
from app.repositories.report_repository import ReportRepository
from app.core.exceptions import BadRequestException


class ExportService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.export_repo = ExportRepository(db)
        self.report_repo = ReportRepository(db)

    # Validate date range
    def validate_date_range(self, start_date: date | None, end_date: date | None):
        if start_date and end_date and start_date > end_date:
            raise BadRequestException("Start date cannot be after end date")

    # Get export headers
    def get_headers(self):
        return [
            "Transaction ID",
            "Title",
            "Category",
            "Type",
            "Amount",
            "Transaction Date",
            "Payment Method",
            "Notes",
        ]

    # Get transaction values
    def get_transaction_values(self, transaction):
        return [
            transaction["id"],
            transaction["title"],
            transaction["category_name"] or "Uncategorized",
            transaction["type"],
            str(transaction["amount"]),
            str(transaction["transaction_date"]),
            transaction["payment_method"] or "",
            transaction["notes"] or "",
        ]

    # Export transactions to CSV
    async def export_csv(
        self, user_id: str, start_date: date | None = None, end_date: date | None = None
    ):

        self.validate_date_range(start_date, end_date)

        transactions = await self.export_repo.get_transactions(
            user_id, start_date, end_date
        )

        output = StringIO()
        writer = csv.writer(output)

        # Add column headers
        writer.writerow(self.get_headers())

        # Add transaction records
        for transaction in transactions:
            writer.writerow(self.get_transaction_values(transaction))

        # Return CSV as bytes
        return output.getvalue().encode("utf-8-sig")

    # Export transactions to Excel
    async def export_excel(
        self, user_id: str, start_date: date | None = None, end_date: date | None = None
    ):

        self.validate_date_range(start_date, end_date)

        transactions = await self.export_repo.get_transactions(
            user_id, start_date, end_date
        )

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Transactions"

        # Add column headers
        headers = self.get_headers()
        worksheet.append(headers)

        # Style column headers
        for cell in worksheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color="2563EB", end_color="2563EB", fill_type="solid"
            )
            cell.alignment = Alignment(horizontal="center")

        # Add transaction records
        for transaction in transactions:
            values = self.get_transaction_values(transaction)

            # Prevent spreadsheet formula injection
            safe_values = [
                (
                    "'" + value
                    if isinstance(value, str) and value.startswith(("=", "+", "-", "@"))
                    else value
                )
                for value in values
            ]

            worksheet.append(safe_values)

        # Adjust column widths
        column_widths = [38, 25, 20, 15, 15, 20, 20, 35]

        for index, width in enumerate(column_widths, start=1):
            worksheet.column_dimensions[
                worksheet.cell(row=1, column=index).column_letter
            ].width = width

        # Freeze header row
        worksheet.freeze_panes = "A2"

        # Save workbook into memory
        output = BytesIO()
        workbook.save(output)

        return output.getvalue()

    # Export transactions to PDF
    async def export_pdf(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        title: str = "Transaction Report",
    ):

        self.validate_date_range(start_date, end_date)

        transactions = await self.export_repo.get_transactions(
            user_id, start_date, end_date
        )

        summary = await self.report_repo.get_summary(user_id, start_date, end_date)

        output = BytesIO()

        document = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=25,
            leftMargin=25,
            topMargin=25,
            bottomMargin=25,
        )

        styles = getSampleStyleSheet()
        elements = []

        # Add report title
        elements.append(Paragraph(title, styles["Title"]))

        elements.append(Spacer(1, 15))

        # Add report date range
        elements.append(
            Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"])
        )

        elements.append(Spacer(1, 15))

        # Add summary information
        summary_data = [
            ["Total Income", "Total Expenses", "Net Savings"],
            [
                str(summary["total_income"]),
                str(summary["total_expenses"]),
                str(
                    Decimal(str(summary["total_income"]))
                    - Decimal(str(summary["total_expenses"]))
                ),
            ],
        ]

        summary_table = Table(summary_data)

        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Add transaction table
        table_data = [["Title", "Category", "Type", "Amount", "Date", "Payment Method"]]

        for transaction in transactions:
            table_data.append(
                [
                    str(transaction["title"]),
                    str(transaction["category_name"] or "Uncategorized"),
                    str(transaction["type"]),
                    str(transaction["amount"]),
                    str(transaction["transaction_date"]),
                    str(transaction["payment_method"] or ""),
                ]
            )

        transaction_table = Table(table_data, repeatRows=1)

        transaction_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elements.append(transaction_table)

        # Generate PDF
        document.build(elements)

        return output.getvalue()

    # Export monthly report to PDF
    async def export_monthly_pdf(self, user_id: str, month: int, year: int):

        if month < 1 or month > 12:
            raise BadRequestException("Month must be between 1 and 12")

        if year < 2000 or year > 9999:
            raise BadRequestException("Year must be between 2000 and 9999")

        # Get first and last day of the month
        import calendar

        start_date = date(year, month, 1)

        last_day = calendar.monthrange(year, month)[1]

        end_date = date(year, month, last_day)

        # Generate monthly PDF
        return await self.export_pdf(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            title=f"Monthly Expense Report - {month}/{year}",
        )
