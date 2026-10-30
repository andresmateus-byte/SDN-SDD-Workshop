"""Reproducible local checks for NFR-10 and NFR-11; writes nfr-results.json."""
import json, os, socket, subprocess, sys, tempfile, time
from pathlib import Path
from statistics import median
import httpx

ROOT=Path(__file__).resolve().parents[1]

def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1",0)); return s.getsockname()[1]

def synthetic_topology():
    nodes=[f"N{i}" for i in range(50)]
    edges=set()
    for stride in (1,2,3):
        for i in range(50): edges.add(tuple(sorted((i,(i+stride)%50))))
    links=[]
    for j,(a,b) in enumerate(sorted(edges)):
        links.append({"node_a":nodes[a],"node_b":nodes[b],"delay_ms":1+(j%13),"bandwidth_mbps":10+(j%90),"loss_probability":(j%5)/100})
    return {"nodes":nodes,"links":links}

def start_app(module, port, env):
    command=[sys.executable,"-m","uvicorn",module,"--host","127.0.0.1","--port",str(port),"--log-level","warning"]
    return subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def wait_health(url, proc, seconds=12):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        if proc.poll() is not None: raise RuntimeError(f"Proceso terminó durante el arranque: {url}, exit={proc.returncode}")
        try:
            r=httpx.get(url+"/health",timeout=.4)
            if r.status_code==200:return
        except httpx.HTTPError: pass
        time.sleep(.1)
    raise TimeoutError(f"No inició a tiempo: {url}")

def stop(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)

def main():
    result={"environment":{"python":sys.version.split()[0],"platform":sys.platform},"nfr10":{},"nfr11":{}}
    controller=None; router=None
    with tempfile.TemporaryDirectory(prefix="sdn-nfr-") as td:
        tmp=Path(td); topology=tmp/"topology.json"; topology.write_text(json.dumps(synthetic_topology()),encoding="utf-8")
        log_path=tmp/"forwarding.jsonl"
        cp,rp=free_port(),free_port()
        env=os.environ.copy(); env["PYTHONPATH"]=str(ROOT); env["TOPOLOGY_FILE_PATH"]=str(topology); env["LOG_LEVEL"]="WARNING"
        base=f"http://127.0.0.1:{cp}"
        try:
            controller=start_app("controller.app:app",cp,env); wait_health(base,controller)
            with httpx.Client(timeout=5) as client:
                # Warm-up requests do not count toward the 100 measured samples per metric.
                for metric in ("delay","bandwidth","loss"):
                    for _ in range(3):
                        r=client.get(base+"/route",params={"src":"N0","dst":"N25","metric":metric})
                        r.raise_for_status()
                    samples=[]
                    for _ in range(100):
                        start=time.perf_counter()
                        r=client.get(base+"/route",params={"src":"N0","dst":"N25","metric":metric})
                        elapsed=(time.perf_counter()-start)*1000
                        if r.status_code!=200: raise AssertionError(f"GET /route {metric}: {r.status_code} {r.text}")
                        samples.append(elapsed)
                    ordered=sorted(samples); p95=ordered[94]
                    result["nfr10"][metric]={"samples_ms":[round(x,3) for x in samples],"p95_nearest_rank_ms":round(p95,3),"threshold_ms":200,"meets_threshold":p95<=200,"min_ms":round(min(samples),3),"median_ms":round(median(samples),3),"max_ms":round(max(samples),3)}
            # NFR-11: keep Router alive while stopping Controller; then restart Controller.
            r_env=os.environ.copy(); r_env["PYTHONPATH"]=str(ROOT); r_env["CONTROLLER_BASE_URL"]=base; r_env["CONTROLLER_TIMEOUT_SECONDS"]="2"; r_env["FORWARDING_LOG_PATH"]=str(log_path); r_env["LOG_LEVEL"]="WARNING"
            router=start_app("router.app:app",rp,r_env); router_url=f"http://127.0.0.1:{rp}"; wait_health(router_url,router)
            stop(controller); controller=None
            attempts=[]
            with httpx.Client(timeout=4) as client:
                for i in range(10):
                    start=time.perf_counter(); response=client.post(router_url+"/packets",json={"packet_id":f"outage-{i:02d}","src":"A","dst":"D"}); elapsed=(time.perf_counter()-start)*1000
                    attempts.append({"http_status":response.status_code,"error":response.json().get("error"),"elapsed_ms":round(elapsed,3)})
                    if response.status_code!=503 or response.json().get("error")!="CONTROLLER_UNAVAILABLE" or elapsed>3000: raise AssertionError(f"NFR-11 failed: {attempts[-1]}")
                health_after=client.get(router_url+"/health")
                if health_after.status_code!=200: raise AssertionError("Router health failed during Controller outage")
            controller=start_app("controller.app:app",cp,env); wait_health(base,controller)
            with httpx.Client(timeout=5) as client:
                recovered=client.post(router_url+"/packets",json={"packet_id":"after-recovery","src":"N0","dst":"N25"})
                if recovered.status_code!=200: raise AssertionError(f"Router did not recover: {recovered.status_code} {recovered.text}")
            result["nfr11"]={"attempts":attempts,"router_health_during_outage":health_after.status_code,"recovery_http_status":recovered.status_code,"all_within_3s":all(x["elapsed_ms"]<=3000 for x in attempts)}
        finally:
            stop(router); stop(controller)
    out=ROOT/"nfr-results.json"; out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"nfr10":{k:{kk:vv for kk,vv in v.items() if kk!="samples_ms"} for k,v in result["nfr10"].items()},"nfr11":result["nfr11"],"report":str(out)},indent=2,ensure_ascii=False))
    if not all(v["meets_threshold"] for v in result["nfr10"].values()): sys.exit(1)

if __name__=="__main__": main()
