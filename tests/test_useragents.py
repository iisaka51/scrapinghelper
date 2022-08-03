import os
import sys

sys.path.insert(0,"../scrapinghelper")

from pathlib import Path
from scrapinghelper import UserAgent, user_agent
from pprint import pprint

class TestClass:
    def test_user_random_agent(self):
        for _ in range(10):
            u = UserAgent()
            assert u.get_random_user_agent() in u.user_agents.user_agent.to_list()
    def test_keep_user_agents_default(self):
        u = UserAgent()
        assert u.keep_user_agents == 50
        assert len(u.user_agents) == 50

    def test_keep_user_agents_custom(self):
        u = UserAgent(keep_user_agents=100)
        assert u.keep_user_agents == 100
        assert len(u.user_agents) == 100

    def test_keep_user_agents_full(self):
        # one bad user_agent dropped.
        u = UserAgent(keep_user_agents=0)
        assert u.keep_user_agents == 19999
        assert len(u.user_agents) == 19999

    def test_load_user_agent_from_file(self):
        this_directory = Path(__file__).parent
        datapath = this_directory / "user_agent_test.csv"

        u = UserAgent(datapath=datapath)
        assert u.keep_user_agents == 50
        assert len(u.user_agents) == 50

    def test_reload_user_agent_from_file(self):
        this_directory = Path(__file__).parent
        datapath = this_directory / "user_agent_test.csv"

        u = UserAgent()
        u.load_datafile(datapath=datapath)
        assert u.keep_user_agents == 50
        assert len(u.user_agents) == 50

    def test_load_user_agent_from_env(self):
        this_directory = Path(__file__).parent
        datapath = this_directory / "user_agent_test.csv"
        os.environ.update(
             {'SCRAPINGHELPER_USERAGENT_PATH': str(datapath)})
        u = UserAgent()
        assert u.keep_user_agents == 50
        assert len(u.user_agents) == 50

    def test_func_user_agent(self):
        ua1 = user_agent()
        ua2 = user_agent()
        assert ua1== ua2
