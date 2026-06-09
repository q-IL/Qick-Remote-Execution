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

The client submits jobs and retrieve them.

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

* Python
* pyzmq
* cloudpickle
* qick
* QickRemote.py for the client


Install QICK according to the official documentation.

---

## Basic Usage

An explanation of the project and several usage examples can be found in:

`Final/Client_example.ipynb`



## Motivation

This project was created to simplify the use of QICK hardware in shared environments where:

* the acquisition board is located on a dedicated machine,
* multiple users may submit experiments,
* execution must be decoupled from experiment development,
* experiments should run asynchronously without blocking the user's Python session.

---

## Credits

Developed by Iohannès Laurent with the help of Jérôme Esteve for the NS2,
Laboratoire LPS, Université Paris-Saclay (June 2026).
