from wahu_backend.wahu_core.wahu_context import WahuContext
from .illust_database import _check_db_name
from ..wahu_core import wahu_methodize

class WahuIdbSubscriptionMethods:

    @classmethod
    @wahu_methodize(middlewares=[_check_db_name])
    async def ibdsubs_update(
        cls,
        ctx: WahuContext,
        name: str
    ) -> None:
        await ctx.ibdsub_man.update_subscriptions(name)
    