from wahu_backend.wahu_core.wahu_context import WahuContext
from .illust_database import _check_db_name
from ..wahu_core import wahu_methodize
from ..illust_bookmarking.subscription import DatabaseSubscription

class WahuIdbSubscriptionMethods:

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibdsubs_update(
        cls,
        ctx: WahuContext,
        name: str
    ) -> None:
        await ctx.ibdsub_man.update_subscriptions(name)
    
    @classmethod
    @wahu_methodize()
    async def ibdsubs_get(cls, ctx: WahuContext) -> list[DatabaseSubscription]:
        return list(ctx.ibdsub_man.subscriptions.values())
    