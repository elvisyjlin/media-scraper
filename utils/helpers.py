def log(msg, file='log.txt'):
    print(msg)
    with open(file, 'a') as f:
        f.write(msg + '\n')