from django.core.management import call_command
#from aircanary.utils import cd


def deploy_production():

    import subprocess
    subprocess.call(['git', '-C', '/home/ac/air-canary-web', 'pull'])
    subprocess.call(['/home/ac/Envs/ac/bin/pip', 'install', '-r', '/home/ac/air-canary-web/requirements/production.txt'])

    call_command('migrate')
    call_command('collectstatic', noinput=True)

    #with cd('/home/ac/air-canary-web/aircanary'):
    #    subprocess.call(['source', '/home/ac/.acrc', '/home/ac/Envs/ac/bin/python', 'manage.py', 'migrate'])
    #    subprocess.call(['source', '/home/ac/.acrc', '/home/ac/Envs/ac/bin/python', 'manage.py', 'collectstatic', '--noinput'])

    subprocess.call(['sudo', 'service', 'uwsgi', 'restart'])
    subprocess.call(['sudo', 'service', 'nginx', 'restart'])
