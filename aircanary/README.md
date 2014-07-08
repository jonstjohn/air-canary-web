Data process

Hourly cron executes in celery airnow/tasks::grib_process_csv() .  This task executes airnow/grib::run() .

airnow/grib::run() can be executed async or regular.  By default it runs async, but it can run sync when executed using the management command.

