import pickle
import sys
import os
from .utils import *
from .constants import *
from .config import EasyRosettaConfig, ProtocolConfig


class Session():
    def __init__(self, session_name=None, working_dir=None, protein_name=None, progress_dict=None, protocol_configs=None):
        self.session_name = session_name
        self.working_dir = working_dir
        self.protein_name = protein_name
        self.progress_dict = progress_dict
        if self.progress_dict == None:
            self.progress_dict = {
                "frags_generated":False,
                "decoys_generated":False,
                "scored":False,
                "clustered":False,
            }
        self.easyrosetta_config = EasyRosettaConfig.load()
        self.protocol_configs = protocol_configs
        if self.protocol_settings == None:
            self.protocol_settings = []

    def save_session(self):
        yes = ["yes", "y"]
        no = ["no", "n"]
        overwrite = True
        is self.session_name == None:
            return
        while Session.session_exists(self.session_name) and not overwrite:
            status = input("A session with that name already exists. Do you want to overwrite that session? (Y/n)").lower()
            while status not in yes and status not in no:
                status = input("Please enter (Y/n) ")
            if status in no:
                session_name = input("Enter a new session name, or (q) to quit: ")
                if session_name == 'q':
                    sys.exit()
                else:
                    self.set_session_name(session_name)
            else:
                overwrite = True
        with open(self.get_session_file(), 'w') as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    def set_session_name(self, session_name):
        self.session_name = session_name

    def set_working_dir(self, working_dir):
        self.working_dir = working_dir

    def set_protein_name(self, protein_name):
        self.protein_name = protein_name

    def set_progress_dict(self, progress_dict):
        self.progress_dict = progress_dict

    def change_progress_dict(self, key, value):
        if key not in self.progress_dict:
            return
        else:
            self.progress_dict[key] = value

    def print_session_info(self):
        print("Session name: " + self.session_name)
        print("Protein name: " + self.protein_name)
        print("Working directory: " + self.working_dir)
        print("Progress:" + str(self.progress_dict))

    @staticmethod
    def load_session(session_name):
        if not Session.session_exists(session_name):
            print("No such session exists. To list all sessions, try easy-rosetta-sessions -l")
            sys.exit()
        session = None
        with open(os.path.join(SESSIONS_PATH, Session.get_session_file(session_name)), 'r') as fp:
            session = pickle.load(fp)
        if session == None:
            print("Error loading session " + session_name + ". Check logs for more details.")
            sys.exit()
        return session

    @staticmethod
    def remove_session(session_name):
        if not Session.session_exists(session_name):
            print("No such session exists. To list all sessions, try easy-rosetta-sessions -l")
            sys.exit()
        os.remove(Session.get_session_file(session_name))

    @staticmethod
    def clear_sessions():
        for file in os.listdir(SESSIONS_PATH):
            os.remove(file)

    @staticmethod
    def session_exists(session_name):
        return Session.get_session_file(session_name) in os.listdir(SESSIONS_PATH)

    @staticmethod
    def get_session_file(session_name):
        return session_name + ".session"


    


