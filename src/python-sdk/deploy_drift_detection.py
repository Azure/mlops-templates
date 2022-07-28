# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from obs.drift.drift_analysis_scheduler import execute
from datetime import datetime
from azure.ai.ml.constants import TimeZone
from dateutil import tz
from azure.ai.ml.entities import CronSchedule, ScheduleStatus
from azureml.core import Workspace

schedule_start_time = datetime.now(tz=tz.gettz("PACIFIC STANDARD TIME"))
cron_schedule = CronSchedule(
    expression="*/10 * * * *", #provide a cron express to schedule the recurring execution of drift detection job
    start_time=schedule_start_time,
    time_zone=TimeZone.PACIFIC_STANDARD_TIME,
    status=ScheduleStatus.ENABLED,

)

target_dt_shift_step_size= "W"

ws = Workspace.from_config()

subscription_id = ws.subsription_id
resource_group = ws.resource_group
workspace = ws.name

compute_name = 
base_table_name =
target_table_name = 
base_dt_from = 
base_dt_to = 
target_dt_from = 
target_dt_to= 

ml_client, job_name = execute(subscription_id=subscription_id,resource_group=resource_group,workspace=workspace, compute_name =compute_name, 
base_table_name =base_table_name,target_table_name =target_table_name, base_dt_from =base_dt_from, base_dt_to= base_dt_to,target_dt_from=target_dt_from, 
target_dt_to=target_dt_to, bin="7d", limit=100000, concurrent_run=False, drift_threshold =0.4,target_dt_shift_step_size=target_dt_shift_step_size,job_cron_schedule=cron_schedule)
