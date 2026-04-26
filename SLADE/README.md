# [SLADE: Detecting Dynamic Anomalies in Edge Streams without Labels via Self-Supervised Learning]
This is the source code for "SLADE: Detecting Dynamic Anomalies in Edge Streams without Labels via Self-Supervised Learning".

## Requirements

* Dependency

```{bash}
python==3.9
pandas==1.5.2
numpy==1.23.5
torch==1.13.1
torch-scatter=2.1.0
scikit_learn==1.1.3
tqdm==4.65.0
```

### Dataset and Preprocessing


#### Download the dataset

We already preprocess bitcoinalpha, bitcionotc, Sytentic-Hijack, Sytentic-New datsets and save csv files in directory `data/`.

You can download the Wikipedia and Reddit datasets from here (http://snap.stanford.edu/jodie/) and store their csv files in directory `data/`.

We need the data format like `source_id, destination_id, timestamp, labels, features (optional))`.


#### Preprocess the dataset (from [TGN](https://github.com/twitter-research/tgn))

```{bash}
python utils/preprocess_data.py --data wikipedia --bipartite
python utils/preprocess_data.py --data reddit --bipartite
python utils/preprocess_data.py --data bitcoinalpha
python utils/preprocess_data.py --data bitcoinotc

```
After preprocessing, output file is `ml_dataset_name.csv` and contains data format like `source id, destination id, timestamp, label, edge idx`.

During this process, `.npy` files containing node or edge feature information have been generated for other baseline models, which are not utilized in the SLADE model. (we need only `ml_dataset_name.csv` files)

Data preprocessing has been conducted for all datasets (except reddit dataset) and saved in directory `data/`.


### Run the model


Dynamic Anomaly Detection for each dataset (SLADE)

```{bash}
python SLADE_main.py -d wikipedia
python SLADE_main.py -d reddit
python SLADE_main.py -d bitcoinalpha
python SLADE_main.py -d bitcoinotc
```

Dynamic Anomaly Detection for each dataset (SLADE-HP)

```{bash}
python SLADE_main.py -d wikipedia --bs 300 --srf 10 --drf 10
python SLADE_main.py -d reddit --bs 100 --srf 0.1 --drf 1
python SLADE_main.py -d bitcoinalpha --bs 300 --srf 1 --drf 10
python SLADE_main.py -d bitcoinotc --bs 300 --srf 10 --drf 1
```

Training Ratio Test

```{bash}
python SLADE_main.py -d wikipedia --training_ratio 0.7
python SLADE_main.py -d reddit --training_ratio 0.7
```

Detection Time Test (on the Wikipedia dataset)

```{bash}
python SLADE_main.py --test_inference_time
```

### Ablation Study


```{bash}
# Memory Drift Loss + Drift Score
python SLADE_main.py --only_drift_loss_score

# Memory Reconstruction Loss + Reconstruction Score
python SLADE_main.py --only_recovery_loss_score

# Memory Drift Loss + Memory Reconstruction Loss + Drift Score
python SLADE_main.py --only_drift_score

# Memory Drift Loss + Memory Reconstruction Loss + Reconstruction Score
python SLADE_main.py --only_rec_score
```

### Type Analysis

```{bash}
# Sythetic-Hijack (type 1 & 3)
python SLADE_main.py -d synthetic_hijack

# Sythetic-New (type 2 & 3)
python SLADE_main.py -d synthetic_new
```


### Argument Options

```{txt}
optional arguments:
  -d DATA, --data DATA         Data sources to use (wikipedia / reddit / Bitcoinalpha / BitcoinOTC)
  --bs BS                      Batch size
  --n_degree N_DEGREE          Maximum Number of most recent neighbors
  --n_head N_HEAD              Number of heads used in the attention layer
  --n_epoch N_EPOCH            Number of epochs
  --lr LR                      Learning rate
  --n_runs                     Number of runs (compute mean and std of results)
  --drop_out DROP_OUT          Dropout probability
  --gpu GPU                    Idx for the gpu to use
  --message_dim MESSAGE_DIM    Dimension of the message
  --memory_dim MEMORY_DIM      Dimension of the memory
  --agg_type                   Type of the neighbors aggregation module
  --negative_memory_type       Type of the negative samples
  --message_function           Type of the message function
  --memory_updater             Type of the memory updater
  --training_ratio             Training ratio of the Dataset
  --lr_decay                   Learning Rate Decay (Exponential)
  --weight_decay               Weight Decay of the Optimizer
  --srf                        Weight of the source node in memory reconstruction loss
  --drf                        Weight of the destination node in memory reconstruction loss

  --only_drift_loss_score      Whether to use only Memory Drift Loss and Drift Score
  --only_recovery_loss_score   Whether to use only Memory Reconstruction Loss and Reconstruction Score
  --only_drift_score           Whether to use all losses and only Drift Score
  --only_rec_score             Whether to use all losses and only Reconstruction Score
  --test_inference_time        Whether to measure detection time (with an evolving CTDG)  
```
## Config ./run_slade depending on the user

Adjusting hyperparameters based on log size is essential to balance **model capacity** with **data density**, ensuring scientific validity. Small datasets are highly susceptible to **overfitting**, where the model memorizes specific noise instead of learning generalizable patterns; reducing epochs and complexity prevents this "memorization" trap. Conversely, large datasets require more stable learning via smaller learning rates and larger batch sizes to capture complex, long-term temporal dependencies without overshooting the optimal solution. This approach ensures that your comparison with MIDAS is rigorous, as it optimizes SLADE to reach its maximum potential for each specific user profile rather than applying a "one-size-fits-all" configuration that would unfairly disadvantage the model in extreme cases.

| Log Category | Row Count ($N$) | Epochs | Batch Size | Learning Rate | Memory Dim | Neighbor Degree | Strategy Goal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Small** | $N < 5,000$ | $5 - 10$ | $32$ | $1 \times 10^{-3}$ | $128$ | $5 - 10$ | Prevent Overfitting |
| **Medium** | $5,000 \le N < 50,000$ | $20 - 30$ | $128$ | $5 \times 10^{-4}$ | $256$ | $20$ | Balance Convergence |
| **Large** | $N \ge 50,000$ | $50 - 100$ | $512$ | $1 \times 10^{-5}$ | $512$ | $30$ | Stabilize Learning |