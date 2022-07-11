import random
from typing import Iterator

from .simple_mat import Mat, many, exp_mat, log_mat  # type: ignore


def sigmoid(x: Mat) -> Mat:
    return 1. / (exp_mat(0. - x) + 1.)


def cross_entrophy(y: Mat, p: Mat) -> float:
    """
    交叉熵损失函数

    `y`: 目标值 dim1: 样本 dim2: 1
    `p`: 预测值 dim 同 `y`
    """
    return - (
        y.T.dot(log_mat(p))[0, 0] + (1. - y).T.dot(log_mat(1. - p))[0, 0]
    )


def accuracy(y: Mat, p: Mat) -> float:
    """
    计算准确率
    参数同 `cross_entrophy`
    """

    right = [not (p[i, 0] > 0.5) ^ (y[i, 0] == 1.) for i in range(y.rows)]

    total = sum(right)

    return total / y.rows


class DataSet:
    """
    储存数据集
    """

    def __init__(self, x: list[list[float]], y: list[float], shuffle: bool=True):
        """
        `x`: x 样本列表 dim1: 样本 dim2: 特征
        `y`: y 样本列表
        """
        if len(x) != len(y):
            raise ValueError(f'x 样本数 ({len(x)}) != y 样本数 ({len(y)})')

        if shuffle:
            shuffled = list(zip(x, y))
            random.shuffle(shuffled)

            self.x = [s[0] for s in shuffled]
            self.y = [s[1] for s in shuffled]
        else:
            self.x = x
            self.y = y

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, slc: slice) -> tuple[list[list[float]], list[float]]:
        return (self.x[slc], self.y[slc])

    def split(self, ratio: float) -> tuple['DataSet', 'DataSet']:
        if not 0 < ratio < 1:
            raise ValueError('ratio 应在 (0, 1) 中')

        num_1 = int(ratio * len(self))

        return (
            DataSet(self.x[:num_1], self.y[:num_1], shuffle=False),
            DataSet(self.x[num_1:], self.y[num_1:], shuffle=False)
        )


class DataLoader:
    """
    按某个批大小加载数据
    """

    def __init__(self, dataset: DataSet, batch_size: int):

        self.dataset = dataset
        self.batch_size = batch_size
        self.pointer = 0

    def __next__(self) -> tuple[Mat, Mat]:
        """
        返回
        `x`: dim1: batch_size dim2: 特征
        `y`: dim1: batch_size dim2: 1
        """

        if self.pointer + self.batch_size <= len(self.dataset):
            x_list, y_list = self.dataset[self.pointer:self.pointer + self.batch_size]

        else:
            x_list, y_list = self.dataset[self.pointer:]
            self.pointer = 0

        x = Mat(lst=x_list)
        y = Mat(lst=[y_list]).T

        return x, y

    def __iter__(self) -> Iterator:
        return self


def logistic_regression_epoch(
    omega: Mat,
    bias: float,
    x: Mat,
    y: Mat,
    lr: float = 0.1,
) -> tuple[Mat, float, float]:
    """
    进行一次逻辑回归

    返回：
    `omega`: 参数矩阵 dim1: 特征 dim2: 1
    `bias`: 偏置
    """

    z = x.dot(omega) + bias  # dim1: 样本 dim2: 1
    p = sigmoid(z)  # dim1: 样本 dim2: 1

    loss: float = cross_entrophy(y, p)

    g_omega = ((p - y).T.dot(x)).T / float(x.rows)  # dim1: 特征 dim2: 1
    omega = omega - g_omega * lr

    g_b: float = (p - y).average(axis=1)[0, 0]
    bias -= g_b * lr

    return omega, bias, loss


def logistic_regression_test(
    omega: Mat,
    bias: float,
    x: Mat,
    y: Mat,
) -> float:
    """
    将逻辑回归模型进行测试

    返回正确率
    """

    z = x.dot(omega) + bias
    p = sigmoid(z)

    return accuracy(y, p)


def apply_model(
    x_list: list[list[float]],
    weights: list[float],
    bias: float
) -> list[float]:

    x = Mat(lst=x_list)
    omega = Mat(lst=[weights]).T

    z = x.dot(omega) + bias
    p = sigmoid(z)

    return p.T.as_list()[0]

