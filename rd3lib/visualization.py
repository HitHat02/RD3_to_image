'''
이미지/그래프 그리기 함수들
'''
import matplotlib.pyplot as plt

def plot_gpr_image(rd3_cut, channel, cmap='gray'):
    """
    특정 채널에 대한 GPR 데이터를 시각화하여 화면에 출력합니다.

    3차원 GPR 데이터 중 지정된 채널(channel)을 기준으로 2차원 이미지를 생성하며,
    색상 맵(cmap)을 적용하여 `matplotlib`를 이용해 화면에 표시합니다.

    :param rd3_cut: 슬라이스된 3차원 GPR 데이터 (예: cutRd3 결과)
    :type rd3_cut: numpy.ndarray
    :param channel: 시각화할 채널 인덱스
    :type channel: int
    :param cmap: 사용할 컬러맵 (기본값: 'gray')
    :type cmap: str
    :return: 없음 (이미지 출력만 수행)
    :rtype: None
    """
    plt.figure(figsize=(12, 6))
    plt.imshow(rd3_cut[channel], aspect='auto', cmap=cmap)
    plt.title(f"GPR img")
    plt.tight_layout()
    plt.show()