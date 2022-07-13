import itertools
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, AsyncGenerator, Optional, Type, TypeVar


from ..aiopixivpy import IllustTag
from ..logistic_regression import (DataLoader, DataSet,
                                   logistic_regression_epoch,
                                   logistic_regression_test, simple_mat)
from ..wahu_core import (GenericWahuMethod, WahuArguments, WahuContext,
                         wahu_methodize)
from ..wahu_core.core_exceptions import WahuRuntimeError
from .lib_tag_utils import TagRegressionModel, WeighedIllustTag, dump_tag_model

if TYPE_CHECKING:
    from . import WahuMethods


RT = TypeVar('RT')
def _check_dbnames_factory(
    *arg_names: str
):
    """
    检查数据库名的中间件工厂函数

    `arg_names`: WahuMethod 的参数名，该参数可以是 list 也可以是 str
    """

    async def f(
        m: GenericWahuMethod[RT],
        cls: Type['WahuMethods'],
        args: WahuArguments,
        ctx: WahuContext
    ) -> RT:

        for name in arg_names:

            if name not in args:
                raise WahuRuntimeError(f'_check_dbnames：未提供数据库名参数 {name}')

            if isinstance(args[name], str):
                args[name] = [args[name]]

            for db_name in args[name]:

                if db_name not in ctx.ilst_bmdbs.keys():
                    raise WahuRuntimeError(f'_check_db_name: 数据库名 {args.name} 不在上下文中')

        return await m(cls, args, ctx)

    return f

async def get_tag_groups(ctx: WahuContext, *names: str) -> list[list[IllustTag]]:

    tag_groups: list[list[IllustTag]] = []

    for name in names:
        with await ctx.ilst_bmdbs[name](readonly=True) as ibd:

            tag_groups += [r[0] for r in ibd.illusts_te.select_cols(cols=['tags'])]

    return tag_groups


@dataclass(slots=True)
class CountedIllustTag(IllustTag):
    count: int


class WahuTagStatisticMethods:

    @classmethod
    @wahu_methodize(middlewares=[_check_dbnames_factory('names')])
    async def ibdtag_count(
        cls, ctx: WahuContext, names: list[str]
    ) -> list[CountedIllustTag]:
        """
        对若干个插画数据库中的标签进行计数

        返回：[(IllustTag，次数), ...]
        """

        tags: list[IllustTag] = []

        for name in names:
            with await ctx.ilst_bmdbs[name](readonly=True) as ibd:

                tags += itertools.chain(
                    *(r[0] for r in ibd.illusts_te.select_cols(cols=['tags']))
                )

        cntr = Counter(tags)

        result = cntr.most_common()

        return [CountedIllustTag(tag.name, tag.translated, count)
                for tag, count in result]

    @classmethod
    @wahu_methodize(middlewares=[_check_dbnames_factory('pos', 'neg')])
    async def ibdtag_logistic_regression(
        cls,
        ctx: WahuContext,
        pos: list[str],
        neg: list[str],
        tags: list[IllustTag],
        lr: float,
        batch_size: int,
        epoch: int,
        test_set_ratio: float
    ) -> AsyncGenerator[
            tuple[tuple[int, int],  # 进度
            Optional[tuple[list[float], list[float], TagRegressionModel]]
            # ( 训练损失，测试集正确率，模型 )
        ], None]:
        """
        以若干插画数据库为正 (`pos`) 负 (`neg`) 样本进行逻辑回归

        `tags`: 要进行统计的标签集
        `lr`: 学习率
        `batch_size`: 批处理「批大小」占「总样本数」的比率
        `epoch`: 迭代数
        `test_set_ratio`: 测试集占比
        `report_interval`: 报告学习情况的间隔迭代数

        返回:
        `train_gen`: 训练时报告，异步生成器，返回 训练损失 和 测试集正确率
        `model_gen`: 当训练结束后返回模型
        """

        pos_tag_groups = await get_tag_groups(ctx, *pos)
        neg_tag_groups = await get_tag_groups(ctx, *neg)

        x_list = [
            [1. if tag in tag_group else 0. for tag in tags]
            for tag_group in pos_tag_groups
        ] + [
            [1. if tag in tag_group else 0. for tag in tags]
            for tag_group in neg_tag_groups
        ]

        y_list = [
            1. for _ in range(len(pos_tag_groups))
        ] + [
            0. for _ in range(len(neg_tag_groups))
        ]

        root_dataset = DataSet(x_list, y_list, shuffle=True)
        test_ds, train_ds = root_dataset.split(test_set_ratio)
        test_dl = DataLoader(test_ds, batch_size=len(test_ds))
        train_dl = DataLoader(train_ds, batch_size=batch_size)

        omega = simple_mat.many(len(x_list[0]), 1, 0.)  # dim1: 特征 dim2: 1
        bias = 0.

        report_interval = int(epoch / 100) + 1

        async def train_gen():
            nonlocal omega, bias

            loss_list: list[float] = []
            accu_list: list[float] = []

            for i, (x, y) in enumerate(train_dl):
                if i == epoch:
                    break

                omega, bias, loss = logistic_regression_epoch(
                    omega, bias, x, y, lr
                )

                if i % report_interval == 0:
                    test_x, test_y = next(test_dl)
                    accuracy = logistic_regression_test(
                        omega, bias, test_x, test_y
                    )

                    loss_list.append(loss)
                    accu_list.append(accuracy)

                    yield (i, epoch), None


            weighed_tags = [
                WeighedIllustTag(tag.name, tag.translated, omega[i, 0])
                for i, tag in enumerate(tags)
            ]
            weighed_tags.sort(key=lambda item: item.weight, reverse=True)

            yield (epoch, epoch), (loss_list, accu_list, TagRegressionModel(weighed_tags, bias))

        return train_gen()


    @classmethod
    @wahu_methodize()
    async def ibdtag_write_model(
        cls, ctx: WahuContext,
        model: TagRegressionModel,
        model_name: str
    ) -> None:
        """
        将逻辑回归得到模型保存到文件中
        """

        dump_tag_model(
            ctx.config.tag_model_dir / (model_name + '.toml'),
            model
        )

