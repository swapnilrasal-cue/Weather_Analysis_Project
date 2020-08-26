from apscheduler.schedulers.background import BackgroundScheduler
from app import app,models
from app import controller

if __name__ == "__main__":
    # this manager.run() can be used only for migrate and upgrade database
    # models.manager.run()

    scheduler = BackgroundScheduler()
    scheduler.add_job(controller.get_current_weather, 'interval', seconds=20)
    scheduler.start()
    app.run(debug=True)