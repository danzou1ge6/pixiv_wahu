import dataclasses
from pathlib import Path

import toml

from ..aiopixivpy import IllustTag, IllustDetail
from ..logistic_regression import apply_model


@dataclasses.dataclass(slots=True)
class WeighedIllustTag(IllustTag):
    weight: float


@dataclasses.dataclass
class TagRegressionModel:
    weighed_tags: list[WeighedIllustTag]
    bias: float


def dump_tag_model(
    file_path: Path, model: TagRegressionModel
) -> None:
    """
    保存 tag 逻辑回归模型到 toml 文件
    """

    d = {
        'weight': [dataclasses.asdict(tag) for tag in model.weighed_tags],
        'bias': model.bias
    }

    with open(file_path, 'w', encoding='utf-8') as wf:
        wf.write(toml.dumps(d))

def load_tag_model(
    file_path: Path
) -> TagRegressionModel:
    """从 toml 文件加载逻辑回归模型"""

    with open(file_path, 'r', encoding='utf-8') as rf:
        d = toml.loads(rf.read())

    weighed_tags = [
        WeighedIllustTag(**wit)
        for wit in d['weight']
    ]

    return TagRegressionModel(weighed_tags, d['bias'])

def process_illusts(
    model: TagRegressionModel, illusts: list[IllustDetail]
) -> list[float]:
    """
    根据模型计算若干插画的分类预测值

    预测值越接近 1 ，则插画在正类别中的概率越大
    """

    tag_groups = (ilst.tags for ilst in illusts)

    x_list = [
        [1. if tag in tag_group else 0. for tag in model.weighed_tags]
        for tag_group in tag_groups
    ]

    weights = [wt.weight for wt in model.weighed_tags]

    predict = apply_model(x_list, weights, model.bias)

    return predict
