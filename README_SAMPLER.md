# Sampler Node

Prerequisites:
- nodejs >= 0.20
- python >= 3.9


Install IPFS:

- https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions

Run the IPFS daemon:

```bash
ipfs daemon
```

Install near-cli:

```bash
npm i -g near-cli
```

Create an account:

```bash
near create-account [NAME]_dqpu_sampler.testnet --useFaucet
```

Install the sampler software:

```bash
git clone https://github.com/dakk/dqpu
cd dqpu
pip install -r requirements.txt
python setup.py install
```

Run the sampler:

```bash
dqpu-sampler -a NAME_dqpu_sampler.testnet --max-deposit 0.1 --sampler aersimulator --max-qubits 21
```

More qubits you support, more ram is needed but greater is the reward.


## Update the software:

```bash
cd dqpu
git pull
python setup.py install
```
