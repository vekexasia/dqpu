# Copyright 2024 Davide Gessa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import random
import time

from .blockchain import IPFSGateway, NearBlockchain, from_near, to_near
from .cli import default_parser
from .sampler import SAMPLERS
from .utils import create_dqpu_dirs


def sampler_node():
    parser = default_parser()

    parser.add_argument("-d", "--max-deposit", help="maximum deposit", default=0.1)
    parser.add_argument(
        "-q", "--max-qubits", help="maximum number of simulable qubits", default=21
    )
    parser.add_argument(
        "-s", "--sampler", help="sampler to use", default="aersimulator"
    )

    args = parser.parse_args()  # noqa: F841
    base_dir = create_dqpu_dirs()

    nb = NearBlockchain(args.account, args.network)
    ipfs = IPFSGateway()  # noqa: F841

    # Start contract polling for new jobs
    running = True
    n_sampled = 0
    current_limit = 256

    print("Sampler node started.")

    while running:
        latest_jobs = nb.get_latest_jobs(limit=current_limit)

        # If there is a new job that needs execution, process it
        for j in latest_jobs:
            if j["status"] == "waiting":
                # Check if reward/10 is < of max_deposit
                if int(j["reward_amount"]) / 10 > to_near(float(args.max_deposit)):
                    print("reward / 10 is greater than max_deposit, skipping")
                    continue

                # Check for max qubits
                if int(j["qubits"]) > int(args.max_qubits):
                    print(
                        f"qubits {j['qubits']} is greater than max_qubits {args.max_qubits}"
                        + ", skipping"
                    )
                    continue

                print(
                    f"Processing job {j['id']} with {j['qubits']} qubits for {j['shots']} shots"
                )

                # Get the qasm file
                jf = ipfs.get(j["job_file"])

                # Load into a Sampler object (selected by params)
                # qc = Circuit.fromQasmCircuit(jf)
                sampler = SAMPLERS[args.sampler](jf)

                # Do the simulation
                counts = sampler.sample(j["shots"])

                # Upload the result
                result_f = f"{base_dir}/sampler/cache/{j['id']}_result.json"
                with open(result_f, "w") as cf:
                    cf.write(json.dumps(counts))
                jf_result = ipfs.upload(result_f)
                print("\t", "Result file uploaded", jf_result)

                # Submit the result with the deposit
                print(
                    "\t",
                    nb.submit_job_result(
                        j["id"],
                        jf_result,
                        deposit=from_near(j["reward_amount"]) / 10 + 0.00001,
                    ),
                )
                n_sampled += 1

        current_limit = 48
        print(f"Account balance is {nb.balance():0.5f} N, sampled jobs {n_sampled}")
        time.sleep(random.randint(0, 60))
