from django.core.management import call_command
#from aircanary.utils import cd


def deploy_production():

    import subprocess
    subprocess.call(['sudo', '-u', 'ac', '/home/ac/git.sh'])
    subprocess.call(['git', '-C', '/home/ac/air-canary-web', 'reset', '--hard', 'HEAD'])
    subprocess.call(['git', '-C', '/home/ac/air-canary-web', 'pull'])
    subprocess.call(['/home/ac/Envs/ac/bin/pip', 'install', '-r', '/home/ac/air-canary-web/requirements/production.txt'])

    call_command('migrate')
    call_command('collectstatic', interactive=False)

    subprocess.call(['sudo', 'service', 'uwsgi', 'restart'])
    subprocess.call(['sudo', 'service', 'nginx', 'restart'])
