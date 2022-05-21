from ..wahu_core.core_exceptions import WahuRuntimeError
from ..wahu_core import WahuContext, wahu_methodize
class WahuConfigMethods:

    @wahu_methodize(middlewares=[])
    @staticmethod
    async def get_config(
        ctx: WahuContext, name: str
    ) -> str:

        if not hasattr(ctx.config, name):
            raise WahuRuntimeError(f'没有配置项 {name}')

        return str(getattr(ctx.config, name))
    