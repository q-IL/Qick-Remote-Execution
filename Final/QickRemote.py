#client = QickClient()

#job1 = client.submit(prog1, cfg1)
#job2 = client.submit(prog2, cfg2)

#print(job1.status())

#result1 = job1.wait()

#finished = client.wait_all()

#print(finished)
import zmq
import cloudpickle
import uuid
import time

class QickJob:

    def __init__(self, client, nom):
        self.client = client 
        self.nom = nom
        self.recup=False #si déjà récupéré ou non

    def status(self):
        return self.info()["status"]

    def result(self):
        rep = self.info()
        status = rep["status"]
        if status == "done":
            return rep["result"]
        elif status == "failed":
            error_type = rep.get("error_type", "UnknownError")
            traceback_text = rep.get("result", "")
            raise RuntimeError(
                f"Le job '{self.nom}' a échoué.\n\n"
                f"Type d'erreur : {error_type}\n\n"
                f"Traceback complet :\n"
                f"{traceback_text}")
        elif status == "queued":
            raise RuntimeError(f"Le job '{self.nom}' n'a pas encore démarré.\n" f"{rep['result']}")
        elif status == "running":
            raise RuntimeError(f"Le job '{self.nom}' est actuellement en cours d'exécution.")
        elif status == "cancelled":
            raise RuntimeError(f"Le job '{self.nom}' a été annulé.")
        else: 
            raise RuntimeError(f"État inconnu pour le job '{self.nom}' : {status}")
        try:  self.recup=True
        except ValueError:
            pass
            
    def print_info(self):
        rep = self.info()
        print(f"Job : {self.nom}")
        print(f"Status : {rep['status']}")
        if rep["status"] == "done":
            print(f"Temps total : "
                f"{rep['temps total']} s")
            print(f"Temps mesure : "
                f"{rep['durée taitement']} s\n")
        elif rep["status"] == "queued":
            print(rep["result"]+"\n")
        elif rep["status"] == "failed":
            print(f"Type erreur : "
            f"{rep['error_type']}\n")
        return rep
        
        

    def cancel(self):
        request = {
            "type": "cancel",
            "client_id": self.client.client_id,
            "nom": self.nom}
        try: self.client.jobs.remove(self)
        except ValueError: pass
        return self.client._request(request)

    def info(self):
        request = {
            "type": "recuperer",
            "client_id":self.client.client_id,
            "nom": self.nom}
        rep = self.client._request(request)
        return rep

    def __repr__(self):
        try:
            s = self.status()
        except Exception:
            s = "unknown"

        return f"QickJob('{self.nom}', status='{s}')"

        return f"QickJob('{self.nom}', status='{status}')"

        
    def wait(self, refresh=1.0):
        try:  self.recup=True
        except ValueError:
            pass
        while True:
            rep = self.info()
            if rep["status"] == "done":
                print(f"{self.nom} terminé "
                    f"({rep['temps total']} s "
                    f"dont {rep['durée taitement']} s de mesure)")
                return rep["result"]
            elif rep["status"] == "failed":
                raise RuntimeError(
                    f"Le job '{self.nom}' a échoué.\n\n"
                    f"{rep['error_type']}\n\n"
                    f"{rep['result']}")
            elif rep["status"] == "cancelled":
                raise RuntimeError(
                    f"Le job '{self.nom}' a été annulé.")
            time.sleep(refresh)
        
#####################################################################################################################################################    

class QickClient:
    def __init__(self,
                 ip_server="localhost",
                 port=5555):

        self.client_id = str(uuid.uuid4()) #Pour les administrateurs, prendre le nom adminXXX pour pouvoir cancel les demandes des autres

        self.context = zmq.Context()

        self.socket = self.context.socket(zmq.REQ)

        self.socket.connect(
            f"tcp://{ip_server}:{port}"
        )

        self.jobs = []

    def _request(self, data):
        self.socket.send(cloudpickle.dumps(data))
        return cloudpickle.loads(self.socket.recv())
    
    def submit(self, prog, config, nom_programme=None,acquire_method="acquire_decimated",time_max=60 ): #méthodes codées : prog.acquire(...),prog.acquire_decimated(...),prog.acquire_round(...)
#max time n'est pas encore implémenté
        request = {
        "type": "Requete",
        "client_id": self.client_id,
        "prog": prog,
        "config":config,
        "nom": nom_programme,
        "acquire_method": acquire_method,
        "max_time":time_max}
        answer = self._request(request)
        
    # On suppose que le serveur renvoie :
    # {
    #     "message": "...",
    #     "nom": "job_123"
    # }
        nom_reel = answer["nom"]
        job = QickJob(client=self,nom=nom_reel)
        self.jobs.append(job)
        print(answer["message"])
        return job

        
    def check_all(self):
        print("État des jobs :\n")
        results = {}
        for job in self.jobs:
            try:  job.recup=True
            except ValueError:
                pass
            try:
                results[job.nom] = job.result()
                print(f"{job.nom} -> terminé")
            except RuntimeError:
                status = job.status()
                if status == "queued":
                    print(f"{job.nom} -> en attente")
                elif status == "running":
                    print(f"{job.nom} -> en cours")
                elif status == "failed":
                    print(f"{job.nom} -> FAILED")
                elif status == "cancelled":
                    print(f"{job.nom} -> annulé")
        if not self.jobs:
            print("aucun job")
        return results
    
    
    
    def wait_all(self, refresh=1.0):
        previous = {}
        res={}
        jobs_to_wait = [job for job in self.jobs if not job.recup]
        finished = set()
        if not jobs_to_wait:
            print("Aucun job à attendre.")
            return {}
        while len(finished) < len(jobs_to_wait):
            for job in jobs_to_wait:

                if job.nom in finished:
                    continue
                rep = job.info()
                if rep["status"] == "queued":
                    current = (rep["status"], rep["result"])
                else:
                    current = rep["status"]
                if previous.get(job.nom) != current:
                    previous[job.nom] = current
                    if rep["status"] == "queued":
                        print( f"{job.nom} -> {rep['result']}" )
                    elif rep["status"] == "running":
                        print( f"{job.nom} -> running" )
                    elif rep["status"] == "done":
                        res[job.nom]=rep["result"]
                        print( f"{job.nom} -> terminé " f"({rep['temps total']} s)" )
                    elif rep["status"] == "failed":
                        print( f"{job.nom} -> FAILED " f"({rep['error_type']})" )
                    elif rep["status"] == "cancelled":
                        print( f"{job.nom} -> cancelled")
                    if rep["status"] in ("done","failed","cancelled"):
                        try:  job.recup=True
                        except ValueError:
                            pass
                        finished.add(job.nom) 
            time.sleep(refresh)
        return res


    def get_config(self):
        request = {"type": "get_config"}
        cfg_dict = self._request(request)
        from qick.qick_asm import QickConfig
        return QickConfig(cfg_dict)
        

    def close(self):
        for job in self.jobs:
            try:
                job.cancel()
            except Exception:
                pass
        self.socket.close()
        self.context.term()