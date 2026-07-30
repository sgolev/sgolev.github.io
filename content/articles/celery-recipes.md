Title: Celery: from first task to advanced recipes
Date: 2026-07-28 02:59 +03:00
Tags: python, celery

[Celery](https://github.com/celery/celery) is a mature distributed task queue system for Python. It is useful for integrating various services in a decoupled producer-consumer fashion. In this article, I want to share my experience with Celery. After a brief introduction, I provide code snippets that you can reuse in your projects.

# Introduction

As a task queue system, Celery can send tasks and write the results to Redis, RabbitMQ, etc. Celery specifically distinguishes between a broker and a result backend. A *broker* is where a task is queued and picked up, and a *backend* is where the optional result is saved. For a minimal use case, only the broker is required.

Let's start with the installation of Celery. In what follows, we will use Redis both as a broker and as a backend. Get Celery with `pip install celery[redis]`. You may launch Redis using Docker with the following command:

```sh
docker run -d -p 6379:6379 redis
```

Now to try a simple example. Here is how we define a task named `say_hello`:

```py title="tasks.py"
from celery import Celery

# Specify the broker URL as an argument to Celery(...).
# You may also set CELERY_BROKER_URL environment variable instead.
app = Celery(broker='redis://localhost:6379/0')

@app.task
def say_hello():
    print('Hello, World!')
```

In fact, the full name of the task is `tasks.say_hello`. The prefix is inferred from the module's name. This detail is important if we call the task remotely, since this method requires us to specify the full name.

Run the Celery worker that will serve the task:

```sh
celery -A tasks worker
# On Windows: celery -A tasks -P solo worker
```

Workers in Celery support concurrency. The default pool is `prefork` (child processes), so multiple tasks will be executed in parallel without any tuning. Note, however, that on Windows, the `prefork` pool is not supported. Instead, you may use the `solo` pool for simple testing, and launch multiple Celery processes to implement concurrency. Alternatively, use the `threads` or `gevent` pool.

Run the task from the terminal:

```sh
celery -A tasks call tasks.say_hello
```

This command prints the ID of the request (e.g., `d91260dd-19b3-401b-84d8-1ba85df55fad`).

In the worker's terminal, you should see something like:

```
[2026-07-12 16:06:34,971: WARNING/ForkPoolWorker-15] Hello, World!
```

But what if there are several workers with their own sets of tasks? Separate queues are what you need. By default, Celery operates on the `celery` queue. You may point the worker at a different queue:

```sh
celery -A tasks worker -Q my-queue
```

Then call the task like this:

```sh
celery -A tasks call tasks.say_hello --queue my-queue
```

That's it for the basic usage! In the following sections, I provide some useful code snippets.

# Running tasks from the command line

Define the `CELERY_BROKER_URL` environment variable, then run in Bash:

```sh
celery call TASK_NAME --args '["hello", 123]' --kwargs '{"key": true}' --queue QUEUE
```

To get the result, define the `CELERY_RESULT_BACKEND` environment variable and run:

```sh
celery result TASK_ID
```

Without these environment variables, you would need to specify the module with a Celery application via the `-A` option.

# Running tasks from code

Suppose that the task is defined within the current service. In order to run it, you simply access the corresponding function object:

```py
from celery import Celery

app = Celery(broker='...', backend='...')

@app.task
def multiply(x, y):
    return x * y

# Call the task asynchronously
task_result = multiply.apply_async((2, 4))
# ^^^ Equivalent:
#     task_result = multiply.delay(2, 4)

# Wait for the result. A backend is required for this.
print(task_result.get())  # Prints: 8
```

If you need to run a task from another service, then you may call it by its name:

```py
from celery import Celery

app = Celery(broker='...', backend='...')

# Call the task asynchronously
task_result = app.send_task('tasks.multiply', (2, 4))

# Wait for the result. A backend is required for this.
print(task_result.get())  # Prints: 8
```

Both options may be unified with so-called signatures from the *Canvas* functionality:

```py
from celery import Celery

app = Celery(broker='...', backend='...')

@app.task
def multiply(x, y):
    return x * y

# Call by declaration
sig = multiply.signature((2, 4))
# ^^^ Equivalent:
#     sig = multiply.s(2, 4)
task_result = sig.apply_async()
print(task_result.get())

# Call by name
sig = app.signature('tasks.multiply', (2, 4))
task_result = sig.apply_async()
print(task_result.get())
```

# Running a batch of tasks

To start multiple tasks at once, use `group` from the Canvas functionality:

```py
...
import celery

task_result = celery.group(
    app.signature('tasks.multiply', (2, i))
    for i in range(10)
).apply_async()
print(task_result.get())  # Prints: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

Some tasks may finish successfully, and some with an error. To handle each case separately, use the `propagate=False` parameter when calling `.get()`:

```py
for value in task_result.get(propagate=False):
    if isinstance(value, Exception):
        ...
    else:
        ...
```

# Queues in the broker

By default, all tasks are sent to the `celery` queue. To change the target queue, use the `queue='...'` parameter when calling `.apply_async()`:

```py
# Call by declaration
multiply.apply_async((2, 4), queue='...')
multiply.signature(options=dict(queue='...')).delay(2, 4)
# ^^^ options=... are forwarded to delay() / apply_async()

# Call by name
app.send_task('tasks.multiply', (2, 4), queue='...')
# ^^^ send_task()'s parameters are analogous to those of apply_async()
app.signature('tasks.multiply').apply_async((2, 4), queue='...')
```

# Time limits

A task may accidentally hang for an indefinite time, which is why in production code it is important to set a time limit on waiting for the result. Use the `timeout=...` parameter of `.get()`:

```py
# Wait 60 seconds, then raise a celery.exceptions.TimeoutError
task_result.get(timeout=60)
```

If after the timeout the task is no longer relevant, consider defining a time limit on the relevance of the task. After this time expires, any worker that picks up the task will cancel and discard it. Use the `expires=...` parameter of `.apply_async()`:

```py
multiply.apply_async((2, 4), expires=60)
```

You may also define limits on the duration of a task's execution. A *soft* limit raises an exception when the allotted time expires. A *hard* limit forcibly terminates the child process of the worker in question. Example:

```py
@app.task(soft_time_limit=5, time_limit=10)
def my_task():
    ...
```

Thus, Celery offers three kinds of time limits: `timeout` at the client level, `expires` at the message level, and `soft_time_limit`/`time_limit` at the worker level.

# Retrying

Some tasks may encounter transient errors, in which case you may want to retry execution at a later time. In Celery, there's a mechanism to implement this logic on the worker's side. More specifically, a worker can initiate a retry by returning the task to the queue with a countdown (3 minutes by default). The client waits until all the retries (at most 3 by default) fail or the timeout of `.get()` is reached. The implementation:

```py
@app.task(bind=True)
def my_unreliable_task(self):
    try:
        do_request()
    except NetworkError as exc:
        raise self.retry(exc=exc)
```

Here `bind=True` gives access to the task instance, which is passed as the first parameter. If you need to change the retry delay, set the `countdown` parameter of `.retry()`.

# Preventing parallel execution

Sometimes you want to explicitly forbid parallel execution of a specific task. You may either forcibly cancel the task or retry it at a later time. Below I provide an example that uses Redis locks and task retries, but you can alter the code as you wish. Importantly, I create a separate Redis connection — that is, there are two connections per worker: from `Celery` and from `Redis`. See the code:

```py
import contextlib
from functools import wraps

from celery import Celery
from redis import Redis
from redis.exceptions import LockError

TASK_SOFT_TIME_LIMIT = 300  # seconds
TASK_TIME_LIMIT = TASK_SOFT_TIME_LIMIT + 5

broker_url = '...'
app = Celery(broker=broker_url)
redis_client = Redis.from_url(broker_url)

# This is a decorator that can be applied to any task declared with bind=True
def with_lock(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        lock = redis_client.lock(f'task-lock-{self.name}', timeout=TASK_TIME_LIMIT)
        if not lock.acquire(blocking=False):
            raise self.retry(exc=LockError('Task is already running'))

        try:
            return func(self, *args, **kwargs)
        finally:
            with contextlib.suppress(LockError):
                lock.release()

    return wrapper

@app.task(bind=True, max_retries=1, soft_time_limit=TASK_SOFT_TIME_LIMIT,
          time_limit=TASK_TIME_LIMIT)
@with_lock
def my_task(self):
    ...
```

Now if you send two tasks in a row, the second task receives `RETRY` status. The default retry delay is 3 minutes, so the task is restarted after this time. If the first task still hasn't finished by that moment, then the second task is dropped with `FAILURE` status. This scenario relies on the retry delay being shorter than the task's time limit (180 s < 305 s).

# `await`-ing a task

Async/await syntax of modern Python is still not supported by Celery. Yet `await`-ing a task can be very convenient. The simplest workaround is to wait for the result in a separate thread using `asyncio.to_thread()`:

```py
...
import asyncio

async def main():
    task_result = app.send_task('tasks.multiply', (2, 4))
    print(await asyncio.to_thread(task_result.get))

asyncio.run(main())
```

If the task invocation rate is high, you may hit the default thread pool limit. Unfortunately, avoiding threads completely is a path filled with pitfalls. The general idea is to poll the task result until it becomes ready. But note that checking for the status of the result can be a blocking operation depending on the backend. This is not an issue if the backend is located on the same machine, but troublesome if it is not. Here is the implementation:

```py
...
import asyncio
import contextlib

async def async_get(task_result, *, poll_interval=0.05,
                    poll_interval_max=2.0, timeout=None, **kwargs):
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout if timeout is not None else None

    try:
        while not task_result.ready():
            delay = poll_interval
            if deadline is not None:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    raise TimeoutError
                delay = min(delay, remaining)

            await asyncio.sleep(delay)
            poll_interval = min(poll_interval * 2, poll_interval_max)
    except BaseException:
        with contextlib.suppress(Exception):
            task_result.forget()
        raise

    return task_result.get(**kwargs)
```

Usage:

```py
async def main():
    task_result = app.send_task('tasks.multiply', (2, 4))
    print(await async_get(task_result))

asyncio.run(main())
```

# Conclusion

To summarize, we've covered the core usage of Celery and worked our way up to a set of recipes that you can use in your projects. Hopefully they'll serve as a guide for the advanced use cases, which — as my experience shows — you will inevitably encounter. For anything beyond this post, refer to the [official documentation](https://docs.celeryq.dev/en/stable/index.html). Here, I've tried to make a few of its topics clearer and more practical.