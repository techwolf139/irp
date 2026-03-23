from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from irp.models.fund import FundFlow, BudgetView


class FundSyncService:
    def __init__(self, db: AsyncSession, pms_client, oms_client, srm_client):
        self.db = db
        self.pms = pms_client
        self.oms = oms_client
        self.srm = srm_client

    async def sync_from_all_sources(self, start_date: date, end_date: date):
        await self.sync_from_srm(start_date, end_date)
        await self.sync_from_oms(start_date, end_date)
        await self.sync_from_pms(start_date, end_date)

    async def sync_from_srm(self, start_date, end_date):
        invoices = await self.srm.get_invoices(start_date=start_date, end_date=end_date)

        for invoice in invoices:
            flow = FundFlow(
                record_id=f"SRM-INV-{invoice.invoice_id}",
                date=invoice.invoice_date,
                type="支出",
                amount=invoice.amount,
                source_system="SRM",
                source_id=invoice.invoice_id,
                category="采购支出",
                supplier_id=invoice.supplier_id,
                contract_id=invoice.contract_id
            )
            self.db.add(flow)

        await self.db.commit()

    async def sync_from_oms(self, start_date, end_date):
        sales = await self.oms.get_sales(start_date=start_date, end_date=end_date)

        for sale in sales:
            flow = FundFlow(
                record_id=f"OMS-SALE-{sale.sale_id}",
                date=sale.sale_date,
                type="收入",
                amount=sale.amount,
                source_system="OMS",
                source_id=sale.sale_id,
                category="销售收入",
                project_id=sale.project_id
            )
            self.db.add(flow)

        await self.db.commit()

    async def sync_from_pms(self, start_date, end_date):
        budgets = await self.pms.get_budgets(start_date=start_date, end_date=end_date)

        for budget in budgets:
            existing = await self.db.execute(
                select(BudgetView).where(BudgetView.project_id == budget.project_id)
            )
            existing_budget = existing.scalar_one_or_none()

            if existing_budget:
                existing_budget.budget_total = budget.budget_total
                existing_budget.budget_spent = budget.budget_spent
                existing_budget.budget_committed = budget.budget_committed
            else:
                new_budget = BudgetView(
                    project_id=budget.project_id,
                    budget_total=budget.budget_total,
                    budget_spent=budget.budget_spent,
                    budget_committed=budget.budget_committed
                )
                self.db.add(new_budget)

        await self.db.commit()

    async def get_dashboard(self, group_by: str = "month") -> dict:
        income_result = await self.db.execute(
            select(func.sum(FundFlow.amount)).where(FundFlow.type == "收入")
        )
        total_income = income_result.scalar() or 0

        expense_result = await self.db.execute(
            select(func.sum(FundFlow.amount)).where(FundFlow.type == "支出")
        )
        total_expense = expense_result.scalar() or 0

        by_dimension = await self.get_breakdown(group_by)

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_flow": total_income - total_expense,
            "by_dimension": by_dimension
        }

    async def get_breakdown(self, group_by: str) -> dict:
        if group_by == "project":
            result = await self.db.execute(
                select(FundFlow.project_id, func.sum(FundFlow.amount))
                .group_by(FundFlow.project_id)
            )
            return {row[0]: row[1] for row in result.all() if row[0]}

        elif group_by == "supplier":
            result = await self.db.execute(
                select(FundFlow.supplier_id, func.sum(FundFlow.amount))
                .group_by(FundFlow.supplier_id)
            )
            return {row[0]: row[1] for row in result.all() if row[0]}

        elif group_by == "month":
            result = await self.db.execute(
                select(
                    func.date_trunc('month', FundFlow.date).label('month'),
                    func.sum(FundFlow.amount)
                ).group_by('month').order_by('month')
            )
            return {str(row[0]): row[1] for row in result.all()}

        return {}
