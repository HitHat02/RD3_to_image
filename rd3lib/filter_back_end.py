import numpy as np
import cv2
import time

from scipy import special

def logging_time(original_fn):
    """
    필터 함수가 실행되는 데 걸리는 시간을 출력하는 데코레이터입니다.

    :param original_fn: 데코레이팅할 원본 함수
    :type original_fn: function
    :return: 실행 시간을 출력한 뒤 결과를 반환하는 래퍼 함수
    :rtype: function
    """
    def wrapper_fn(*args, **kwargs):
        start_time = time.time()
        result = original_fn(*args, **kwargs)
        end_time = time.time()
        print("WorkingTime[{}]: {} sec".format(original_fn.__name__, end_time-start_time))
        return result
    return wrapper_fn

class Gain():
    """
        GPR 데이터에 대해 감쇠 곡선을 적용하는 Gain 필터 클래스입니다.
    """
    def __init__(self):

        self.y_inter = 0.80  # default : 0.80   3.0
        self.grad_const = 10  # default : 10.0  5
        self.inflection_point = 127  # default : 127
        self.inflection_range = 60  # default : 60

    def Curve(self, x):
        """
        감쇠 곡선을 정의하는 함수로, erf 함수를 기반으로 계산합니다.

        :param x: 위치 값 (1차원)
        :type x: numpy.ndarray
        :return: 감쇠 계수 배열
        :rtype: numpy.ndarray
        """
        return (special.erf((x - self.inflection_point) / self.inflection_range) + 1) * self.grad_const + self.y_inter

    @logging_time
    def Gain(self, x):
        """
        Gain 필터를 적용하여 입력 데이터를 보정합니다.

        :param x: 입력 GPR 데이터 (3차원)
        :type x: numpy.ndarray
        :return: Gain 필터가 적용된 데이터
        :rtype: numpy.ndarray
        """
        z = np.int16(self.Curve(np.arange(x.shape[1])))
        z = np.vstack(([z] * x.shape[0]))
        z = np.dstack(([z] * x.shape[2]))
        x *= z

        return np.int16(x)


class Range():
    """
    입력값을 지정된 범위로 클리핑하는 필터 클래스입니다.
    """
    def __init__(self):

        self.range_vaule = 5000  # default : 5000

    @logging_time
    def Range(self, x):
        """
        -range_value ~ +range_value 사이로 데이터를 제한합니다.

        :param x: 입력 GPR 데이터
        :type x: numpy.ndarray
        :return: 클리핑된 데이터
        :rtype: numpy.ndarray
        """
        x = np.where(x <= self.range_vaule, x, self.range_vaule)
        x = np.where(x >= -self.range_vaule, x, -self.range_vaule)

        return np.int16(x)


class Las():
    """
    LAS 필터 (Local Adaptive Signal filter)를 적용하여 고주파 노이즈를 제거합니다.
    """
    def __init__(self):

        self.las_ratio = 0.98  # default : 1.0
        self.sigmaNumber = 50  # default : 100
        self.sigma_constants = 0.16  # default : 0.16

    @logging_time
    def Las(self,x):
        """
        가우시안 커널을 사용하여 국소 평균을 구하고 비선형적으로 노이즈를 제거합니다.

        :param x: 입력 GPR 데이터
        :type x: numpy.ndarray
        :return: LAS 필터 적용된 데이터
        :rtype: numpy.ndarray
        """
        sigma = self.sigmaNumber * self.sigma_constants
        kernel = cv2.getGaussianKernel(round(self.sigmaNumber), sigma)
        las_npy = cv2.filter2D(x.T, -1, kernel) + 0.001
        x = x - las_npy.T / (
                    (las_npy.T ** 2) ** ((1.0001 - self.las_ratio) / 2))

        return np.int16(x)

class edge():
    """
    특정 임계값 이상의 edge 신호만 남기는 필터입니다.
    """
    def __init__(self):
        self.edge_range = 1000

    @logging_time
    def edge(self,x):
        """
        edge_range를 기준으로 이상값만 유지하고 나머지는 0으로 설정합니다.

        :param x: 입력 데이터
        :type x: numpy.ndarray
        :return: edge 필터 적용 결과
        :rtype: numpy.ndarray
        """
        x = np.where(((x >= self.edge_range) | (x <= -self.edge_range)), x, 0)
        return np.int16(x)

class average():
    """
    이동 평균 필터를 적용하는 클래스입니다.
    """
    def __init__(self):
        self.depth = 3
        self.dist = 3

    @logging_time
    def average(self, x):
        """
        지정된 depth, dist 크기로 평균 필터를 적용합니다.

        :param x: 입력 GPR 데이터
        :type x: numpy.ndarray
        :return: 평균 필터가 적용된 데이터
        :rtype: numpy.ndarray
        """
        print(self.depth, self.dist)
        kernel = np.ones((self.depth, self.dist))/(self.depth*self.dist)
        blured = np.empty((x.shape))
        for i in range(x.shape[0]):
            blured[i] = cv2.filter2D(x[i], -1, kernel)

        return np.int16(blured)

class y_differential():
    """
    Y축 방향 미분을 수행하는 필터입니다.
    """
    def __init__(self):
        self.y_window_para = 1

    def y_differential(self, x):
        """
        y_window_para 크기의 창을 사용하여 y축 방향 차분을 계산합니다.

        :param x: 입력 GPR 데이터
        :type x: numpy.ndarray
        :return: Y 방향 미분 결과
        :rtype: numpy.ndarray
        """
        diff = np.zeros((x.shape))
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                diff[i, j, 0:-1] = np.convolve(x[i, j, 1:], np.ones(self.y_window_para)/self.y_window_para, mode='same')\
                                 - np.convolve(x[i, j, :-1], np.ones(self.y_window_para)/self.y_window_para, mode='same')
        return np.int16(diff)


class z_differential():
    """
    Z축 방향 미분을 수행하는 필터입니다.
    """
    def __init__(self):
        self.z_window_para = 1

    def z_differential(self, x):
        """
        z_window_para 크기의 창을 사용하여 z축 방향 차분을 계산합니다.

        :param x: 입력 GPR 데이터
        :type x: numpy.ndarray
        :return: Z 방향 미분 결과
        :rtype: numpy.ndarray
        """
        diff = np.zeros((x.shape))
        for i in range(x.shape[0]):
            for k in range(x.shape[2]):
                diff[i, :-1, k] = (np.convolve(x[i, 1:, k], np.ones(self.z_window_para) / self.z_window_para, mode='same')\
                                   - np.convolve(x[i, :-1, k], np.ones(self.z_window_para) / self.z_window_para, mode='same'))
        return np.int16(diff)

class sign_smoother():
    """
    GPR 데이터의 신호 부호(양/음)를 기준으로 경계 및 노이즈를 부드럽게 처리하는 필터입니다.
    """
    def run_with_npy(self, x):
        """
        사전 정의된 방식으로 SIGN 및 ZERO 스무딩을 단계적으로 적용합니다.

        :param x: 입력 3차원 데이터
        :type x: numpy.ndarray
        :return: 스무딩 처리된 데이터
        :rtype: numpy.ndarray
        """
        for The_number_of_consideration_for_one_direction1 in range(1, 2):
            for The_number_of_consideration_for_one_direction2 in range(3, 4):
                for The_number_of_consideration_for_one_direction3 in range(2, 3):

                    if The_number_of_consideration_for_one_direction1 != 0:
                        # SIGN_SMOOTHER
                        n = The_number_of_consideration_for_one_direction1
                        npy_ori = x
                        npy = np.zeros((len(npy_ori) + 2 * n, len(npy_ori[0]) + 2 * n, len(npy_ori[0, 0]) + 2 * n))
                        npy = np.int16(npy)
                        for i in range(0, n):
                            npy[i, n:-n, n:-n] = npy_ori[0]
                            npy[-(i + 1), n:-n, n:-n] = npy_ori[-1]
                        npy[n:-n, n:-n, n:-n] = npy_ori
                        npy[np.where(npy > 0)] = 2
                        npy[np.where(npy < 0)] = -2
                        for d in [4, 10, 12]:
                            npy[n:-n, n:-n, n:-n] = self.SIGN_SMOOTHER(self.SLICING(npy, n, d))

                    if The_number_of_consideration_for_one_direction2 != 0:
                        # ZERO_SMOOTHER
                        npy_ori = npy[n:-n, n:-n, n:-n]
                        n = The_number_of_consideration_for_one_direction2
                        npy = np.zeros((len(npy_ori) + 2 * n, len(npy_ori[0]) + 2 * n, len(npy_ori[0, 0]) + 2 * n))
                        npy = np.int16(npy)
                        for i in range(0, n):
                            npy[i, n:-n, n:-n] = npy_ori[0]
                            npy[-(i + 1), n:-n, n:-n] = npy_ori[-1]
                        npy[n:-n, n:-n, n:-n] = npy_ori
                        npy[np.where(npy > 0)] = 103
                        npy[np.where(npy < 0)] = -3
                        for d in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                            npy[n:-n, n:-n, n:-n] = self.ZERO_SMOOTHER(self.SLICING(npy, n, d))

                    if The_number_of_consideration_for_one_direction3 != 0:
                        # ZERO_SMOOTHER
                        npy_ori = npy[n:-n, n:-n, n:-n]
                        n = The_number_of_consideration_for_one_direction3
                        npy = np.zeros((len(npy_ori) + 2 * n, len(npy_ori[0]) + 2 * n, len(npy_ori[0, 0]) + 2 * n))
                        npy = np.int16(npy)
                        for i in range(0, n):
                            npy[i, n:-n, n:-n] = npy_ori[0]
                            npy[-(i + 1), n:-n, n:-n] = npy_ori[-1]
                        npy[n:-n, n:-n, n:-n] = npy_ori
                        npy[np.where(npy > 0)] = 103
                        npy[np.where(npy < 0)] = -3
                        for d in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                            npy[n:-n, n:-n, n:-n] = self.ZERO_SMOOTHER(self.SLICING(npy, n, d))

                    npy_result = npy[n:-n, n:-n, n:-n]
                    npy_result[np.where(npy_result != 0)] = 1
                    npy_ori = x
                    npy_ori = npy_ori * npy_result
                    npy_ori = np.int16(npy_ori)
                    return npy_ori

    def DIRECTION(self, d):  # 0 ~ 12
        direction_list = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [0, 1, 0], [1, 1, 0], [2, 1, 0], [0, 2, 0], [1, 2, 0],
                          [2, 2, 0], [0, 0, 1], [1, 0, 1], [2, 0, 1], [0, 1, 1]]
        return (direction_list[d])

    def LISTING(self, n, d):
        listing_list = []
        for i in range(0, 2 * n + 1):
            listing_list.append(
                [n * self.DIRECTION(d)[0] + (1 - self.DIRECTION(d)[0]) * i,
                 n * self.DIRECTION(d)[1] + (1 - self.DIRECTION(d)[1]) * i,
                 n * self.DIRECTION(d)[2] + (1 - self.DIRECTION(d)[2]) * i])
        return (listing_list)

    def SLICING(self, npy, n, d):
        length_0 = len(npy)
        length_1 = len(npy[0])
        length_2 = len(npy[0][0])
        slicing_list = []
        for i in range(0, len(self.LISTING(n, d))):
            slicing_list.append(npy[self.LISTING(n, d)[i][0]:length_0 - 2 * n + self.LISTING(n, d)[i][0],
                                self.LISTING(n, d)[i][1]:length_1 - 2 * n + self.LISTING(n, d)[i][1],
                                self.LISTING(n, d)[i][2]:length_2 - 2 * n + self.LISTING(n, d)[i][2]])
        return (slicing_list)

    def SIGN_SMOOTHER(self, npy_list):
        for i in range(0, len(npy_list)):
            if i == 0:
                npy_xz = npy_list[i]
            elif i != int((len(npy_list) - 1) * 0.5):
                npy_xz = npy_xz + npy_list[i]

        npy_y = npy_list[int((len(npy_list) - 1) * 0.5)]

        numpy = npy_xz * npy_y
        numpy[np.where(numpy != -(4 * len(npy_list) - 4))] = 1
        numpy[np.where(numpy == -(4 * len(npy_list) - 4))] = 0
        npy_result = npy_y * numpy
        return (npy_result)

    def ZERO_SMOOTHER(self, npy_list):
        for i in range(0, len(npy_list)):
            if i == 0:
                npy_xz = npy_list[i]
            elif i != int((len(npy_list) - 1) * 0.5):
                npy_xz = npy_xz + npy_list[i]

        npy_y = npy_list[int((len(npy_list) - 1) * 0.5)]

        npy_xz[np.where(npy_xz != 0)] = 1
        npy_result = npy_y * npy_xz
        return (npy_result)

class kalman_filter:
    """
    칼만 필터를 적용하여 신호의 예측 및 보정을 수행하는 클래스입니다.
    """
    def __init__(
            self,
            data = None,
            axis = 1,
            percentvar = 0.2,
            gain = 0.1,
                 ):

        self.data = data
        self.axis = axis
        self.percentvar = percentvar
        self.gain = gain

    def run(self, data = None):
        """
        입력 데이터에 대해 Kalman 보정 및 예측을 적용하여 필터링된 결과를 반환합니다.

        :param data: 필터링할 3차원 데이터 (선택 사항, 기본은 self.data 사용)
        :type data: numpy.ndarray
        :return: 필터가 적용된 GPR 데이터
        :rtype: numpy.ndarray
        """
        if not isinstance(data, type(None)):
            self.data = data

        if isinstance(self.data, type(None)):
            raise Exception("data가 없습니다.")

        self.dimension = list(self.data.shape)
        self.dimension.pop(self.axis)

        new_data = data.copy().astype(np.int)

        stackslice = np.zeros(self.dimension)
        filteredslice = np.zeros(self.dimension)
        noisevar = np.zeros(self.dimension)
        average = np.zeros(self.dimension)
        predicted = np.zeros(self.dimension)
        predictedvar = np.zeros(self.dimension)
        observed = np.zeros(self.dimension)
        Kalman = np.zeros(self.dimension)
        corrected = np.zeros(self.dimension)
        correctedvar = np.zeros(self.dimension)

        noisevar[:, :] = self.percentvar
        slicing = []

        for i in range(self.data.ndim):
            if i == self.axis:
                slicing.append(0)
            else:
                slicing.append(slice(0, None, 1))
        # print(slicing)
        predicted = self.data[tuple(slicing)]
        slicing.clear()
        predictedvar = noisevar

        for i in range(0, self.data.shape[self.axis] - 1):

            for j in range(self.data.ndim):
                if j == self.axis:
                    slicing.append(i + 1)
                else:
                    slicing.append(slice(0, None, 1))
            # print(slicing)
            stackslice = self.data[tuple(slicing)]
            observed = stackslice

            Kalman = predictedvar / (predictedvar + noisevar)

            corrected = self.gain * predicted + (1.0 - self.gain) * observed + Kalman * (observed - predicted)

            correctedvar = predictedvar * (1.0 - Kalman)

            predictedvar = correctedvar
            predicted = corrected
            new_data[tuple(slicing)] = corrected.astype(np.int)
            slicing.clear()

        return np.int16(new_data)


class Backgroud_remove:
    """
    각 채널의 평균값을 기반으로 배경 신호를 제거하는 필터입니다.
    """
    def __init__(self):
        self.percent = 1

    def run(self, gpr_aligned):
        """
        채널별 평균을 사용해 배경 성분을 제거합니다.

        :param gpr_aligned: 입력 GPR 데이터
        :type gpr_aligned: numpy.ndarray
        :return: 배경 제거된 데이터
        :rtype: numpy.ndarray
        """
        gpr_AB = gpr_aligned * 0
        for bg_channel in range(0, gpr_aligned.shape[0]):
            for bg_depth2 in range(0, gpr_aligned.shape[1]):
                gpr_AB[bg_channel, bg_depth2] = gpr_aligned[bg_channel, bg_depth2] \
                                                - (np.mean(gpr_aligned[bg_channel, bg_depth2], dtype=np.int32) * self.percent)

        return np.int16(gpr_AB)

class alignGround:
    """
    지면 반사점을 기준으로 GPR 데이터를 정렬하는 클래스입니다.
    """
    def __init__(self):
        pass

    def run(self, gpr_reshaped, manual_add = None):
        """
        평균 신호를 기준으로 지면을 찾아 정렬하고, 필요시 수동 보정도 적용합니다.

        :param gpr_reshaped: 입력 GPR 데이터
        :type gpr_reshaped: numpy.ndarray
        :param manual_add: 수동 정렬 보정값 (선택)
        :type manual_add: list[int] or None
        :return: 정렬된 데이터
        :rtype: numpy.ndarray
        """
        ground_idx_list = []

        for align_channel in range(0, gpr_reshaped.shape[0]):
            ground_avg_list = []
            for align_depth_001 in range(0, gpr_reshaped.shape[1]):
                ground_avg_list.append(np.mean(gpr_reshaped[align_channel][align_depth_001, :]))
            ground_avg_list = np.int32(ground_avg_list)

            for align_depth_002 in range(0, len(ground_avg_list - 1)):
                if ground_avg_list[align_depth_002] < - 1000 and ground_avg_list[align_depth_002 + 1] - ground_avg_list[
                    align_depth_002] > 0:
                    minimum = ground_avg_list[align_depth_002]
                    minimum_idx = align_depth_002
                    break

            for align_depth_003 in range(minimum_idx, len(ground_avg_list - 1)):
                if ground_avg_list[align_depth_003] > 1000 and ground_avg_list[align_depth_003 + 1] - ground_avg_list[align_depth_003] < 0:
                    maximum = ground_avg_list[align_depth_003]
                    maximum_idx = align_depth_003
                    break

            for align_depth_004 in range(minimum_idx, maximum_idx + 1):
                if ground_avg_list[align_depth_004] > 0:
                    # VER : 평균과 양수의 평균
                    uint_idx = align_depth_004
                    mean_idx = (minimum_idx + maximum_idx) / 2
                    ground_idx = round((uint_idx + mean_idx) / 2)
                    ground_idx_list.append(ground_idx)
                    break



        gpr_reshaped2 = np.zeros((gpr_reshaped.shape[0], gpr_reshaped.shape[1], len(gpr_reshaped[0][0])))

        if manual_add == None:

            for align_channel3 in range(0, gpr_reshaped.shape[0]):
                gpr_reshaped2[align_channel3, 0:gpr_reshaped.shape[1] - ground_idx_list[align_channel3] + 10, :] = gpr_reshaped[
                                                                                                 align_channel3,
                                                                                                 ground_idx_list[
                                                                                                     align_channel3] - 10:gpr_reshaped.shape[1],
                                                                                                 :]
            return np.int16(gpr_reshaped2)

        else:
            ground_idx_list = np.array(ground_idx_list)
            ground_idx_list += np.array(manual_add)

            for align_channel3 in range(0, gpr_reshaped.shape[0]):
                gpr_reshaped2[align_channel3, 0:gpr_reshaped.shape[1] - ground_idx_list[align_channel3] + 10, :] = gpr_reshaped[
                                                                                                 align_channel3,
                                                                                                 ground_idx_list[
                                                                                                     align_channel3] - 10:gpr_reshaped.shape[1],
                                                                                                 :]
            return np.int16(gpr_reshaped2)



class alingnSignal:
    """
    채널별 신호 강도 범위를 기준으로 스케일을 정규화하는 필터입니다.
    """
    def __init__(self):
        pass

    def alingnSignal(self, gpr_reshaped):
        """
        채널 간 신호 범위 차이를 줄이기 위해 보정 계수를 곱해 정렬합니다.

        :param gpr_reshaped: 입력 GPR 데이터
        :type gpr_reshaped: numpy.ndarray
        :return: 스케일 정규화된 데이터
        :rtype: numpy.ndarray
        """

        minimum_list = [-1000 for _ in range(0, gpr_reshaped.shape[0])]
        maximum_list = [1001 for _ in range(0, gpr_reshaped.shape[0])]

        for align_channel in range(0, gpr_reshaped.shape[0]):
            ground_avg_list = []
            for align_depth_001 in range(0, gpr_reshaped.shape[1]):
                ground_avg_list.append(np.mean(gpr_reshaped[align_channel][align_depth_001, :]))
            ground_avg_list = np.int32(ground_avg_list)

            for align_depth_002 in range(0, len(ground_avg_list - 1)):
                if ground_avg_list[align_depth_002] < - 1000 and ground_avg_list[align_depth_002 + 1] - ground_avg_list[
                    align_depth_002] > 0:
                    minimum = ground_avg_list[align_depth_002]
                    minimum_idx = align_depth_002
                    minimum_list[align_channel] = minimum
                    break

            for align_depth_003 in range(minimum_idx, len(ground_avg_list - 1)):
                if ground_avg_list[align_depth_003] > 1000 and ground_avg_list[align_depth_003 + 1] - ground_avg_list[
                    align_depth_003] < 0:
                    maximum = ground_avg_list[align_depth_003]
                    maximum_idx = align_depth_003
                    maximum_list[align_channel] = maximum
                    break

        range_list = np.array(maximum_list) - np.array(minimum_list)
        multiple_list = (range_list.max() / range_list)**0.5

        align_test2_mean_mult = np.empty((gpr_reshaped.shape))
        for i in range(gpr_reshaped.shape[1]):
            for j in range(gpr_reshaped.shape[2]):
                align_test2_mean_mult[:, i, j] = gpr_reshaped[:, i, j] * multiple_list

        gpr_reshaped = align_test2_mean_mult
        return np.int16(gpr_reshaped)

class ch_bias:
    """
    각 채널별 오프셋을 기준으로 보정하는 필터입니다.
    """
    def __init__(self):
        pass

    def ch_bias(self, data, start_bias):
        """
        start_bias 값을 이용해 채널별 기준값을 제거합니다.

        :param data: 입력 GPR 데이터
        :type data: numpy.ndarray
        :param start_bias: 채널별 평균 기준값
        :type start_bias: numpy.ndarray
        :return: 바이어스가 제거된 데이터
        :rtype: numpy.ndarray
        """
        return data - np.broadcast_to(start_bias[:, np.newaxis, np.newaxis], data.shape)
