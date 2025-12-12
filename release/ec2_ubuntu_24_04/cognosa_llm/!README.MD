### Cognosa LLM EC2 instance instructions

Using EC2 instance settings:
Ubuntu 24.04
type: g6e.2xlarge
gp3 storage: 300 GB

#### Installation script:

cognosa_llm.sh

#### To change keep alive or other settings:

Edit file:

```
sudo nano /etc/systemd/system/ollama.service
```

Add/edit environment variables into [Service] section, e.g.:

```
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_KEEP_ALIVE=10m"
```

And restart service:

```
sudo systemctl restart ollama
```

#### To check GPU usage:

```
nvidia-smi
```

Example output (using llama3.1:70b-instruct-q4_0):

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 590.44.01 Driver Version: 590.44.01 CUDA Version: 13.1 |
+-----------------------------------------+------------------------+----------------------+
| GPU Name Persistence-M | Bus-Id Disp.A | Volatile Uncorr. ECC |
| Fan Temp Perf Pwr:Usage/Cap | Memory-Usage | GPU-Util Compute M. |
| | | MIG M. |
|=========================================+========================+======================|
| 0 NVIDIA L40S On | 00000000:30:00.0 Off | 0 |
| N/A 44C P0 287W / 350W | 40193MiB / 46068MiB | 98% Default |
| | | N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes: |
| GPU GI CI PID Type Process name GPU Memory |
| ID ID Usage |
|=========================================================================================|
| 0 N/A N/A 1610 C /usr/local/bin/ollama 40184MiB |
+-----------------------------------------------------------------------------------------+
```
