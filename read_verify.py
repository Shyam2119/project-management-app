
try:
    with open('git_verification.info', 'r', encoding='utf-16') as f:
        print(f.read())
except:
    try:
        with open('git_verification.info', 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e:
        print(e)
