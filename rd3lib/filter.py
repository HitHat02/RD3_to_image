'''
rd3 파일 데이터 전처리에 사용되는 모든 필터를 적용하는 모듈
apply_filter(numpy_data)를 사용하면
default로 지정되어있는 전처리를 하여 numpy_data를 돌려줌
'''

from rd3lib import filter_back_end as filterBack

import pandas as pd
import numpy as np
import copy

def apply_filter(npy_file):
    """
    RD3 데이터에 필터를 자동 적용하는 함수.

    filterCollect.csv 파일에 정의된 필터 중 default == 1로 지정된 필터들을
    순서대로 적용하여 전처리된 numpy 데이터를 반환합니다.

    :param npy_file: 필터를 적용할 3차원 numpy 배열 (RD3 데이터)
    :type npy_file: numpy.ndarray
    :return: 필터가 적용된 RD3 numpy 배열
    :rtype: numpy.ndarray
    """
    filter_df = pd.read_csv('.\\rd3lib\\filterCollect.csv')

    filter_ = filter_worker(npy_file, filter_df)
    RD3_data = filter_.filterRun()
    return RD3_data

class filter_worker:
    """
        filterCollect.csv의 설정을 바탕으로 RD3 데이터에 다양한 필터를 순차적으로 적용하는 클래스.

        :param data: 필터를 적용할 3차원 numpy 배열 (RD3 데이터)
        :type data: numpy.ndarray
        :param filter_df: filterCollect.csv를 pandas로 읽어온 데이터프레임
        :type filter_df: pandas.DataFrame
        """
    def __init__(self, data, filter_df):
        super().__init__()
        self.data = data  # rd3를 읽은 3차원 numpy 데이터
        self.filter_df = filter_df  # filterCollect.csv 로 읽은 데이터프레임

    def filterRun(self):
        """
        filterCollect.csv 내 default == 1로 설정된 필터를
        filter_order 순서에 따라 적용합니다.

        적용 가능한 필터:
        - gain, range, las, edge, average
        - y_differential, z_differential
        - sign_smoother, kalman, background
        - alingnSignal, ch_bias

        :return: 모든 필터가 적용된 RD3 데이터
        :rtype: numpy.ndarray (dtype=int32)
        """
        # start_time = time.time()
        self.RD3_data = copy.deepcopy(self.data)

        selectedFilter = self.filter_df[self.filter_df.default == 1].copy()

        selectedFilter = selectedFilter.fillna(0)
        selectedFilter = selectedFilter.sort_values(by=['filter_order'])

        for index, row in selectedFilter.iterrows():

            if row['filter_base'] == 'gain':
                print('gain start')
                Gain = filterBack.Gain()

                Gain.y_inter = float(row['y_inter'])
                Gain.grad_const = float(row['grad_const'])
                Gain.inflection_point = float(row['inflection_point'])
                Gain.inflection_range = float(row['inflection_range'])
                self.RD3_data = Gain.Gain(self.RD3_data)
                print('gain end')

            elif row['filter_base'] == 'range':
                print('Range start')
                Range = filterBack.Range()

                Range.range_vaule = float(row['range_vaule'])
                self.ascan_range = int(row['range_vaule'])
                self.RD3_data = Range.Range(self.RD3_data)
                print('Range end')

            elif row['filter_base'] == 'las':
                print('Las start')

                Las = filterBack.Las()

                Las.las_ratio = float(row['las_ratio'])
                Las.sigmaNumber = float(row['sigmaNumber'])
                # Las.las_number = float(row['las_number'])
                Las.sigma_constants = float(row['sigma_constants'])
                self.RD3_data = Las.Las(self.RD3_data)

                print('Las end')

            elif row['filter_base'] == 'edge':
                print('edge start')

                edge = filterBack.edge()

                edge.edge_range = float(row['edge_range'])
                self.RD3_data = edge.edge(self.RD3_data)

                print('edge end')

            elif row['filter_base'] == 'average':
                print('average start')

                average = filterBack.average()

                average.depth = int(row['depth_para'])
                average.dist = int(row['dist_para'])
                self.RD3_data = average.average(self.RD3_data)

                print('average end')

            elif row['filter_base'] == 'y_differential':
                print('y_differential start')

                y_differential = filterBack.y_differential()
                y_differential.y_window_para = int(row['y_window_para'])
                self.RD3_data = y_differential.y_differential(self.RD3_data)

                print('y_differential end')

            elif row['filter_base'] == 'z_differential':
                print('y_differential start')

                z_differential = filterBack.z_differential()
                z_differential.z_window_para = int(row['z_window_para'])
                self.RD3_data = z_differential.z_differential(self.RD3_data)

                print('y_differential end')

            elif row['filter_base'] == 'sign_smoother':
                print('sign_smoother start')

                sign_smoother = filterBack.sign_smoother()
                # sign_smoother.runable = int(row['sign_smoother_check'])
                if int(row['sign_smoother_check']) == 2:
                    self.RD3_data = sign_smoother.run_with_npy(self.RD3_data)

                print('sign_smoother end')

            elif row['filter_base'] == 'kalman':
                print('kalman start')

                kalman_filter = filterBack.kalman_filter()
                kalman_filter.axis = int(row['axis_para'])
                kalman_filter.percentvar = float(row['percent_var_para'])
                kalman_filter.gain = float(row['gain_para'])

                self.RD3_data = kalman_filter.run(self.RD3_data)

                print('kalman end')

            elif row['filter_base'] == 'background':
                print('background start')

                Backgroud_remove = filterBack.Backgroud_remove()
                Backgroud_remove.percent = float(row['background_percent'])
                # sign_smoother.runable = int(row['sign_smoother_check'])
                if int(row['background_check']) == 2:
                    self.RD3_data = Backgroud_remove.run(self.RD3_data)

                print('background end')

            elif row['filter_base'] == 'alingnSignal':
                print('alingnSignal start')

                alingnSignal = filterBack.alingnSignal()
                # sign_smoother.runable = int(row['sign_smoother_check'])
                if int(row['alingnSignal_check']) == 2:
                    self.RD3_data = alingnSignal.alingnSignal(self.RD3_data)

                print('alingnSignal end')

            elif row['filter_base'] == 'ch_bias':
                print('ch_bias start')
                self.start_bias = np.mean(self.data, axis=(1, 2))
                ch_bias = filterBack.ch_bias()
                # sign_smoother.runable = int(row['sign_smoother_check'])
                if int(row['ch_bias_check']) == 2:
                    self.RD3_data = ch_bias.ch_bias(self.RD3_data, self.start_bias)

                print('ch_bias end')

        return np.int32(self.RD3_data)