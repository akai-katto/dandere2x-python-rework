import os
from abc import ABC
from threading import Thread
from typing import Type

from dandere2x import Dandere2x
from dandere2x_services._dandere2x_service_interface import _Dandere2xServiceInterface
from dandere2xlib.d2xsession import Dandere2xSession
from dandere2xlib.ffmpeg.ffmpeg_utils import migrate_tracks_contextless


class Dandere2xServiceResolver(Thread):
    """
    Accepts a "root"-level request and will handle all the logic in spawning the child-dandere2x sessions.

    This folder is a very generic wrapper in that it's mostly there to handle superficial logic in how dandere2x
    should go about processing a service request.
    """

    def __init__(self, dandere2x_session: Dandere2xSession):
        super().__init__()
        self.dandere2x_session = dandere2x_session

        # discover which dandere2x-process the user wants to use.
        anonymous_dandere2x_service = self._determine_process_type(self.dandere2x_session)

        # start a child-thread of the selected process.
        self._root_service_thread = anonymous_dandere2x_service(dandere2x_session=self.dandere2x_session)

    @staticmethod
    def _determine_process_type(session: Dandere2xSession) -> Type[_Dandere2xServiceInterface]:
        """
        A wrapper to determine what the root service should be - i.e a logical set of operations to determine what
        the user was intending for dandere2x to return given the initial service request.

        :param request: The root service request.
        :return: A Dandere2xInterface-inherited subclass.
        """

        if session.processing_type == "multiprocess":
            from dandere2x_services.multiprocess_dandere2x_service import MultiProcessDandere2xService
            return MultiProcessDandere2xService

        if session.processing_type == "singleprocess":
            from dandere2x_services.singleprocess_dandere2x_service import SingleProcessDandere2xService
            return SingleProcessDandere2xService

        raise Exception("Could not find selected waifu2x type. ")

    def run(self) -> None:
        self._root_service_thread.run()
