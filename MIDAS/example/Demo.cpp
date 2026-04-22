// -----------------------------------------------------------------------------
// Copyright 2020 Rui Liu (liurui39660) and Siddharth Bhatia (bhatiasiddharth)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// 	http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// -----------------------------------------------------------------------------

#include <cstdio>
#include <chrono>
#include <string>

#include "NormalCore.hpp"
#include "RelationalCore.hpp"
#include "FilteringCore.hpp"
#include "AUROC.hpp"

using namespace std;
using namespace std::chrono;

int main(int argc, char* argv[]) {
	// Parameter
	// --------------------------------------------------------------------------------

    // If no arguments are passed, use the default values ​​(DARPA)
	string pathMeta  = (argc > 1) ? argv[1] : SOLUTION_DIR"data/DARPA/darpa_shape.txt";
    string pathData  = (argc > 2) ? argv[2] : SOLUTION_DIR"data/DARPA/darpa_processed.csv";
    string pathLabel = (argc > 3) ? argv[3] : SOLUTION_DIR"data/DARPA/darpa_ground_truth.csv";
    string pathScore = (argc > 4) ? argv[4] : SOLUTION_DIR"temp/Score.txt";

    const unsigned seed = time(nullptr);
    printf("Seed = %u\n", seed);
    srand(seed);

// 2. Read Meta (using .c_str())
    // --------------------------------------------------------------------------------
    FILE* fileMeta = fopen(pathMeta.c_str(), "r");
    if (!fileMeta) {
        printf("ERROR: Could not open Meta in: %s\n", pathMeta.c_str());
        return -1;
    }
    int n;
    if (fscanf(fileMeta, "%d", &n) != 1) {
        printf("ERROR: Could not read logs number.\n");
        return -1;
    }
    fclose(fileMeta);

    // 3. Read Dataset (using .c_str())
    // --------------------------------------------------------------------------------
    FILE* fileData = fopen(pathData.c_str(), "r");
    if (!fileData) {
        printf("ERROR: Could not open Data in: %s\n", pathData.c_str());
        return -1;
    }
    const auto source = new int[n];
    const auto destination = new int[n];
    const auto timestamp = new int[n];
    for (int i = 0; i < n; i++)
        fscanf(fileData, "%d,%d,%d", &source[i], &destination[i], &timestamp[i]);
    fclose(fileData);
    printf("# Records = %d\t// Dataset loaded correctly\n", n);

    // 4. MIDAS algorithm
    // --------------------------------------------------------------------------------
    MIDAS::FilteringCore midas(2, 1024, 1e3f);
    const auto score = new float[n];
    const auto start_time = high_resolution_clock::now();
    for (int i = 0; i < n; i++)
        score[i] = midas(source[i], destination[i], timestamp[i]);
    
    auto end_time = high_resolution_clock::now();
    printf("Time = %lldms\t\t// Process ended\n", duration_cast<milliseconds>(end_time - start_time).count());

    // 5. Load tags to validation
    // --------------------------------------------------------------------------------
    const auto label = new float[n];
    FILE* fileLabel = fopen(pathLabel.c_str(), "r");
    if (fileLabel) {
        for (int i = 0; i < n; i++)
            fscanf(fileLabel, "%f", &label[i]);
        fclose(fileLabel);
        printf("ROC-AUC local = %.4f\n", AUROC(label, score, n));
    }
    delete[] label;

    // 6. Write independent results
    // --------------------------------------------------------------------------------
    FILE* fileScore = fopen(pathScore.c_str(), "w");
    if (fileScore == nullptr) {
        printf("ERROR: Could not create the score file in: %s\n", pathScore.c_str());
    } else {
        for (int i = 0; i < n; i++)
            fprintf(fileScore, "%f\n", score[i]);
        fclose(fileScore);
        printf("// Results exported successfully to: %s\n", pathScore.c_str());
    }

    // 7. Call evaluation Script
    // --------------------------------------------------------------------------------
    char command[2048];
    sprintf(command, "python3 %sutil/EvaluateScore.py %s %s", SOLUTION_DIR, pathLabel.c_str(), pathScore.c_str());
    printf("Executing internal evaluation: %s\n", command);
    system(command);

    delete[] source; delete[] destination; delete[] timestamp; delete[] score;
    return 0;
}

// To run:
// cmake --build . --target Demo
