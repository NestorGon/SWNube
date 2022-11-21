#from celery import Celery
from pydub import AudioSegment
import requests
import os
from google.cloud import storage, pubsub_v1

project_id = "swnube"
subscription_id = "tasks-sub"
# Number of seconds the subscriber should listen for messages
#timeout = 5.0
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

#celery = Celery(__name__, broker='redis://localhost:6379/00')

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message_dict = eval(message.data.decode("utf-8"))
    print(message_dict)
    print(type(message_dict))
    start_conversion(message_dict["task_id"],message_dict["in_route"],message_dict["out_route"],message_dict["in_ext"],message_dict["out_ext"])

    # Use `ack_with_response()` instead of `ack()` to get a future that tracks
    # the result of the acknowledge call. When exactly-once delivery is enabled
    # on the subscription, the message is guaranteed to not be delivered again
    # if the ack future succeeds.
    ack_future = message.ack_with_response()

    try:
        # Block on result of acknowledge call.
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        ack_future.result()
        print(f"Ack for message {message.message_id} successful.")
    except sub_exceptions.AcknowledgeError as e:
        print(
            f"Ack for message {message.message_id} failed with error: {e.error_code}"
        )

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")


#@celery.task(name="start_conversion")
def start_conversion(task_id,in_route,out_route,in_ext,out_ext):
    print(in_route)
    print(in_route[1::])
    print(out_route)
    print(1)
    storage_client = storage.Client()
    bucket = storage_client.bucket("swnube30")
    blob = bucket.blob(in_route)
    blob.download_to_filename("{}".format(in_route.split("/")[1]))
    AudioSegment.from_file("{}".format(in_route.split("/")[1],format=in_ext)).export("{}".format(out_route.split("/")[1]), format=out_ext)
    blob = bucket.blob(out_route)
    blob.upload_from_filename(out_route.split("/")[1])
    os.remove(in_route.split("/")[1])
    os.remove(out_route.split("/")[1])
    print(2)
    r = requests.post(f'http://{os.environ.get("API_INSTANCE_IP")}:5000/api/tasks/{task_id}/processed')
    print(f'Response: {r.status_code}')


with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.
