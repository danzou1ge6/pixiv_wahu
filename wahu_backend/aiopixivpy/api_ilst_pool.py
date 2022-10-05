from .api_base import BasePixivAPI, check_login
from .datastructure_illust import IllustDetail
from .datastructure_processing import process_pixiv_illust_dict


class IllustPoolAPI(BasePixivAPI):

    # 插画详情池
    def _pool_push_illust(self, ilst_detail: IllustDetail) -> None:

        if ilst_detail.iid not in self.ilst_pool.keys():
            if len(self.ilst_pool) >= self.ilst_pool_size:
                self.ilst_pool.popitem(last=False)

            self.ilst_pool[ilst_detail.iid] = ilst_detail

    async def pool_illust_detail(self, iid: int) -> IllustDetail:
        if iid in self.ilst_pool.keys():
            return self.ilst_pool[iid]

        ilst_detail = await self.illust_detail(iid)

        self._pool_push_illust(ilst_detail)

        return ilst_detail

    @check_login
    async def illust_detail(self, iid: int) -> IllustDetail:
        """插画详情"""

        pixiv_ret = await self.get_json(
            'v1/illust/detail',
            params={'illust_id': iid}
        )

        dtl = process_pixiv_illust_dict(pixiv_ret['illust'])  # type: ignore
        self._pool_push_illust(dtl)

        return dtl

