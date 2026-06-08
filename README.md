# QICK Remote Execution

A client/server framework for running QICK programs remotely.

This project provides a simple way to submit QICK experiments from a Python client to a remote QICK board. Jobs are queued, executed, and their results can be retrieved later from the client.

The system is based on three components:

* **Client**: submits jobs and retrieves results.
* **Server**: manages the job queue and distributes work.
* **Worker**: runs directly on the QICK hardware and executes the requested programs.

Communication is performed using **ZeroMQ** and objects are serialized with **cloudpickle**, allowing QICK programs and configurations to be transmitted directly between machines.

---

## Features

* Remote execution of QICK programs.
* Asynchronous job submission.
* Job queue management.
* Job status monitoring.
* Result retrieval.
* Job cancellation.
* Automatic generation of unique job names.
* Support for multiple simultaneous clients.
* Separation between experiment control and hardware execution.

---

### Client

The client submits jobs using:

```python
job = client.submit(
    prog=MyProgram,
    config=cfg,
    nom_programme="my_experiment"
)
```

Each submission returns a `QickJob` object.

### Server

The server:

* receives requests from clients,
* maintains the execution queue,
* tracks job states,
* stores results,
* forwards jobs to available workers.

### Worker

The worker runs on the QICK board and:

* receives execution requests,
* instantiates the requested program,
* executes the selected acquisition method,
* returns the acquired data and execution metadata.

---

## Installation

### Requirements

* Python 3.8+
* pyzmq
* cloudpickle
* qick


Install QICK according to the official documentation.

---

## Basic Usage

### Connect to a server
A simple explanation of the program is made in Final\Client_example
```python
from QickRemote import QickClient

client = QickClient(
    ip_server="192.168.1.100",
    port=5555
)
```

### Submit a job

```python
job = client.submit(
    prog=LoopbackProgram,
    config=cfg,
    nom_programme="test"
)
```

### Check status

```python
job.status()
```

Possible states:

* `queued`
* `running`
* `done`
* `failed`
* `cancelled`

### Wait for completion

```python
result = job.wait()
```

### Retrieve the result

```python
result = job.result()
```

### Cancel a job

```python
job.cancel()
```

---

## Multiple Jobs

Submit several jobs:

```python
job1 = client.submit(prog1, cfg1, "job1")
job2 = client.submit(prog2, cfg2, "job2")
job3 = client.submit(prog3, cfg3, "job3")
```

Check their status:

```python
client.check_all()
```

Wait for all jobs:

```python
results = client.wait_all()
```

---

## Job Naming

If a requested job name already exists, the server automatically generates a unique name:

```text
The name 'job1' was already used.
The job has been renamed to 'job_a2e67cef'.
```

This prevents accidental overwriting of existing jobs.

---

## Error Handling

Execution errors occurring on the worker are propagated back to the client.

Example:

```python
try:
    result = job.result()
except RuntimeError as e:
    print(e)
```

The complete traceback generated on the worker can be returned to simplify debugging.

---

## Typical Workflow

```python
client = QickClient()

job = client.submit(
    prog=LoopbackProgram,
    config=cfg,
    nom_programme="experiment_1"
)

result = job.wait()

client.close()
```

---

## Motivation

This project was created to simplify the use of QICK hardware in shared environments where:

* the acquisition board is located on a dedicated machine,
* multiple users may submit experiments,
* execution must be decoupled from experiment development,
* experiments should run asynchronously without blocking the user's Python session.

---

## License

Specify your license here (MIT, BSD, GPL, etc.).

---

## Future Improvements

Possible future additions include:

* execution time limits,
* job priorities,
* persistent job database,
* web monitoring interface,
* authentication and permissions,
* multiple worker support,
* automatic result storage.
