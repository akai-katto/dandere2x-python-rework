import time
from abc import abstractmethod, ABC
from threading import Thread

from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.utilities.yaml_utils import load_executable_paths_yaml


@abstractmethod
class _Dandere2xServiceInterface(Thread, ABC):
    """
    An abstract-base-class dictating how dandere2x_service should be utilized.

    As an example, a singleprocess_service will only use one dandere2x-thread to upscale a video file, where as
    multiprocess_service will use multiple. In either case, an upscaled video will still be produced, but the black
    box implementation in between will change.

    This abstract-interface gives enough shared functions / descriptions of how the black-box should be implemented,
    See singleprocess_service.py or gif_service.py for examples of how to use these shared functions / see why they
    exist.
    """

    def __init__(self, dandere2x_session: Dandere2xSession):
        super().__init__(name=str(dandere2x_session.input_video_path))
        self._dandere2x_session = dandere2x_session
        self._executable_paths = load_executable_paths_yaml()

        # meta-data
        self.__start_time: float = 0
        self.__end_time: float = 0

    # Public Methods

    @abstractmethod
    def run(self):
        pass

    def timer_start(self) -> None:
        self.__start_time = time.time()

    def timer_end(self) -> None:
        self.__end_time = time.time()

    def timer_get_duration(self) -> float:
        return self.__end_time - self.__start_time

    # Protected Methods

    @abstractmethod
    def _pre_process(self):
        pass

    @abstractmethod
    def _on_completion(self):
        pass