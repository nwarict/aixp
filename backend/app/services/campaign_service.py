from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.contact import Contact
from app.tasks.celery_tasks import send_campaign_message

class CampaignService:
    async def execute_campaign(self, db: AsyncSession, campaign_id: str) -> dict:
        """Execute a campaign by sending messages to all recipients."""
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()

        if not campaign:
            return {"error": "Campaign not found"}

        if campaign.status != "scheduled":
            return {"error": "Campaign is not scheduled"}

        # Get recipients
        recipients = await self._get_recipients(db, campaign)
        campaign.total_recipients = len(recipients)
        campaign.status = "running"
        campaign.sent_count = 0
        await db.commit()

        # Queue messages for sending
        for recipient in recipients:
            send_campaign_message.delay(
                campaign_id=campaign.id,
                tenant_id=campaign.tenant_id,
                channel=campaign.channel,
                recipient_id=recipient["id"],
                recipient_value=recipient["value"],
                content=campaign.content
            )

        return {"message": f"Campaign queued with {len(recipients)} recipients"}

    async def _get_recipients(self, db: AsyncSession, campaign: Campaign) -> List[dict]:
        """Get list of recipients based on audience type."""
        recipients = []

        if campaign.audience_type == "all":
            result = await db.execute(
                select(Customer).where(
                    Customer.tenant_id == campaign.tenant_id,
                    Customer.is_deleted == False,
                    Customer.status == "active"
                )
            )
            customers = result.scalars().all()
            for customer in customers:
                result_contact = await db.execute(
                    select(Contact).where(
                        Contact.customer_id == customer.id,
                        Contact.type == campaign.channel
                    )
                )
                contact = result_contact.scalar_one_or_none()
                if contact:
                    recipients.append({"id": customer.id, "value": contact.value})

        elif campaign.audience_type == "segment":
            # Apply segment filters
            segment = campaign.audience_segment
            query = select(Customer).where(
                Customer.tenant_id == campaign.tenant_id,
                Customer.is_deleted == False
            )
            if "tags" in segment:
                from sqlalchemy import any_
                query = query.where(Customer.tags.contains(segment["tags"]))
            if "status" in segment:
                query = query.where(Customer.status == segment["status"])

            result = await db.execute(query)
            customers = result.scalars().all()
            for customer in customers:
                result_contact = await db.execute(
                    select(Contact).where(
                        Contact.customer_id == customer.id,
                        Contact.type == campaign.channel
                    )
                )
                contact = result_contact.scalar_one_or_none()
                if contact:
                    recipients.append({"id": customer.id, "value": contact.value})

        elif campaign.audience_type == "manual":
            for customer_id in campaign.audience_manual:
                result = await db.execute(
                    select(Contact).where(
                        Contact.customer_id == customer_id,
                        Contact.type == campaign.channel
                    )
                )
                contact = result_contact.scalar_one_or_none()
                if contact:
                    recipients.append({"id": customer_id, "value": contact.value})

        return recipients
