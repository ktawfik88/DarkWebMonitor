import os
from datetime import datetime, timedelta

import pytz
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient


class JobManager:

    def __init__(self):
        client = MongoClient(
            'mongodb+srv://foxhat_data:Rm5HlMvTis55zgg3@foxhat.kivqpyk.mongodb.net/?retryWrites=true&w=majority')
        jobstores = {
            'default': MongoDBJobStore(client=client)
        }
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)

        # self.scheduler.configure(
        #     jobstores={"default": SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')}
        # )

    def add_job(self, fun, param):
        if self.scheduler.running:
            self.scheduler.shutdown()
        alarm_time = datetime.now() + timedelta(seconds=5)
        job = self.scheduler.add_job(fun, "date", run_date=alarm_time, args=param,timezone=pytz.timezone('Africa/Cairo'))
        self.scheduler.start()

        #950
        #110
        #

    def remove_job(self, job_id):
        try:
            job_id_ = self.sessionManager.jobs_collection.find_one({"job_id": job_id})["job_id"]
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            self.scheduler.remove_job(job_id_)
            self.scheduler.start()
            self.sessionManager.remove_job(job_id)
        except:
            self.sessionManager.remove_job(job_id)
