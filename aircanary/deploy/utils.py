from django.core.management import call_command
#from aircanary.utils import cd


def deploy_prod():

    import subprocess
    print(subprocess.check_output(['git', '-C', '/home/ac/air-canary-web', 'reset', '--hard', 'HEAD'])
    print(subprocess.check_output(['git', '-C', '/home/ac/air-canary-web', 'pull'])
    print(subprocess.check_output(['/home/ac/Envs/ac/bin/pip', 'install', '-r', '/home/ac/air-canary-web/requirements/production.txt'])

    call_command('migrate')
    call_command('collectstatic', interactive=False)

    print(subprocess.check_output(['sudo', 'service', 'uwsgi', 'restart'])
    print(subprocess.check_output(['sudo', 'service', 'nginx', 'restart'])
