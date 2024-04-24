ps -ef | grep 'au555720' | grep 'firefox' | grep -v grep | awk '{print $2}' | xargs -r kill -9
