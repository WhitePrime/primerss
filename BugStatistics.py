import cherrypy
import json
import subprocess
from os.path import exists

class bug_statistic:
    def __init__(self, data_file_path, group='main'):
        self.data_file_path = data_file_path
        self.group = group
        commit = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
        self.data = {'commit':commit, 'tags':dict(), 'bugs':0}
        if exists(data_file_path):
            data = json.load(open(data_file_path))
            data = data.get(group,self.data)
            if data['commit'] == commit:
                self.data = data
            
    def log_bug(self, tag, message=None):
        tags = self.data['tags']
        current_tag = tags.get(tag,{'count':0,'messages':[]})
        current_tag['count']+=1
        current_tag['messages'].append(message)
        tags[tag] = current_tag
        self.data['bugs'] = len(tags)

    def dump(self):
        json.dump({self.group:self.data}, open(self.data_file_path,'w'),indent = 2, ensure_ascii = False)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.data

def run_web_report(conf, statistics: bug_statistic, script_name='/'):
    cherrypy.config.update(conf)
    cherrypy.tree.mount(statistics,script_name)
    cherrypy.engine.start()

def stop_report():
    cherrypy.engine.stop()