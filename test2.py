#!/usr/bin/env python
# coding=utf-8
import datetime
import logging
import os
import sys
import stat
import multiprocessing
from concurrent_log_handler import ConcurrentRotatingFileHandler

server_conf = {}
server_root = os.path.dirname(__file__)
app_log = ""


def setup_log():
    os.chdir(sys.path[0])
    log_path = os.path.join(os.path.realpath(os.path.dirname("__file__")), "log/server_control")
    log_file_path = os.path.join(log_path, "start_stop_record.log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    os.chmod(log_path, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP)
    if not os.path.isfile(log_file_path):
        with open(log_file_path, "a") as f:
            f.close()
    os.chmod(log_file_path, stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP)
    logging.basicConfig(level=logging.INFO)
    file_log_handler = FileHandler(
        log_file_path, encoding="utf-8", maxBytes=10 * 1024 * 1024, backupCount=10)
    formatter = logging.Formatter(
        '[%(asctime)s] - [%(levelname)s] - log_msg: %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.logThreads = 0
    logging.logMultiprocessing = 0
    logging.logProcesses = 0
    global app_log
    app_log = logging.getLogger("operation_start_stop")
    app_log.propagate=False
    app_log.handlers.clear()
    app_log.addHandler(file_log_handler)


class FileHandler(ConcurrentRotatingFileHandler):

    def __init__(self, name, encoding=None, maxBytes=None, backupCount=None):
        super().__init__(name, encoding=encoding, maxBytes=maxBytes, backupCount=backupCount,
                         chmod=stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP)

    def doRollover(self):
        os.chmod(self.baseFilename, stat.S_IRUSR + stat.S_IRGRP)
        super().doRollover()
        if os.path.exists(self.baseFilename):
            os.chmod(self.baseFilename, stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP)


def change_log_file_permissions(fileName, type):
    fileName = os.path.join(server_root, fileName)
    if not os.path.exists(fileName):
        with open(fileName, "a") as f:
            f.close()
        os.chmod(os.path.dirname(fileName), stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP)
    if type == "stop":
        os.chmod(fileName, stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP)
    elif type == "start":
        os.chmod(fileName, stat.S_IRUSR + stat.S_IWUSR + stat.S_IRGRP)
        run_log_path = fileName.rsplit("/", 1)
        log_name = run_log_path[-1]
        log_list = list()
        for i in os.listdir(run_log_path[0]):
            if i.endswith(".log"):
                log_list.append(i)
                if i != log_name:
                    os.chmod(os.path.join(run_log_path[0], i), stat.S_IRUSR + stat.S_IRGRP)
        if len(log_list) > 7:
            log_list.sort(key=lambda x: x.split(".")[0], reverse=True)
            # delete older log
            for i in log_list[7:]:
                os.remove(os.path.join(run_log_path[0], i))

    else:
        sys.stdout.write("change file permissions type is start or stop\n")


def app_status(port):
    cmd = "lsof -P -i:%s | gawk '$1==\"gunicorn\"'| awk '{print $2}'|wc -l" % port
    p = os.popen(cmd)
    output = p.read()
    try:
        num = int(output.strip())
        if num > 0:
            sys.stdout.write("app is running\n")
        else:
            sys.stdout.write("app is not start\n")
        return num
    except Exception as e:
        sys.stdout.write(e)
    finally:
        p.close()
        sys.stdout.write("done\n")


def time_wait_num():
    cmd = "netstat -ant|grep TIME_WAIT|awk '/^tcp/'|wc -l"
    p = os.popen(cmd)
    output = p.read()
    try:
        num = int(output.strip())
        return num
    except Exception as e:
        sys.stdout.write(e + "\n")
    finally:
        p.close()
        sys.stdout.write("done\n")


def app_start(father_path, pid_num, host, port):
    path = str(father_path)
    os.chdir(path)
    sys.stdout.write("app start...\n")
    fileName = datetime.date.today().strftime("%Y%m%d")
    cmd = "gunicorn -k gevent -w %d -b %s:%d app:app --daemon --log-file log/run_log/%s.log &" % (
        pid_num, host, port, fileName)
    os.system(cmd)
    app_log.info("Hisearch start success")
    change_log_file_permissions("log/run_log/%s.log" % fileName, "start")
    sys.stdout.write("done\n")


def app_stop(port):
    sys.stdout.write("app stop...\n")
    cmd = "lsof -P -i:%s | gawk '$1==\"gunicorn\"'| awk '{print $2}' | xargs kill -9" % port
    os.system(cmd)
    app_log.info("HiSearch stop success")
    sys.stdout.write("done\n")


def load_env_conf(father_path):
    file = os.path.normpath(os.path.join(father_path, "conf/env.conf"))
    try:
        with open(file, "r", encoding="utf-8") as fp:
            for line in fp.readlines():
                # 判断line是否为空/是否是注释行
                if not line or line.strip().startswith('#'):
                    continue
                # 首先：分割
                list_dic = line.strip().split("=", 1)
                if len(list_dic) <= 0:
                    continue
                server_conf.setdefault(list_dic[0], list_dic[1])
    except Exception as e:
        app_log.error(e)



def get_env_conf(father_path):
    if not server_conf:
        load_env_conf(father_path)
    return server_conf


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stdout.write("usage: server_control {start|stop|status|restart|time_wait}\n")
        exit(1)
    option = sys.argv[1]
    if option not in ["start", "stop", "status", "restart", "time_wait"]:
        sys.stdout.write("usage: server_control {start|stop|status|restart|time_wait}\n")
        exit(2)
    # start logging
    setup_log()
    log_path = os.path.realpath(os.path.join(os.path.dirname("__file__"), "log"))
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    run_log_path = os.path.realpath(os.path.join(os.path.dirname("__file__"), "log/run_log"))
    if not os.path.isdir(run_log_path):
        os.mkdir(run_log_path)
    # 获取当前文件路径
    current_path = os.path.abspath(__file__)
    # 获取当前文件的父目录
    father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
    # 加载环境信息
    server_conf = get_env_conf(father_path)
    if "host" in server_conf:
        host = server_conf["host"]
    else:
        host = '127.0.0.1'
    if "port" in server_conf:
        port = int(server_conf["port"])
    else:
        port = 5000
    if "pid_num" in server_conf:
        pid_num = int(server_conf["pid_num"])
    else:
        pid_num = multiprocessing.cpu_count() * 2 + 1

    # args port
    if len(sys.argv) == 3 and sys.argv[2].isdigit():
        port = int(sys.argv[2])

    if port:
        if option == "start":
            if app_status(port):
                app_stop(port)
                app_start(father_path, pid_num, host, port)
            else:
                app_start(father_path, pid_num, host, port)
        elif option == "stop":
            if app_status(port):
                app_stop(port)
        elif option == "status":
            app_status(port)
        elif option == "restart":
            app_stop(port)
            app_start(father_path, pid_num, host, port)
        elif option == "time_wait":
            time_wait_num()
        else:
            sys.stdout.write("usage: server_control {start|stop|status|restart|time_wait}\n")
            exit(2)
