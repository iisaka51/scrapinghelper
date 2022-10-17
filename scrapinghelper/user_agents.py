import os
from pathlib import Path
from typing import Optional
from itertools import cycle
import numpy as np
import pandas as pd

class UserAgent(object):
    __user_agents_datafile = '20000 User Agents.csv'
    __columns = "id,user_agent"

    def __init__(self,
        keep_user_agents: int=50,
        datapath: Optional[str]=None,
        ):
        """UserAgent manager
        Parameters
        ----------
        keep_user_agents: int
            The number of user_agents to keep in memory. default is 50.
            if 0 passed for keep_user_agents, all data will be kept.
        datapath: Optional[str]
            The CSV filename of user_agents datasets from 51degrees.com.
        """
        self.first_user_agent: str = ''

        self.load_datafile(keep_user_agents, datapath)

    def load_datafile(self,
        keep_user_agents: int=50,
        datapath: Optional[str]=None,
        ) ->None:

        self.__known_bad_user_agents = ['Hello, world']

        datapath = datapath or os.environ.get('SCRAPINGHELPER_USERAGENT_PATH',
                                              default=None)
        if datapath:
            data_file = Path(datapath)
        else:
            data_file  = ( Path(__file__).parent
                            / 'data/{}'.format(self.__user_agents_datafile) )

        with open(data_file) as file:
            user_agents = file.read().splitlines()

        self.user_agent_count = len(user_agents)
        df = pd.DataFrame( data=user_agents, columns=['user_agent'] )
        df = df[~df.user_agent.isin(self.__known_bad_user_agents)]
        if keep_user_agents:
            self.user_agents = df.sample(n=keep_user_agents)
        else:
            self.user_agents = df.copy()

        self.keep_user_agents = len(self.user_agents)
        self.user_agent_pool = cycle(self.user_agents.user_agent.to_list())
        self.first_user_agent = next(self.user_agent_pool)

    def get_random_user_agent(self) ->str:
        user_agent = np.random.choice(self.user_agents.user_agent.to_list(),
                                      replace=True, size=1)
        return list(user_agent)[0]

    def get_next_user_agent(self) ->str:
        return next(self.user_agent_pool)

    def __repr__(self):
        return self.first_user_agent


user_agent = UserAgent()
