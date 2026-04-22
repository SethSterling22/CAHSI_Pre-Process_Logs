# ------------------------------------------------------------------------------
# Copyright 2020 Rui Liu (liurui39660) and Siddharth Bhatia (bhatiasiddharth)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from pathlib import Path
import sys

from pandas import read_csv
from sklearn.metrics import roc_auc_score

root = (Path(__file__) / '../..').resolve()

python_exe = "python" if sys.version_info.major < 3 else "python3"

if len(sys.argv) < 3:
    print(f'Print ROC-AUC to stdout and MIDAS/temp/AUC[<indexRun>].txt')
    print(f'Usage: {python_exe} EvaluateScore.py <pathGroundTruth> <pathScore> [<indexRun>]')
else:
	y = read_csv(sys.argv[1], header=None)
	z = read_csv(sys.argv[2], header=None)
	indexRun = sys.argv[3] if len(sys.argv) >= 4 else ''
	auc = roc_auc_score(y, z)
	print(f"ROC-AUC{indexRun} = {auc:.4f}")
	if indexRun:
		with open(root / f"temp/AUC{indexRun}.txt", 'w') as file:
			file.write(str(auc))
